import json
import os
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from agent_backend import (  # noqa: E402
    DEFAULT_XIAOMIAO_AGENT_BASE_URL,
    DEFAULT_XIAOMIAO_AGENT_SESSION_ID,
    XiaomiaoAgentConfig,
    XiaomiaoAgentRequest,
    load_xiaomiao_agent_config,
    publish_xiaomiao_agent_event,
    reply_with_xiaomiao_agent,
    request_xiaomiao_agent,
)


class AgentBackendTests(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("XIAOMIAO_UNIFIED_CONFIG", None)

    def test_load_config_uses_enabled_defaults(self):
        config = load_xiaomiao_agent_config({})

        self.assertTrue(config.enabled)
        self.assertEqual(config.base_url, DEFAULT_XIAOMIAO_AGENT_BASE_URL)
        self.assertIsNone(config.model)
        self.assertEqual(config.session_id, DEFAULT_XIAOMIAO_AGENT_SESSION_ID)

    def test_root_config_overrides_xiaomiao_agent_section(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "xiaomiao_agent": {
                            "base_url": "http://127.0.0.1:9999/v1/chat/completions",
                            "model": "root-model",
                            "session_id": "root-session",
                            "timeout_seconds": 12,
                        }
                    }
                ),
                encoding="utf-8",
            )
            os.environ["XIAOMIAO_UNIFIED_CONFIG"] = str(config_path)

            config = load_xiaomiao_agent_config(
                {"xiaomiao_agent": {"model": "local-model"}}
            )

        self.assertEqual(config.base_url, "http://127.0.0.1:9999/v1/chat/completions")
        self.assertEqual(config.model, "root-model")
        self.assertEqual(config.session_id, "root-session")
        self.assertEqual(config.timeout_seconds, 12)

    def test_empty_root_config_values_do_not_override_local_values(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            config_path.write_text(
                json.dumps({"xiaomiao_agent": {"model": "", "session_id": None}}),
                encoding="utf-8",
            )
            os.environ["XIAOMIAO_UNIFIED_CONFIG"] = str(config_path)

            config = load_xiaomiao_agent_config(
                {"xiaomiao_agent": {"model": "local-model", "session_id": "local-session"}}
            )

        self.assertEqual(config.model, "local-model")
        self.assertEqual(config.session_id, "local-session")

    def test_disabled_config_raises_without_request(self):
        config = XiaomiaoAgentConfig(
            enabled=False,
            base_url="http://127.0.0.1:1/v1/chat/completions",
            model=None,
            session_id="xiaomiao-unified",
            timeout_seconds=0.01,
        )

        with self.assertRaisesRegex(RuntimeError, "disabled"):
            reply_with_xiaomiao_agent(config, _payload("hello"))

    def test_successful_agent_reply_uses_unified_session(self):
        with _agent_server(_SuccessHandler) as base_url:
            reply = reply_with_xiaomiao_agent(_config(base_url), _payload("你好"))

        self.assertEqual(reply, "agent reply")
        self.assertEqual(_SuccessHandler.last_body["session_id"], "xiaomiao-unified")
        self.assertEqual(_SuccessHandler.last_body["channel"], "web")
        self.assertEqual(_SuccessHandler.last_body["chat_id"], "stage-web")
        self.assertEqual(_SuccessHandler.last_body["user_id"], "3554978979")
        self.assertEqual(_SuccessHandler.last_body["messages"][0]["content"], "你好")

    def test_agent_reply_sends_media_as_image_content_parts(self):
        with _agent_server(_SuccessHandler) as base_url:
            reply = reply_with_xiaomiao_agent(
                _config(base_url),
                _payload("看图", media=("data:image/png;base64,AAA=",)),
            )

        self.assertEqual(reply, "agent reply")
        self.assertEqual(
            _SuccessHandler.last_body["messages"][0]["content"],
            [
                {"type": "text", "text": "看图"},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,AAA="}},
            ],
        )

    def test_agent_reply_sends_tool_policy_and_confirmation_id(self):
        with _agent_server(_SuccessHandler) as base_url:
            reply = reply_with_xiaomiao_agent(
                _config(base_url),
                _payload(
                    "执行 dir",
                    tool_policy="trusted_confirmed",
                    confirmation_id="ABC123",
                ),
            )

        self.assertEqual(reply, "agent reply")
        self.assertEqual(_SuccessHandler.last_body["tool_policy"], "trusted_confirmed")
        self.assertEqual(_SuccessHandler.last_body["confirmation_id"], "ABC123")

    def test_agent_response_keeps_tool_events(self):
        with _agent_server(_ToolEventsHandler) as base_url:
            response = request_xiaomiao_agent(_config(base_url), _payload("stage action"))

        self.assertEqual(response.assistant_text, "agent reply")
        self.assertEqual(
            response.tool_events,
            (
                {
                    "event_type": "stage_action",
                    "tool_name": "xiaomiaobot_action",
                    "risk_level": "high",
                    "confirmation_id": "ABC123",
                    "result_summary": "stage:say",
                },
            ),
        )

    def test_structured_event_is_published_to_agent_api(self):
        with _agent_server(_SuccessHandler) as base_url:
            publish_xiaomiao_agent_event(
                _config(base_url),
                {
                    "source": "qq-group",
                    "channel": "qq-group",
                    "chat_id": "10001",
                    "user_id": 3554978979,
                    "role": "assistant",
                    "content": "permission denied",
                    "event_type": "tool_error",
                },
            )

        self.assertEqual(_SuccessHandler.last_path, "/v1/xiaomiao/events")
        self.assertEqual(_SuccessHandler.last_body["event_type"], "tool_error")

    def test_http_error_is_visible(self):
        with _agent_server(_ErrorHandler) as base_url:
            with self.assertRaisesRegex(RuntimeError, "HTTP 502"):
                reply_with_xiaomiao_agent(_config(base_url), _payload("hello"))

    def test_empty_agent_reply_is_visible(self):
        with _agent_server(_EmptyReplyHandler) as base_url:
            with self.assertRaisesRegex(RuntimeError, "empty reply"):
                reply_with_xiaomiao_agent(_config(base_url), _payload("hello"))

    def test_timeout_is_visible(self):
        with _agent_server(_SlowHandler) as base_url:
            config = _config(base_url, timeout_seconds=0.01)
            with self.assertRaisesRegex(RuntimeError, "request failed"):
                reply_with_xiaomiao_agent(config, _payload("hello"))

    def test_zero_timeout_waits_for_slow_agent_reply(self):
        with _agent_server(_SlowHandler) as base_url:
            config = _config(base_url, timeout_seconds=0)
            reply = reply_with_xiaomiao_agent(config, _payload("hello"))

        self.assertEqual(reply, "late")


class _ServerContext:
    def __init__(self, handler):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return f"http://127.0.0.1:{self.server.server_address[1]}/v1/chat/completions"

    def __exit__(self, *_args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1)


class _SuccessHandler(BaseHTTPRequestHandler):
    last_body = {}
    last_path = ""

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        _SuccessHandler.last_body = json.loads(body.decode("utf-8"))
        _SuccessHandler.last_path = self.path
        self._write(200, {"choices": [{"message": {"content": "agent reply"}}]})

    def _write(self, status, payload):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        return


class _ErrorHandler(_SuccessHandler):
    def do_POST(self):
        self._write(502, {"error": "bad gateway"})


class _EmptyReplyHandler(_SuccessHandler):
    def do_POST(self):
        self._write(200, {"choices": [{"message": {"content": ""}}]})


class _ToolEventsHandler(_SuccessHandler):
    def do_POST(self):
        self._write(
            200,
            {
                "choices": [{"message": {"content": "agent reply"}}],
                "xiaomiao_tool_events": [
                    {
                        "event_type": "stage_action",
                        "tool_name": "xiaomiaobot_action",
                        "risk_level": "high",
                        "confirmation_id": "ABC123",
                        "result_summary": "stage:say",
                    }
                ],
            },
        )


class _SlowHandler(_SuccessHandler):
    def do_POST(self):
        time.sleep(0.2)
        self._write(200, {"choices": [{"message": {"content": "late"}}]})


def _agent_server(handler):
    return _ServerContext(handler)


def _config(base_url: str, timeout_seconds: float = 1.0) -> XiaomiaoAgentConfig:
    return XiaomiaoAgentConfig(
        enabled=True,
        base_url=base_url,
        model=None,
        session_id="xiaomiao-unified",
        timeout_seconds=timeout_seconds,
    )


def _payload(
    text: str,
    media: tuple[str, ...] = (),
    tool_policy: str | None = None,
    confirmation_id: str | None = None,
) -> XiaomiaoAgentRequest:
    return XiaomiaoAgentRequest(
        user_id=3554978979,
        channel="web",
        chat_id="stage-web",
        text=text,
        media=media,
        tool_policy=tool_policy,
        confirmation_id=confirmation_id,
    )


if __name__ == "__main__":
    unittest.main()
