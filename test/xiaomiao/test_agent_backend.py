import json
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from agent_backend import (  # noqa: E402
    DEFAULT_NANOBOT_BASE_URL,
    DEFAULT_NANOBOT_SESSION_ID,
    NanobotAgentConfig,
    NanobotAgentRequest,
    load_nanobot_agent_config,
    reply_with_nanobot_agent,
)


class AgentBackendTests(unittest.TestCase):
    def test_load_config_uses_enabled_defaults(self):
        config = load_nanobot_agent_config({})

        self.assertTrue(config.enabled)
        self.assertEqual(config.base_url, DEFAULT_NANOBOT_BASE_URL)
        self.assertIsNone(config.model)
        self.assertEqual(config.session_id, DEFAULT_NANOBOT_SESSION_ID)

    def test_disabled_config_raises_without_request(self):
        config = NanobotAgentConfig(
            enabled=False,
            base_url="http://127.0.0.1:1/v1/chat/completions",
            model=None,
            session_id="xiaomiao-unified",
            timeout_seconds=0.01,
        )

        with self.assertRaisesRegex(RuntimeError, "disabled"):
            reply_with_nanobot_agent(config, _payload("hello"))

    def test_successful_agent_reply_uses_unified_session(self):
        with _agent_server(_SuccessHandler) as base_url:
            reply = reply_with_nanobot_agent(_config(base_url), _payload("你好"))

        self.assertEqual(reply, "agent reply")
        self.assertEqual(_SuccessHandler.last_body["session_id"], "xiaomiao-unified")
        self.assertEqual(_SuccessHandler.last_body["messages"][0]["content"], "你好")

    def test_http_error_is_visible(self):
        with _agent_server(_ErrorHandler) as base_url:
            with self.assertRaisesRegex(RuntimeError, "HTTP 502"):
                reply_with_nanobot_agent(_config(base_url), _payload("hello"))

    def test_empty_agent_reply_is_visible(self):
        with _agent_server(_EmptyReplyHandler) as base_url:
            with self.assertRaisesRegex(RuntimeError, "empty reply"):
                reply_with_nanobot_agent(_config(base_url), _payload("hello"))

    def test_timeout_is_visible(self):
        with _agent_server(_SlowHandler) as base_url:
            config = _config(base_url, timeout_seconds=0.01)
            with self.assertRaisesRegex(RuntimeError, "request failed"):
                reply_with_nanobot_agent(config, _payload("hello"))


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

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        _SuccessHandler.last_body = json.loads(body.decode("utf-8"))
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


class _SlowHandler(_SuccessHandler):
    def do_POST(self):
        time.sleep(0.2)
        self._write(200, {"choices": [{"message": {"content": "late"}}]})


def _agent_server(handler):
    return _ServerContext(handler)


def _config(base_url: str, timeout_seconds: float = 1.0) -> NanobotAgentConfig:
    return NanobotAgentConfig(
        enabled=True,
        base_url=base_url,
        model=None,
        session_id="xiaomiao-unified",
        timeout_seconds=timeout_seconds,
    )


def _payload(text: str) -> NanobotAgentRequest:
    return NanobotAgentRequest(
        user_id=3554978979,
        channel="web",
        chat_id="stage-web",
        text=text,
    )


if __name__ == "__main__":
    unittest.main()
