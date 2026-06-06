"""xiaomiaoVirtual stage bridge tool."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib import error, request

from nanobot.agent.tools.base import Tool, tool_parameters
from nanobot.agent.tools.context import ContextAware, RequestContext
from nanobot.agent.tools.schema import StringSchema, tool_parameters_schema


DEFAULT_BRIDGE_EVENTS_URL = "http://127.0.0.1:5519/v1/xiaomiao/events"


@tool_parameters(
    tool_parameters_schema(
        action=StringSchema(
            "Stage action type. Examples: say, subtitle, emotion, background, model, tts."
        ),
        content=StringSchema("Human-readable action content to show on the stage/event stream."),
        required=["action", "content"],
    )
)
class XiaomiaoStageTool(Tool, ContextAware):
    """Publish stage actions to the xiaomiao desktop bridge."""

    _scopes = {"core", "subagent"}

    def __init__(self, bridge_events_url: str = DEFAULT_BRIDGE_EVENTS_URL):
        self.bridge_events_url = bridge_events_url
        self._context: RequestContext | None = None

    @property
    def name(self) -> str:
        return "xiaomiao_stage"

    @property
    def description(self) -> str:
        return (
            "Send a xiaomiaoVirtual stage action through the local bridge event stream. "
            "Use it for desktop subtitles, TTS/say requests, emotions, backgrounds, "
            "or model-switch instructions after the user has authorized high-risk tools."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return self.__class__.parameters  # type: ignore[attr-defined]

    @property
    def exclusive(self) -> bool:
        return True

    def set_context(self, ctx: RequestContext) -> None:
        self._context = ctx

    async def execute(self, action: str, content: str, **kwargs: Any) -> str:
        normalized_action = action.strip().lower()
        event_content = _compact_json(
            {
                "service": "stage",
                "action": normalized_action,
                "payload": _stage_payload(normalized_action, content),
            }
        )
        payload = {
            "source": "xiaomiao-agent-tool",
            "channel": self._context.channel if self._context else "agent-tool",
            "chat_id": self._context.chat_id if self._context else "stage",
            "user_id": _safe_user_id(self._context),
            "role": "assistant",
            "content": event_content,
            "event_type": "stage_action",
            "tool_name": self.name,
            "risk_level": "high",
            "result_summary": normalized_action,
        }
        if self._context and self._context.metadata.get("confirmation_id"):
            payload["confirmation_id"] = str(self._context.metadata["confirmation_id"])

        await asyncio.to_thread(_post_json, self.bridge_events_url, payload)
        return f"Stage action published: {normalized_action}"


def _safe_user_id(ctx: RequestContext | None) -> int:
    if ctx is None:
        return 0
    value = ctx.metadata.get("source_user_id") or ctx.chat_id
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _stage_payload(action: str, content: str) -> dict[str, Any]:
    text = content.strip()
    parsed = _parse_object(text)
    if parsed is not None:
        return parsed

    if action in {"say", "tts", "subtitle"}:
        return {"text": text}
    if action == "emotion":
        return {"name": text, "intensity": 1}
    if action == "background":
        return {"id": text}
    if action == "model":
        return {"id": text}
    if action == "status":
        return {"query": text or "current"}
    return {"text": text}


def _parse_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _compact_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


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
