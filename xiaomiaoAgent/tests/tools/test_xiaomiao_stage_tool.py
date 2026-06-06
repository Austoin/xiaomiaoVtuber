from __future__ import annotations

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from nanobot.agent.tools.context import RequestContext
from nanobot.agent.tools.xiaomiao_stage import XiaomiaoStageTool


def test_xiaomiao_stage_tool_posts_stage_action_event() -> None:
    with _server() as server:
        tool = XiaomiaoStageTool(bridge_events_url=server.url)
        tool.set_context(
            RequestContext(
                channel="qq-group",
                chat_id="10001",
                metadata={
                    "source_user_id": "3554978979",
                    "confirmation_id": "ABC123",
                },
            )
        )

        result = asyncio.run(tool.execute(action="say", content="小喵说你好"))

    assert result == "Stage action published: say"
    assert _Handler.last_body == {
        "source": "xiaomiao-agent-tool",
        "channel": "qq-group",
        "chat_id": "10001",
        "user_id": 3554978979,
        "role": "assistant",
        "content": json.dumps(
            {
                "service": "stage",
                "action": "say",
                "payload": {"text": "小喵说你好"},
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        "event_type": "stage_action",
        "tool_name": "xiaomiao_stage",
        "risk_level": "high",
        "result_summary": "say",
        "confirmation_id": "ABC123",
    }


class _Server:
    def __init__(self):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}/v1/xiaomiao/events"

    def __enter__(self):
        _Handler.last_body = {}
        self.thread.start()
        return self

    def __exit__(self, *_args):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=1)


class _Handler(BaseHTTPRequestHandler):
    last_body: dict = {}

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        _Handler.last_body = json.loads(body.decode("utf-8"))
        encoded = json.dumps({"event": _Handler.last_body}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        return


def _server():
    return _Server()
