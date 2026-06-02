import json
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from desktop_bridge import extract_last_user_text, start_desktop_bridge_server
from agent_backend import (
    NanobotAgentConfig,
    NanobotAgentRequest,
    reply_with_nanobot_agent,
)


class DesktopBridgeTests(unittest.TestCase):
    def test_extract_last_user_text_prefers_latest_user_message(self):
        payload = [
            {"role": "system", "content": "ignore"},
            {"role": "user", "content": "第一句"},
            {"role": "assistant", "content": "回复"},
            {"role": "user", "content": [{"type": "text", "text": "最后一句"}]},
        ]

        self.assertEqual(extract_last_user_text(payload), "最后一句")

    def test_openai_compatible_routes_return_models_and_reply(self):
        server = start_desktop_bridge_server(
            host="127.0.0.1",
            port=0,
            default_user_id=3554978979,
            model_name="deepseek-chat",
            reply_callback=lambda user_id, text: f"{user_id}:{text}",
        )

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            time.sleep(0.1)
            port = server.server_address[1]

            models_response = request.urlopen(f"http://127.0.0.1:{port}/v1/models")
            models_json = json.loads(models_response.read().decode("utf-8"))
            self.assertEqual(models_json["data"][0]["id"], "deepseek-chat")

            body = json.dumps(
                {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "你好"}],
                }
            ).encode("utf-8")
            chat_request = request.Request(
                f"http://127.0.0.1:{port}/v1/chat/completions",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            chat_response = request.urlopen(chat_request)
            chat_json = json.loads(chat_response.read().decode("utf-8"))

            self.assertEqual(
                chat_json["choices"][0]["message"]["content"],
                "3554978979:你好",
            )

            state_response = request.urlopen(
                f"http://127.0.0.1:{port}/v1/xiaomiao/state?user_id=3554978979"
            )
            state_json = json.loads(state_response.read().decode("utf-8"))
            self.assertEqual(state_json["reply_text"], "3554978979:你好")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def test_bridge_supports_cors_preflight_and_headers(self):
        server = start_desktop_bridge_server(
            host="127.0.0.1",
            port=0,
            default_user_id=3554978979,
            model_name="deepseek-chat",
            reply_callback=lambda user_id, text: text,
        )

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            time.sleep(0.1)
            port = server.server_address[1]

            preflight = request.Request(
                f"http://127.0.0.1:{port}/v1/xiaomiao/state?user_id=3554978979",
                method="OPTIONS",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Content-Type,X-XiaoMiao-User-Id",
                    "Access-Control-Request-Private-Network": "true",
                },
            )
            response = request.urlopen(preflight)

            self.assertEqual(response.status, 204)
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")
            self.assertIn(
                "GET", response.headers.get("Access-Control-Allow-Methods", "")
            )
            self.assertIn(
                "X-XiaoMiao-User-Id",
                response.headers.get("Access-Control-Allow-Headers", ""),
            )
            self.assertEqual(
                response.headers.get("Access-Control-Allow-Private-Network"), "true"
            )

            models_response = request.urlopen(f"http://127.0.0.1:{port}/v1/models")
            self.assertEqual(
                models_response.headers.get("Access-Control-Allow-Origin"), "*"
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def test_status_route_returns_bridge_runtime_state(self):
        server = start_desktop_bridge_server(
            host="127.0.0.1",
            port=0,
            default_user_id=3554978979,
            model_name="deepseek-chat",
            reply_callback=lambda user_id, text: text,
        )

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            time.sleep(0.1)
            port = server.server_address[1]

            status_response = request.urlopen(
                f"http://127.0.0.1:{port}/v1/xiaomiao/status"
            )
            status_json = json.loads(status_response.read().decode("utf-8"))

            self.assertEqual(
                status_json,
                {
                    "ok": True,
                    "service": "xiaomiao-desktop-bridge",
                    "model": "deepseek-chat",
                    "default_user_id": 3554978979,
                },
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

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
                NanobotAgentRequest(
                    user_id=user_id,
                    channel="web",
                    chat_id="stage-web",
                    text=text,
                ),
            )

        server = start_desktop_bridge_server(
            host="127.0.0.1",
            port=0,
            default_user_id=3554978979,
            model_name="deepseek-chat",
            reply_callback=reply_with_agent,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            time.sleep(0.1)
            port = server.server_address[1]
            body = json.dumps(
                {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "你好"}],
                }
            ).encode("utf-8")
            chat_request = request.Request(
                f"http://127.0.0.1:{port}/v1/chat/completions",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            chat_response = request.urlopen(chat_request)
            chat_json = json.loads(chat_response.read().decode("utf-8"))

            self.assertEqual(
                chat_json["choices"][0]["message"]["content"],
                "nanobot:你好",
            )
            self.assertEqual(
                _AgentHandler.last_body["session_id"],
                "xiaomiao-unified",
            )
        finally:
            server.shutdown()
            server.server_close()
            agent_server.stop()
            thread.join(timeout=1)

    def test_bridge_callback_error_returns_visible_502(self):
        server = start_desktop_bridge_server(
            host="127.0.0.1",
            port=0,
            default_user_id=3554978979,
            model_name="deepseek-chat",
            reply_callback=lambda _user_id, _text: (_ for _ in ()).throw(RuntimeError("agent down")),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            time.sleep(0.1)
            port = server.server_address[1]
            body = json.dumps(
                {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "你好"}],
                }
            ).encode("utf-8")
            chat_request = request.Request(
                f"http://127.0.0.1:{port}/v1/chat/completions",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with self.assertRaises(error.HTTPError) as raised:
                request.urlopen(chat_request)
            self.assertEqual(raised.exception.code, 502)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)


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


if __name__ == "__main__":
    unittest.main()
