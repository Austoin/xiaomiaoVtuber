import json
import os
from pathlib import Path
from typing import Any

BRIDGE_EVENT_STORE_ENV = "XIAOMIAO_BRIDGE_EVENT_STORE"
DEFAULT_BRIDGE_EVENT_STORE = Path(__file__).resolve().parent / "runtime" / "bridge_events.jsonl"
REQUIRED_EVENT_FIELDS = ("id", "source", "channel", "chat_id", "user_id", "role", "content", "timestamp")
BRIDGE_EVENT_SCHEMA_VERSION = 1


def bridge_event_store_path() -> Path:
    configured = os.environ.get(BRIDGE_EVENT_STORE_ENV)
    return Path(configured) if configured else DEFAULT_BRIDGE_EVENT_STORE


def append_bridge_event(event: dict[str, Any]) -> None:
    path = bridge_event_store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
        file.write("\n")


def complete_bridge_event(event: dict[str, Any]) -> dict[str, Any]:
    next_event = dict(event)
    next_event["schema_version"] = int(
        next_event.get("schema_version") or BRIDGE_EVENT_SCHEMA_VERSION
    )
    next_event["conversation_id"] = str(
        next_event.get("conversation_id")
        or _build_conversation_id(next_event["channel"], next_event["chat_id"])
    )
    next_event["message_id"] = str(
        next_event.get("message_id") or _build_message_id(next_event)
    )
    return next_event


def load_bridge_events() -> list[dict[str, Any]]:
    path = bridge_event_store_path()
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
            text = line.strip()
            if not text:
                continue
            try:
                raw_event = json.loads(text)
                events.append(_normalize_event(raw_event, line_number))
            except (json.JSONDecodeError, ValueError) as exc:
                _append_invalid_event_line(path, line_number, text, str(exc))
    return events


def _append_invalid_event_line(
    source_path: Path,
    line_number: int,
    line_text: str,
    error_text: str,
) -> None:
    invalid_path = source_path.with_suffix(".invalid.jsonl")
    invalid_record = {
        "source": str(source_path),
        "line_number": line_number,
        "line": line_text,
        "error": error_text,
    }
    with invalid_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(invalid_record, ensure_ascii=False, separators=(",", ":")))
        file.write("\n")


def _normalize_event(raw_event: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(raw_event, dict):
        raise ValueError(f"bridge event line {line_number} must be an object")
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in raw_event]
    if missing:
        raise ValueError(f"bridge event line {line_number} missing fields: {', '.join(missing)}")
    event = {
        "id": int(raw_event["id"]),
        "source": str(raw_event["source"]),
        "channel": str(raw_event["channel"]),
        "chat_id": str(raw_event["chat_id"]),
        "user_id": int(raw_event["user_id"]),
        "role": str(raw_event["role"]),
        "content": str(raw_event["content"]),
        "timestamp": int(raw_event["timestamp"]),
    }
    client_message_id = raw_event.get("client_message_id")
    if client_message_id is not None:
        event["client_message_id"] = str(client_message_id)
    return complete_bridge_event(event)


def _build_conversation_id(channel: Any, chat_id: Any) -> str:
    return f"{channel}:{chat_id}"


def _build_message_id(event: dict[str, Any]) -> str:
    client_message_id = event.get("client_message_id")
    if client_message_id:
        return f"client:{client_message_id}:{event['role']}"
    return f"bridge:{event['id']}"
