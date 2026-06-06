"""xiaomiaobot service bridge tools."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib import error, request

from nanobot.agent.tools.base import Tool, tool_parameters
from nanobot.agent.tools.context import ContextAware, RequestContext
from nanobot.agent.tools.schema import ObjectSchema, StringSchema, tool_parameters_schema


DEFAULT_BRIDGE_EVENTS_URL = "http://127.0.0.1:5519/v1/xiaomiao/events"
DEFAULT_BRIDGE_STATUS_URL = "http://127.0.0.1:5519/v1/xiaomiao/status"

STATUS_SERVICES = (
    "all",
    "stage",
    "computer_use",
    "minecraft",
    "twitter",
    "homeassistant",
    "bilibili",
    "chess",
    "claude_code",
    "browser_extension",
)
ACTION_SERVICES = tuple(service for service in STATUS_SERVICES if service != "all")
EXECUTABLE_ACTION_SERVICES = frozenset({"stage"})

CAPABILITY_STATUSES: dict[str, dict[str, Any]] = {
    "stage": {
        "capability_status": "qq_agent_ready",
        "read": True,
        "action": True,
        "qq_agent_ready": True,
        "summary": "Stage subtitles, TTS/say, emotion, background, model, and status are bridged through stage_action events.",
    },
    "computer_use": {
        "capability_status": "action_ready",
        "read": True,
        "action": True,
        "bridge_action": False,
        "qq_agent_ready": True,
        "mcp_profile": "tools.computer_use_mcp.enable",
        "summary": "Computer Use is exposed through an opt-in Agent MCP profile; low-risk reads are filtered separately from confirmed desktop/terminal actions.",
    },
    "minecraft": {
        "capability_status": "action_ready",
        "read": True,
        "action": True,
        "bridge_action": False,
        "qq_agent_ready": True,
        "mcp_profile": "tools.minecraft_mcp.enable",
        "summary": "Minecraft debug MCP is exposed through an opt-in Agent MCP profile; state/log reads are low-risk and injections require confirmation.",
    },
    "twitter": {
        "capability_status": "action_ready",
        "read": True,
        "action": True,
        "bridge_action": False,
        "qq_agent_ready": True,
        "mcp_profile": "tools.twitter_mcp.enable",
        "summary": "Twitter MCP is exposed through an opt-in Agent MCP profile; search/profile reads are low-risk and account actions require confirmation.",
    },
    "homeassistant": {
        "capability_status": "wip",
        "read": False,
        "action": False,
        "qq_agent_ready": False,
        "summary": "HomeAssistant plugin entry is present but not QQ Agent ready.",
    },
    "bilibili": {
        "capability_status": "wip",
        "read": False,
        "action": False,
        "qq_agent_ready": False,
        "summary": "Bilibili live chat plugin path is present but not QQ Agent ready.",
    },
    "chess": {
        "capability_status": "wip",
        "read": False,
        "action": False,
        "qq_agent_ready": False,
        "summary": "Chess gamelet packages exist, but no stable QQ Agent adapter is wired.",
    },
    "claude_code": {
        "capability_status": "wip",
        "read": False,
        "action": False,
        "qq_agent_ready": False,
        "summary": "Claude Code hooks can reach the channel layer, but controlled QQ tool execution is not wired.",
    },
    "browser_extension": {
        "capability_status": "wip",
        "read": False,
        "action": False,
        "qq_agent_ready": False,
        "summary": "Browser extension context bridge exists, but QQ Agent context adapter is not wired.",
    },
}


@tool_parameters(
    tool_parameters_schema(
        service=StringSchema(
            "xiaomiaobot service to inspect.",
            enum=STATUS_SERVICES,
        ),
        query=StringSchema(
            "Optional read-only query, such as twitter search terms or status detail.",
            nullable=True,
        ),
        required=["service"],
    )
)
class XiaomiaobotStatusTool(Tool, ContextAware):
    """Read xiaomiaobot bridge/service status through the local bridge."""

    _scopes = {"core", "subagent"}

    def __init__(
        self,
        bridge_status_url: str = DEFAULT_BRIDGE_STATUS_URL,
        bridge_events_url: str = DEFAULT_BRIDGE_EVENTS_URL,
    ):
        self.bridge_status_url = bridge_status_url
        self.bridge_events_url = bridge_events_url
        self._context: RequestContext | None = None

    @property
    def name(self) -> str:
        return "xiaomiaobot_status"

    @property
    def description(self) -> str:
        return (
            "Read low-risk xiaomiaobot service status or request a read-only service query. "
            "Supported services include stage, computer_use, minecraft, twitter, "
            "homeassistant, bilibili, chess, claude_code, and browser_extension."
        )

    @property
    def read_only(self) -> bool:
        return True

    def set_context(self, ctx: RequestContext) -> None:
        self._context = ctx

    async def execute(self, service: str, query: str | None = None, **_kwargs: Any) -> str:
        status = await asyncio.to_thread(_get_json, self.bridge_status_url)
        summary = _status_summary(status)
        capabilities = _service_capabilities(service)
        event_content = _compact_json(
            {
                "service": service,
                "query": query,
                "bridge_status": summary,
                "capabilities": capabilities,
                "note": "Only capabilities marked qq_agent_ready are directly executable from QQ Agent.",
            }
        )
        await asyncio.to_thread(
            _post_json,
            self.bridge_events_url,
            _event_payload(
                ctx=self._context,
                content=event_content,
                event_type="tool_finish",
                tool_name=self.name,
                risk_level="low",
                result_summary=f"{service}:status",
            ),
        )
        return _status_response_text(service, summary, capabilities)


@tool_parameters(
    tool_parameters_schema(
        service=StringSchema(
            "xiaomiaobot service to control.",
            enum=ACTION_SERVICES,
        ),
        action=StringSchema("Action name, such as say, move, post, like, control, or open."),
        payload=ObjectSchema(
            description="Action payload for the service adapter.",
            additional_properties=True,
        ),
        required=["service", "action", "payload"],
    )
)
class XiaomiaobotActionTool(Tool, ContextAware):
    """Publish confirmed xiaomiaobot service actions to the bridge event stream."""

    _scopes = {"core", "subagent"}

    def __init__(self, bridge_events_url: str = DEFAULT_BRIDGE_EVENTS_URL):
        self.bridge_events_url = bridge_events_url
        self._context: RequestContext | None = None

    @property
    def name(self) -> str:
        return "xiaomiaobot_action"

    @property
    def description(self) -> str:
        return (
            "Queue a confirmed xiaomiaobot service action through the local bridge. "
            "Currently only stage actions are executable end-to-end. Other services "
            "return explicit capability errors until their adapters are wired."
        )

    @property
    def exclusive(self) -> bool:
        return True

    def set_context(self, ctx: RequestContext) -> None:
        self._context = ctx

    async def execute(self, service: str, action: str, payload: dict[str, Any], **_kwargs: Any) -> str:
        if service not in EXECUTABLE_ACTION_SERVICES:
            capability = CAPABILITY_STATUSES.get(service, {})
            status = capability.get("capability_status", "unknown")
            summary = capability.get("summary", "No service adapter is available.")
            if capability.get("qq_agent_ready") and capability.get("bridge_action") is False:
                profile = capability.get("mcp_profile", "the matching Agent MCP profile")
                raise RuntimeError(
                    f"xiaomiaobot service '{service}' is not bridge-action-ready for "
                    f"xiaomiaobot_action (capability_status={status}). Use {profile} "
                    f"and the corresponding MCP tools instead. {summary}"
                )
            raise RuntimeError(
                f"xiaomiaobot service '{service}' is not QQ Agent action-ready "
                f"(capability_status={status}). {summary}"
            )

        risk_level = _action_risk(service, action)
        event_type = "stage_action" if service == "stage" else "tool_start"
        content = _compact_json(
            {
                "service": service,
                "action": action,
                "payload": payload,
                "note": "confirmed request queued for xiaomiaobot service adapter",
            }
        )
        await asyncio.to_thread(
            _post_json,
            self.bridge_events_url,
            _event_payload(
                ctx=self._context,
                content=content,
                event_type=event_type,
                tool_name=self.name,
                risk_level=risk_level,
                result_summary=f"{service}:{action}",
            ),
        )
        return f"xiaomiaobot action queued: {service}:{action}"


def _action_risk(service: str, action: str) -> str:
    normalized = f"{service}:{action}".lower()
    if service in {"computer_use", "homeassistant", "claude_code"}:
        return "high"
    if service == "twitter" and any(word in normalized for word in ("post", "like", "retweet")):
        return "high"
    if service == "minecraft" and any(word in normalized for word in ("move", "attack", "place", "dig", "chat")):
        return "high"
    return "medium"


def _service_capabilities(service: str) -> dict[str, Any]:
    if service == "all":
        return {name: dict(value) for name, value in CAPABILITY_STATUSES.items()}
    return dict(CAPABILITY_STATUSES.get(service, {
        "capability_status": "not_started",
        "read": False,
        "action": False,
        "qq_agent_ready": False,
        "summary": "No capability adapter has been registered for this service.",
    }))


def _status_response_text(service: str, bridge_summary: str, capabilities: dict[str, Any]) -> str:
    if service == "all":
        ready = [
            name
            for name, info in capabilities.items()
            if isinstance(info, dict) and info.get("qq_agent_ready")
        ]
        wip = [
            name
            for name, info in capabilities.items()
            if isinstance(info, dict) and info.get("capability_status") == "wip"
        ]
        return (
            f"xiaomiaobot bridge status: {bridge_summary}. "
            f"QQ Agent ready: {', '.join(ready) or 'none'}. "
            f"WIP: {', '.join(wip) or 'none'}."
        )

    capability_status = str(capabilities.get("capability_status") or "unknown")
    summary = str(capabilities.get("summary") or "")
    return (
        f"xiaomiaobot bridge status: {bridge_summary}. "
        f"Service '{service}' capability_status={capability_status}. {summary}"
    )


def _event_payload(
    *,
    ctx: RequestContext | None,
    content: str,
    event_type: str,
    tool_name: str,
    risk_level: str,
    result_summary: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "source": "xiaomiao-agent-tool",
        "channel": ctx.channel if ctx else "agent-tool",
        "chat_id": ctx.chat_id if ctx else "xiaomiaobot",
        "user_id": _safe_user_id(ctx),
        "role": "assistant",
        "content": content,
        "event_type": event_type,
        "tool_name": tool_name,
        "risk_level": risk_level,
        "result_summary": result_summary,
    }
    confirmation_id = ctx.metadata.get("confirmation_id") if ctx else None
    if confirmation_id:
        payload["confirmation_id"] = str(confirmation_id)
    return payload


def _safe_user_id(ctx: RequestContext | None) -> int:
    if ctx is None:
        return 0
    value = ctx.metadata.get("source_user_id") or ctx.chat_id
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _status_summary(status: dict[str, Any]) -> str:
    ok = bool(status.get("ok"))
    service = status.get("service") or "unknown"
    return f"{service} online={ok}"


def _compact_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _get_json(url: str) -> dict[str, Any]:
    try:
        with request.urlopen(url, timeout=5) as response:
            if response.status >= 400:
                raise RuntimeError(f"bridge returned HTTP {response.status}")
            data = response.read()
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"bridge returned HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"bridge request failed: {exc}") from exc
    parsed = json.loads(data.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise RuntimeError("bridge status response must be an object")
    return parsed


def _post_json(url: str, payload: dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=5) as response:
            if response.status >= 400:
                raise RuntimeError(f"bridge returned HTTP {response.status}")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"bridge returned HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"bridge request failed: {exc}") from exc
