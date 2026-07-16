from __future__ import annotations

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from nanobot.agent.tools.context import RequestContext
from nanobot.agent.tools.xiaomiaobot_services import (
    DEFAULT_BRIDGE_EVENTS_URL,
    DEFAULT_BRIDGE_STATUS_URL,
    XiaomiaobotActionTool,
    XiaomiaobotStatusTool,
)
from nanobot.agent.tools.xiaomiao_stage import DEFAULT_BRIDGE_EVENTS_URL as STAGE_EVENTS_URL
from nanobot.channels.websocket import DEFAULT_XIAOMIAO_BRIDGE_EVENTS_URL


def test_agent_owned_event_routes_use_port_8900() -> None:
    assert DEFAULT_BRIDGE_EVENTS_URL == "http://127.0.0.1:8900/v1/xiaomiao/events"
    assert STAGE_EVENTS_URL == DEFAULT_BRIDGE_EVENTS_URL
    assert DEFAULT_XIAOMIAO_BRIDGE_EVENTS_URL == DEFAULT_BRIDGE_EVENTS_URL
    assert DEFAULT_BRIDGE_STATUS_URL == "http://127.0.0.1:8900/health"


def test_xiaomiaobot_status_tool_posts_low_risk_status_event() -> None:
    with _server() as server:
        tool = XiaomiaobotStatusTool(
            bridge_status_url=server.status_url,
            bridge_events_url=server.events_url,
        )
        tool.set_context(
            RequestContext(
                channel="qq-group",
                chat_id="10001",
                metadata={"source_user_id": "3554978979"},
            )
        )

        result = asyncio.run(tool.execute(service="minecraft", query="status"))

    assert result == (
        "xiaomiaobot bridge status: xiaomiao-desktop-bridge online=True. "
        "Service 'minecraft' capability_status=action_ready. "
        "Minecraft debug MCP is exposed through an opt-in Agent MCP profile; "
        "state/log reads are low-risk and injections require confirmation."
    )
    assert _Handler.last_body["event_type"] == "tool_finish"
    assert _Handler.last_body["tool_name"] == "xiaomiaobot_status"
    assert _Handler.last_body["risk_level"] == "low"
    assert _Handler.last_body["result_summary"] == "minecraft:status"
    content = json.loads(_Handler.last_body["content"])
    assert content["service"] == "minecraft"
    assert content["query"] == "status"
    assert content["bridge_status"] == "xiaomiao-desktop-bridge online=True"
    assert content["capabilities"]["capability_status"] == "action_ready"
    assert content["capabilities"]["qq_agent_ready"] is True
    assert content["capabilities"]["bridge_action"] is False
    assert content["capabilities"]["mcp_profile"] == "tools.minecraft_mcp.enable"


def test_xiaomiaobot_status_tool_reports_all_capabilities() -> None:
    with _server() as server:
        tool = XiaomiaobotStatusTool(
            bridge_status_url=server.status_url,
            bridge_events_url=server.events_url,
        )

        result = asyncio.run(tool.execute(service="all"))

    assert "QQ Agent ready: stage" in result
    assert "computer_use" not in result.split("WIP:", 1)[-1]
    content = json.loads(_Handler.last_body["content"])
    assert content["capabilities"]["stage"]["capability_status"] == "qq_agent_ready"
    assert content["capabilities"]["computer_use"]["capability_status"] == "action_ready"
    assert content["capabilities"]["twitter"]["mcp_profile"] == "tools.twitter_mcp.enable"


def test_xiaomiaobot_action_tool_posts_confirmed_stage_event() -> None:
    with _server() as server:
        tool = XiaomiaobotActionTool(bridge_events_url=server.events_url)
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

        result = asyncio.run(
            tool.execute(
                service="stage",
                action="say",
                payload={"text": "你好"},
            )
        )

    assert result == "xiaomiaobot action queued: stage:say"
    assert _Handler.last_body["event_type"] == "stage_action"
    assert _Handler.last_body["tool_name"] == "xiaomiaobot_action"
    assert _Handler.last_body["risk_level"] == "medium"
    assert _Handler.last_body["result_summary"] == "stage:say"
    assert _Handler.last_body["confirmation_id"] == "ABC123"
    content = json.loads(_Handler.last_body["content"])
    assert content["service"] == "stage"
    assert content["action"] == "say"
    assert content["payload"] == {"text": "你好"}


def test_xiaomiaobot_action_tool_rejects_wip_services_without_fake_success() -> None:
    with _server() as server:
        tool = XiaomiaobotActionTool(bridge_events_url=server.events_url)

        try:
            asyncio.run(
                tool.execute(
                    service="homeassistant",
                    action="control",
                    payload={"entity_id": "light.desk", "state": "on"},
                )
            )
        except RuntimeError as exc:
            error_text = str(exc)
        else:
            raise AssertionError("expected wip service action to fail")

    assert "not QQ Agent action-ready" in error_text
    assert "capability_status=wip" in error_text
    assert _Handler.last_body == {}


def test_xiaomiaobot_action_tool_points_mcp_profile_services_to_mcp_tools() -> None:
    with _server() as server:
        tool = XiaomiaobotActionTool(bridge_events_url=server.events_url)

        try:
            asyncio.run(
                tool.execute(
                    service="twitter",
                    action="post-tweet",
                    payload={"content": "hello"},
                )
            )
        except RuntimeError as exc:
            error_text = str(exc)
        else:
            raise AssertionError("expected mcp-profile service action to fail")

    assert "not bridge-action-ready" in error_text
    assert "tools.twitter_mcp.enable" in error_text
    assert "corresponding MCP tools" in error_text
    assert _Handler.last_body == {}


class _Server:
    def __init__(self):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        port = self.httpd.server_address[1]
        self.status_url = f"http://127.0.0.1:{port}/v1/xiaomiao/status"
        self.events_url = f"http://127.0.0.1:{port}/v1/xiaomiao/events"

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

    def do_GET(self):
        if self.path != "/v1/xiaomiao/status":
            self.send_response(404)
            self.end_headers()
            return
        self._write_json(
            200,
            {
                "ok": True,
                "service": "xiaomiao-desktop-bridge",
            },
        )

    def do_POST(self):
        if self.path != "/v1/xiaomiao/events":
            self.send_response(404)
            self.end_headers()
            return
        body = self.rfile.read(int(self.headers["Content-Length"]))
        _Handler.last_body = json.loads(body.decode("utf-8"))
        self._write_json(200, {"event": _Handler.last_body})

    def _write_json(self, status: int, payload: dict) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        return


def _server():
    return _Server()
