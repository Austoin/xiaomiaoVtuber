import base64
import json
import mimetypes
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urlsplit, urlunsplit

from unified_config import merge_unified_config_section


DEFAULT_XIAOMIAO_AGENT_BASE_URL = "http://127.0.0.1:8900/v1/chat/completions"
DEFAULT_XIAOMIAO_AGENT_SESSION_ID = "xiaomiao-unified"
DEFAULT_XIAOMIAO_AGENT_TIMEOUT_SECONDS = 0.0


@dataclass(frozen=True)
class XiaomiaoAgentConfig:
    enabled: bool
    base_url: str
    model: str | None
    session_id: str
    timeout_seconds: float


@dataclass(frozen=True)
class XiaomiaoAgentRequest:
    user_id: int
    channel: str
    chat_id: str
    text: str
    media: tuple[str, ...] = ()
    tool_policy: str | None = None
    confirmation_id: str | None = None


@dataclass(frozen=True)
class XiaomiaoAgentResponse:
    assistant_text: str
    tool_events: tuple[dict[str, Any], ...] = ()


def load_xiaomiao_agent_config(others: dict[str, Any]) -> XiaomiaoAgentConfig:
    raw_config = merge_unified_config_section(
        "xiaomiao_agent",
        others.get("xiaomiao_agent", {}),
    )

    return XiaomiaoAgentConfig(
        enabled=bool(raw_config.get("enabled", True)),
        base_url=str(raw_config.get("base_url") or DEFAULT_XIAOMIAO_AGENT_BASE_URL),
        model=_optional_text(raw_config.get("model")),
        session_id=str(raw_config.get("session_id") or DEFAULT_XIAOMIAO_AGENT_SESSION_ID),
        timeout_seconds=_timeout_seconds(raw_config),
    )


def reply_with_xiaomiao_agent(
    config: XiaomiaoAgentConfig,
    payload: XiaomiaoAgentRequest,
) -> str:
    return request_xiaomiao_agent(config, payload).assistant_text


def request_xiaomiao_agent(
    config: XiaomiaoAgentConfig,
    payload: XiaomiaoAgentRequest,
) -> XiaomiaoAgentResponse:
    if not config.enabled:
        raise RuntimeError("xiaomiaoAgent backend is disabled")
    if not payload.text.strip():
        raise RuntimeError("xiaomiaoAgent backend requires non-empty text")

    body = _build_request_body(config, payload)
    raw_response = _post_json(config.base_url, body, config.timeout_seconds)
    return _extract_agent_response(raw_response)


def publish_xiaomiao_agent_event(
    config: XiaomiaoAgentConfig,
    event: dict[str, Any],
) -> None:
    if not config.enabled:
        raise RuntimeError("xiaomiaoAgent backend is disabled")
    parsed = urlsplit(config.base_url)
    events_url = urlunsplit(
        (parsed.scheme, parsed.netloc, "/v1/xiaomiao/events", "", "")
    )
    _post_json(events_url, event, config.timeout_seconds)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _timeout_seconds(raw_config: dict[str, Any]) -> float:
    if "timeout_seconds" not in raw_config or raw_config.get("timeout_seconds") is None:
        return DEFAULT_XIAOMIAO_AGENT_TIMEOUT_SECONDS
    return float(raw_config.get("timeout_seconds"))


def _build_request_body(
    config: XiaomiaoAgentConfig,
    payload: XiaomiaoAgentRequest,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "messages": [{"role": "user", "content": _build_user_content(payload)}],
        "session_id": config.session_id,
        "channel": payload.channel,
        "chat_id": payload.chat_id,
        "user_id": str(payload.user_id),
    }
    if config.model:
        body["model"] = config.model
    if payload.tool_policy:
        body["tool_policy"] = payload.tool_policy
    if payload.confirmation_id:
        body["confirmation_id"] = payload.confirmation_id
    return body


def _build_user_content(payload: XiaomiaoAgentRequest) -> str | list[dict[str, Any]]:
    if not payload.media:
        return payload.text

    content: list[dict[str, Any]] = [{"type": "text", "text": payload.text}]
    for media_item in payload.media:
        content.append({
            "type": "image_url",
            "image_url": {"url": _media_to_data_url(media_item)},
        })
    return content


def _media_to_data_url(media_item: str) -> str:
    if media_item.startswith("data:"):
        return media_item

    media_path = Path(media_item)
    if not media_path.is_file():
        raise RuntimeError(f"media file not found: {media_item}")

    mime_type = mimetypes.guess_type(media_path.name)[0] or "application/octet-stream"
    if not mime_type.startswith("image/"):
        raise RuntimeError(f"unsupported media type for image_url: {mime_type}")

    encoded = base64.b64encode(media_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _post_json(url: str, body: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        if timeout_seconds <= 0:
            with request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        with request.urlopen(req, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"xiaomiaoAgent HTTP {exc.code}: {detail}") from exc
    except (error.URLError, socket.timeout, TimeoutError) as exc:
        raise RuntimeError(f"xiaomiaoAgent request failed: {exc}") from exc


def _extract_assistant_text(response: dict[str, Any]) -> str:
    return _extract_agent_response(response).assistant_text


def _extract_agent_response(response: dict[str, Any]) -> XiaomiaoAgentResponse:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("xiaomiaoAgent response missing choices")

    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("xiaomiaoAgent returned an empty reply")
    return XiaomiaoAgentResponse(
        assistant_text=content.strip(),
        tool_events=_extract_tool_events(response),
    )


def _extract_tool_events(response: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    raw_events = response.get("xiaomiao_tool_events")
    if raw_events is None:
        return ()
    if not isinstance(raw_events, list):
        raise RuntimeError("xiaomiaoAgent tool events must be a list")
    events: list[dict[str, Any]] = []
    for event in raw_events:
        if not isinstance(event, dict):
            raise RuntimeError("xiaomiaoAgent tool event must be an object")
        events.append(dict(event))
    return tuple(events)
