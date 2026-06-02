import json
import socket
from dataclasses import dataclass
from typing import Any
from urllib import error, request


DEFAULT_NANOBOT_BASE_URL = "http://127.0.0.1:8900/v1/chat/completions"
DEFAULT_NANOBOT_SESSION_ID = "xiaomiao-unified"
DEFAULT_NANOBOT_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True)
class NanobotAgentConfig:
    enabled: bool
    base_url: str
    model: str | None
    session_id: str
    timeout_seconds: float


@dataclass(frozen=True)
class NanobotAgentRequest:
    user_id: int
    channel: str
    chat_id: str
    text: str
    media: tuple[str, ...] = ()


def load_nanobot_agent_config(others: dict[str, Any]) -> NanobotAgentConfig:
    raw_config = others.get("nanobot_agent", {})
    if raw_config is None:
        raw_config = {}
    if not isinstance(raw_config, dict):
        raise ValueError("Others.nanobot_agent must be an object")

    return NanobotAgentConfig(
        enabled=bool(raw_config.get("enabled", True)),
        base_url=str(raw_config.get("base_url") or DEFAULT_NANOBOT_BASE_URL),
        model=_optional_text(raw_config.get("model")),
        session_id=str(raw_config.get("session_id") or DEFAULT_NANOBOT_SESSION_ID),
        timeout_seconds=float(raw_config.get("timeout_seconds") or DEFAULT_NANOBOT_TIMEOUT_SECONDS),
    )


def reply_with_nanobot_agent(
    config: NanobotAgentConfig,
    payload: NanobotAgentRequest,
) -> str:
    if not config.enabled:
        raise RuntimeError("Nanobot Agent backend is disabled")
    if not payload.text.strip():
        raise RuntimeError("Nanobot Agent backend requires non-empty text")

    body = _build_request_body(config, payload)
    raw_response = _post_json(config.base_url, body, config.timeout_seconds)
    return _extract_assistant_text(raw_response)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _build_request_body(
    config: NanobotAgentConfig,
    payload: NanobotAgentRequest,
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
        raise RuntimeError(f"Nanobot Agent HTTP {exc.code}: {detail}") from exc
    except (error.URLError, socket.timeout, TimeoutError) as exc:
        raise RuntimeError(f"Nanobot Agent request failed: {exc}") from exc


def _extract_assistant_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("Nanobot Agent response missing choices")

    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Nanobot Agent returned an empty reply")
    return content.strip()
