import json
import os
from pathlib import Path
from typing import Any

BRIDGE_EVENT_STORE_ENV = "XIAOMIAO_BRIDGE_EVENT_STORE"
DEFAULT_BRIDGE_EVENT_STORE = Path(__file__).resolve().parent / "runtime" / "bridge_events.jsonl"
REQUIRED_EVENT_FIELDS = ("id", "source", "channel", "chat_id", "user_id", "role", "content", "timestamp")


def bridge_event_store_path() -> Path:
    configured = os.environ.get(BRIDGE_EVENT_STORE_ENV)
    return Path(configured) if configured else DEFAULT_BRIDGE_EVENT_STORE


def append_bridge_event(event: dict[str, Any]) -> None:
    path = bridge_event_store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
        file.write("\n")


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
            raw_event = json.loads(text)
            events.append(_normalize_event(raw_event, line_number))
    return events


def _normalize_event(raw_event: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(raw_event, dict):
        raise ValueError(f"bridge event line {line_number} must be an object")
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in raw_event]
    if missing:
        raise ValueError(f"bridge event line {line_number} missing fields: {', '.join(missing)}")
    return {
        "id": int(raw_event["id"]),
        "source": str(raw_event["source"]),
        "channel": str(raw_event["channel"]),
        "chat_id": str(raw_event["chat_id"]),
        "user_id": int(raw_event["user_id"]),
        "role": str(raw_event["role"]),
        "content": str(raw_event["content"]),
        "timestamp": int(raw_event["timestamp"]),
    }
