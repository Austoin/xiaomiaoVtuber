"""Agent-owned event and unified configuration services."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from threading import RLock
from typing import Any
from urllib.parse import urlsplit

from nanobot.config.paths import get_config_path, get_runtime_subdir

EVENT_STORE_ENV = "XIAOMIAO_EVENT_STORE"
UNIFIED_CONFIG_ENV = "XIAOMIAO_UNIFIED_CONFIG"
EVENT_SCHEMA_VERSION = 1
EVENT_ROLES = frozenset({"user", "assistant"})
EVENT_METADATA_FIELDS = (
    "client_message_id",
    "event_type",
    "tool_name",
    "risk_level",
    "confirmation_id",
    "result_summary",
)


def default_event_store_path() -> Path:
    configured = os.environ.get(EVENT_STORE_ENV)
    if configured:
        return Path(configured)
    return get_runtime_subdir("events") / "events.jsonl"


def default_unified_config_path() -> Path:
    configured = os.environ.get(UNIFIED_CONFIG_ENV)
    if configured:
        return Path(configured)

    active_config = get_config_path().resolve(strict=False)
    for parent in active_config.parents:
        candidate = parent / "config.json"
        if candidate != active_config and candidate.exists():
            return candidate

    for parent in Path(__file__).resolve().parents:
        if (parent / "xiaomiaoAgent").is_dir():
            return parent / "config.json"
    raise FileNotFoundError("Unable to locate the unified xiaomiao config.json")


class XiaomiaoEventStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_event_store_path()
        self._lock = RLock()
        self._events = self._load()
        self._next_id = max((event["id"] for event in self._events), default=0) + 1

    def publish(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = self._normalize_new_event(payload)
        with self._lock:
            event["id"] = self._next_id
            event["message_id"] = _message_id(event)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as output:
                output.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
                output.write("\n")
            self._events.append(event)
            self._next_id += 1
        return dict(event)

    def publish_exchange(
        self,
        *,
        source: str,
        chat_id: str,
        user_id: str,
        user_text: str,
        assistant_text: str,
        client_message_id: str | None = None,
    ) -> list[dict[str, Any]]:
        common = {
            "source": source,
            "channel": source,
            "chat_id": chat_id,
            "user_id": _numeric_user_id(user_id),
            "client_message_id": client_message_id,
        }
        return [
            self.publish({**common, "role": "user", "content": user_text}),
            self.publish({**common, "role": "assistant", "content": assistant_text}),
        ]

    def query(self, *, after: int = 0, user_id: int | None = None) -> dict[str, Any]:
        with self._lock:
            events = [
                dict(event)
                for event in self._events
                if event["id"] > after
                and (user_id is None or event["user_id"] == user_id)
            ]
        return {"events": events, "last_id": events[-1]["id"] if events else after}

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        events: list[dict[str, Any]] = []
        with self.path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                    events.append(self._normalize_stored_event(payload))
                except (json.JSONDecodeError, TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Invalid xiaomiao event at {self.path}:{line_number}: {exc}"
                    ) from exc
        return events

    def _normalize_stored_event(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("event must be a JSON object")
        event = self._normalize_new_event(payload)
        event["id"] = int(payload["id"])
        event["timestamp"] = int(payload["timestamp"])
        event["message_id"] = str(payload.get("message_id") or _message_id(event))
        return event

    def _normalize_new_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        role = _required_text(payload, "role")
        if role not in EVENT_ROLES:
            raise ValueError("role must be user or assistant")
        channel = _optional_text(payload, "channel") or _required_text(payload, "source")
        chat_id = _required_text(payload, "chat_id")
        event: dict[str, Any] = {
            "schema_version": EVENT_SCHEMA_VERSION,
            "conversation_id": f"{channel}:{chat_id}",
            "source": _required_text(payload, "source"),
            "channel": channel,
            "chat_id": chat_id,
            "user_id": _numeric_user_id(payload.get("user_id")),
            "role": role,
            "content": _required_text(payload, "content"),
            "timestamp": int(payload.get("timestamp") or time.time()),
        }
        for field in EVENT_METADATA_FIELDS:
            value = _optional_text(payload, field)
            if value is not None:
                event[field] = value
        return event


class UnifiedConfigRepository:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_unified_config_path()
        self._lock = RLock()

    def status(self) -> dict[str, Any]:
        with self._lock:
            return _config_status(self._load())

    def update_custom_provider(self, payload: dict[str, Any]) -> dict[str, Any]:
        api_key = _required_text(payload, "apiKey")
        base_url = _absolute_http_url(payload, "baseUrl")
        model = _required_text(payload, "model")
        with self._lock:
            config = self._load()
            agent = _dict_section(config.get("xiaomiaoAgent"), "xiaomiaoAgent")
            providers = _dict_section(agent.get("providers"), "xiaomiaoAgent.providers")
            custom = _dict_section(providers.get("custom"), "xiaomiaoAgent.providers.custom")
            custom.update({"apiKey": api_key, "baseUrl": base_url})
            providers["custom"] = custom
            agent.update({"provider": "custom", "model": model, "providers": providers})
            config["xiaomiaoAgent"] = agent
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(config, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return _config_status(config)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Unified config must be a JSON object")
        return payload


def _config_status(config: dict[str, Any]) -> dict[str, Any]:
    agent = _dict_section(config.get("xiaomiaoAgent"), "xiaomiaoAgent")
    providers = _dict_section(agent.get("providers"), "xiaomiaoAgent.providers")
    custom = _dict_section(providers.get("custom"), "xiaomiaoAgent.providers.custom")
    provider = _optional_text(agent, "provider") or ""
    model = _optional_text(agent, "model") or ""
    base_url = _optional_text(custom, "baseUrl") or ""
    has_api_key = bool(_optional_text(custom, "apiKey"))
    return {
        "ok": True,
        "configured": provider == "custom" and bool(model and base_url and has_api_key),
        "provider": provider,
        "model": model,
        "baseUrl": base_url,
        "hasApiKey": has_api_key,
    }


def _required_text(payload: dict[str, Any], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _optional_text(payload: dict[str, Any], name: str) -> str | None:
    value = payload.get(name)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _numeric_user_id(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _message_id(event: dict[str, Any]) -> str:
    client_message_id = event.get("client_message_id")
    if client_message_id:
        return f"client:{client_message_id}:{event['role']}"
    return f"event:{event['id']}"


def _dict_section(value: Any, name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return dict(value)


def _absolute_http_url(payload: dict[str, Any], name: str) -> str:
    value = _required_text(payload, name)
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{name} must be an absolute http(s) URL")
    return value
