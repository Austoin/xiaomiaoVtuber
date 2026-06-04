import json
import socket
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from unified_config import merge_unified_config_section


DEFAULT_XIAOMIAO_AGENT_BASE_URL = "http://127.0.0.1:8900/v1/chat/completions"
DEFAULT_XIAOMIAO_AGENT_SESSION_ID = "xiaomiao-unified"
DEFAULT_XIAOMIAO_AGENT_TIMEOUT_SECONDS = 30.0


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
        timeout_seconds=float(raw_config.get("timeout_seconds") or DEFAULT_XIAOMIAO_AGENT_TIMEOUT_SECONDS),
    )


def reply_with_xiaomiao_agent(
    config: XiaomiaoAgentConfig,
    payload: XiaomiaoAgentRequest,
) -> str:
    if not config.enabled:
        raise RuntimeError("xiaomiaoAgent backend is disabled")
    if not payload.text.strip():
        raise RuntimeError("xiaomiaoAgent backend requires non-empty text")

    body = _build_request_body(config, payload)
    raw_response = _post_json(config.base_url, body, config.timeout_seconds)
    return _extract_assistant_text(raw_response)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _build_request_body(
    config: XiaomiaoAgentConfig,
    payload: XiaomiaoAgentRequest,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "messages": [{"role": "user", "content": payload.text}],
        "session_id": config.session_id,
    }
    if config.model:
        body["model"] = config.model
    return body


def _post_json(url: str, body: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"xiaomiaoAgent HTTP {exc.code}: {detail}") from exc
    except (error.URLError, socket.timeout, TimeoutError) as exc:
        raise RuntimeError(f"xiaomiaoAgent request failed: {exc}") from exc


def _extract_assistant_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("xiaomiaoAgent response missing choices")

    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("xiaomiaoAgent returned an empty reply")
    return content.strip()
