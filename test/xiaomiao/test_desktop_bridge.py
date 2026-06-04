import json
import os
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from desktop_bridge import (
    extract_last_user_text,
    publish_bridge_exchange,
    reset_bridge_state,
    start_desktop_bridge_server,
)
from agent_backend import (
    NanobotAgentConfig,
    NanobotAgentRequest,
    reply_with_nanobot_agent,
)

DEFAULT_USER_ID = 3554978979
MODEL_NAME = "deepseek-chat"


class DesktopBridgeTests(unittest.TestCase):
    def setUp(self):
        self.event_store_tmp = tempfile.TemporaryDirectory()
        os.environ["XIAOMIAO_BRIDGE_EVENT_STORE"] = str(
            Path(self.event_store_tmp.name) / "bridge_events.jsonl"
        )
        reset_bridge_state()

    def tearDown(self):
        reset_bridge_state()
        os.environ.pop("XIAOMIAO_BRIDGE_EVENT_STORE", None)
        os.environ.pop("XIAOMIAO_UNIFIED_CONFIG", None)
        self.event_store_tmp.cleanup()

    def test_extract_last_user_text_prefers_latest_user_message(self):
        payload = [
            {"role": "system", "content": "ignore"},
            {"role": "user", "content": "第一句"},
            {"role": "assistant", "content": "回复"},
            {"role": "user", "content": [{"type": "text", "text": "最后一句"}]},
        ]

        self.assertEqual(extract_last_user_text(payload), "最后一句")

    def test_openai_compatible_routes_return_models_reply_state_and_events(self):
        with _bridge_server(lambda user_id, text: f"{user_id}:{text}") as port:
            models_json = _json_get(f"http://127.0.0.1:{port}/v1/models")
            self.assertEqual(models_json["data"][0]["id"], MODEL_NAME)

            chat_json = _json_post(
                f"http://127.0.0.1:{port}/v1/chat/completions",
                {"model": MODEL_NAME, "messages": [{"role": "user", "content": "你好"}]},
            )
            self.assertEqual(chat_json["choices"][0]["message"]["content"], "3554978979:你好")

            state_json = _json_get(
                f"http://127.0.0.1:{port}/v1/xiaomiao/state?user_id={DEFAULT_USER_ID}"
            )
            self.assertEqual(state_json["reply_text"], "3554978979:你好")

            events_json = _json_get(
                f"http://127.0.0.1:{port}/v1/xiaomiao/events?user_id={DEFAULT_USER_ID}"
            )
            self.assertEqual([item["role"] for item in events_json["events"]], ["user", "assistant"])
            self.assertEqual(events_json["events"][0]["source"], "web")
            self.assertEqual(events_json["events"][0]["content"], "你好")
            self.assertEqual(events_json["events"][1]["content"], "3554978979:你好")

    def test_qq_exchange_can_be_read_from_bridge_events(self):
        publish_bridge_exchange(
            source="qq-group",
            channel="qq-group",
            chat_id="10001",
            user_id=42,
            user_text="群里问一句",
            assistant_text="群里答一句",
        )

        with _bridge_server() as port:
            body = _json_get(f"http://127.0.0.1:{port}/v1/xiaomiao/events?user_id=42")

        self.assertEqual(body["last_id"], 2)
        self.assertEqual([item["content"] for item in body["events"]], ["群里问一句", "群里答一句"])
        self.assertEqual(body["events"][0]["chat_id"], "10001")

    def test_events_after_cursor_returns_only_newer_events(self):
        publish_bridge_exchange(
            source="qq-private",
            channel="qq-private",
            chat_id="42",
            user_id=42,
            user_text="旧问题",
            assistant_text="旧回答",
        )
        publish_bridge_exchange(
            source="qq-private",
            channel="qq-private",
            chat_id="42",
            user_id=42,
            user_text="新问题",
            assistant_text="新回答",
        )

        with _bridge_server() as port:
            body = _json_get(
                f"http://127.0.0.1:{port}/v1/xiaomiao/events?user_id=42&after=2"
            )

        self.assertEqual(body["last_id"], 4)
        self.assertEqual([item["content"] for item in body["events"]], ["新问题", "新回答"])

    def test_bridge_supports_cors_preflight_and_headers(self):
        with _bridge_server() as port:
            preflight = request.Request(
                f"http://127.0.0.1:{port}/v1/xiaomiao/state?user_id={DEFAULT_USER_ID}",
                method="OPTIONS",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Content-Type,X-XiaoMiao-User-Id",
                    "Access-Control-Request-Private-Network": "true",
                },
            )
            response = request.urlopen(preflight)
            models_response = request.urlopen(f"http://127.0.0.1:{port}/v1/models")

        self.assertEqual(response.status, 204)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("GET", response.headers.get("Access-Control-Allow-Methods", ""))
        self.assertIn("X-XiaoMiao-User-Id", response.headers.get("Access-Control-Allow-Headers", ""))
        self.assertEqual(response.headers.get("Access-Control-Allow-Private-Network"), "true")
        self.assertEqual(models_response.headers.get("Access-Control-Allow-Origin"), "*")

    def test_status_route_returns_bridge_runtime_state(self):
        with _bridge_server() as port:
            status_json = _json_get(f"http://127.0.0.1:{port}/v1/xiaomiao/status")

        self.assertEqual(
            status_json,
            {
                "ok": True,
                "service": "xiaomiao-desktop-bridge",
                "model": MODEL_NAME,
                "default_user_id": DEFAULT_USER_ID,
            },
        )

    def test_config_route_reports_missing_root_config(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.environ["XIAOMIAO_UNIFIED_CONFIG"] = str(Path(tmp_dir) / "config.json")
            with _bridge_server() as port:
                body = _json_get(f"http://127.0.0.1:{port}/v1/xiaomiao/config")

        self.assertFalse(body["configured"])
        self.assertFalse(body["hasApiKey"])
        self.assertEqual(body["provider"], "")
        self.assertNotIn("apiKey", body)

    def test_config_route_reads_custom_root_config_without_exposing_secret(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "nanobot": {
                            "provider": "custom",
                            "model": "deepseek-v4-flash",
                            "providers": {
                                "custom": {
                                    "apiKey": "secret-key",
                                    "baseUrl": "https://relay.example.com/v1",
                                }
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            os.environ["XIAOMIAO_UNIFIED_CONFIG"] = str(config_path)
            with _bridge_server() as port:
                body = _json_get(f"http://127.0.0.1:{port}/v1/xiaomiao/config")

        self.assertTrue(body["configured"])
        self.assertTrue(body["hasApiKey"])
        self.assertEqual(body["provider"], "custom")
        self.assertEqual(body["model"], "deepseek-v4-flash")
        self.assertEqual(body["baseUrl"], "https://relay.example.com/v1")
        self.assertNotIn("apiKey", body)

    def test_config_route_writes_custom_root_config(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            os.environ["XIAOMIAO_UNIFIED_CONFIG"] = str(config_path)
            with _bridge_server() as port:
                body = _json_post(
                    f"http://127.0.0.1:{port}/v1/xiaomiao/config",
                    {
                        "apiKey": "secret-key",
                        "baseUrl": "https://relay.example.com/v1",
                        "model": "deepseek-v4-flash",
                    },
                )
            saved = json.loads(config_path.read_text(encoding="utf-8"))

        self.assertTrue(body["configured"])
        self.assertEqual(saved["nanobot"]["provider"], "custom")
        self.assertEqual(saved["nanobot"]["model"], "deepseek-v4-flash")
        self.assertEqual(saved["nanobot"]["providers"]["custom"]["apiKey"], "secret-key")
        self.assertEqual(saved["nanobot"]["providers"]["custom"]["baseUrl"], "https://relay.example.com/v1")

    def test_config_route_rejects_incomplete_payload(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.environ["XIAOMIAO_UNIFIED_CONFIG"] = str(Path(tmp_dir) / "config.json")
            with _bridge_server() as port:
                with self.assertRaises(error.HTTPError) as raised:
                    _json_post(
                        f"http://127.0.0.1:{port}/v1/xiaomiao/config",
                        {"apiKey": "secret-key", "baseUrl": "https://relay.example.com/v1"},
                    )

        self.assertEqual(raised.exception.code, 400)

    def test_bridge_callback_can_use_nanobot_agent_backend(self):
        agent_server = _LocalAgentServer()
        agent_server.start()

        def reply_with_agent(user_id, text):
            return reply_with_nanobot_agent(
                NanobotAgentConfig(
                    enabled=True,
                    base_url=agent_server.url,
                    model=None,
                    session_id="xiaomiao-unified",
                    timeout_seconds=1.0,
                ),
                NanobotAgentRequest(user_id=user_id, channel="web", chat_id="stage-web", text=text),
            )

        try:
            with _bridge_server(reply_with_agent) as port:
                chat_json = _json_post(
                    f"http://127.0.0.1:{port}/v1/chat/completions",
                    {"model": MODEL_NAME, "messages": [{"role": "user", "content": "你好"}]},
                )

            self.assertEqual(chat_json["choices"][0]["message"]["content"], "nanobot:你好")
            self.assertEqual(_AgentHandler.last_body["session_id"], "xiaomiao-unified")
        finally:
            agent_server.stop()

    def test_bridge_callback_error_returns_visible_502(self):
        def raise_error(_user_id, _text):
            raise RuntimeError("agent down")

        with _bridge_server(raise_error) as port:
            with self.assertRaises(error.HTTPError) as raised:
                _json_post(
                    f"http://127.0.0.1:{port}/v1/chat/completions",
                    {"model": MODEL_NAME, "messages": [{"role": "user", "content": "你好"}]},
                )

        self.assertEqual(raised.exception.code, 502)


class _BridgeServer:
    def __init__(self, reply_callback=None):
        callback = reply_callback or (lambda _user_id, text: text)
        self.server = start_desktop_bridge_server(
            host="127.0.0.1",
            port=0,
            default_user_id=DEFAULT_USER_ID,
            model_name=MODEL_NAME,
            reply_callback=callback,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        time.sleep(0.1)
        return self.server.server_address[1]

    def __exit__(self, *_args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1)


class _LocalAgentServer:
    def __init__(self):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), _AgentHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}/v1/chat/completions"

    def start(self):
        self.thread.start()
        time.sleep(0.1)

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=1)


class _AgentHandler(BaseHTTPRequestHandler):
    last_body = {}

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        _AgentHandler.last_body = json.loads(body.decode("utf-8"))
        text = _AgentHandler.last_body["messages"][0]["content"]
        payload = {"choices": [{"message": {"content": f"nanobot:{text}"}}]}
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        return


def _bridge_server(reply_callback=None):
    return _BridgeServer(reply_callback)


def _json_get(url: str) -> dict:
    response = request.urlopen(url)
    return json.loads(response.read().decode("utf-8"))


def _json_post(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    response = request.urlopen(http_request)
    return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
