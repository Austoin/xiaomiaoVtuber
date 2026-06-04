import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import RLock
from typing import Callable
from urllib.parse import parse_qs, urlparse

from bridge_event_store import append_bridge_event, load_bridge_events
from unified_config import load_xiaomiao_agent_config_status, save_xiaomiao_agent_custom_config


LATEST_STATE_BY_USER = {}
BRIDGE_EVENTS = []
NEXT_EVENT_ID = 1
BRIDGE_LOCK = RLock()
FIRST_EVENT_ID = 1
VALID_EVENT_ROLES = {"user", "assistant"}


def reset_bridge_state() -> None:
    global NEXT_EVENT_ID
    with BRIDGE_LOCK:
        LATEST_STATE_BY_USER.clear()
        BRIDGE_EVENTS.clear()
        NEXT_EVENT_ID = FIRST_EVENT_ID


def load_persisted_bridge_events() -> None:
    global NEXT_EVENT_ID
    with BRIDGE_LOCK:
        if BRIDGE_EVENTS:
            return
        events = load_bridge_events()
        BRIDGE_EVENTS.extend(events)
        _rebuild_latest_state(events)
        NEXT_EVENT_ID = _next_event_id(events)


def _next_event_id(events: list[dict]) -> int:
    if not events:
        return FIRST_EVENT_ID
    return max(event["id"] for event in events) + 1


def _rebuild_latest_state(events: list[dict]) -> None:
    for event in events:
        if event["role"] != "assistant":
            continue
        LATEST_STATE_BY_USER[event["user_id"]] = {
            "user_id": event["user_id"],
            "reply_text": event["content"],
            "timestamp": event["timestamp"],
        }


def extract_last_user_text(messages) -> str:
    for message in reversed(messages or []):
        if message.get("role") != "user":
            continue
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = [
                item.get("text", "") for item in content if item.get("type") == "text"
            ]
            return "\n".join(part for part in text_parts if part)
    return ""


def build_models_response(model_name: str) -> dict:
    return {
        "object": "list",
        "data": [{"id": model_name, "object": "model", "owned_by": "xiaomiao"}],
    }


def build_status_response(model_name: str, default_user_id: int) -> dict:
    return {
        "ok": True,
        "service": "xiaomiao-desktop-bridge",
        "model": model_name,
        "default_user_id": default_user_id,
    }


def build_chat_response(model_name: str, content: str) -> dict:
    now = int(time.time())
    return {
        "id": f"chatcmpl-{now}",
        "object": "chat.completion",
        "created": now,
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }


def publish_desktop_state(user_id: int, reply_text: str) -> None:
    with BRIDGE_LOCK:
        LATEST_STATE_BY_USER[user_id] = {
            "user_id": user_id,
            "reply_text": reply_text,
            "timestamp": int(time.time()),
        }


def publish_bridge_event(
    *,
    source: str,
    channel: str,
    chat_id: str,
    user_id: int,
    role: str,
    content: str,
) -> dict:
    global NEXT_EVENT_ID
    with BRIDGE_LOCK:
        event = {
            "id": NEXT_EVENT_ID,
            "source": source,
            "channel": channel,
            "chat_id": str(chat_id),
            "user_id": int(user_id),
            "role": role,
            "content": str(content or ""),
            "timestamp": int(time.time()),
        }
        append_bridge_event(event)
        NEXT_EVENT_ID += 1
        BRIDGE_EVENTS.append(event)
        return dict(event)


def publish_bridge_exchange(
    *,
    source: str,
    channel: str,
    chat_id: str,
    user_id: int,
    user_text: str,
    assistant_text: str,
) -> list[dict]:
    events = [
        publish_bridge_event(
            source=source,
            channel=channel,
            chat_id=chat_id,
            user_id=user_id,
            role="user",
            content=user_text,
        ),
        publish_bridge_event(
            source=source,
            channel=channel,
            chat_id=chat_id,
            user_id=user_id,
            role="assistant",
            content=assistant_text,
        ),
    ]
    publish_desktop_state(user_id, assistant_text)
    return events


def publish_local_bridge_event(payload: dict, default_user_id: int) -> dict:
    role = required_payload_text(payload, "role")
    if role not in VALID_EVENT_ROLES:
        raise ValueError("role must be user or assistant")
    return publish_bridge_event(
        source=optional_payload_text(payload, "source", "agent-webui"),
        channel=optional_payload_text(payload, "channel", "agent-webui"),
        chat_id=optional_payload_text(payload, "chat_id", "xiaomiao-unified"),
        user_id=parse_payload_int(payload, "user_id", default_user_id),
        role=role,
        content=required_payload_text(payload, "content"),
    )


def required_payload_text(payload: dict, name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def optional_payload_text(payload: dict, name: str, default: str) -> str:
    value = payload.get(name)
    if value is None:
        return default
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def parse_payload_int(payload: dict, name: str, default: int) -> int:
    if name not in payload:
        return default
    try:
        return int(payload[name])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc


def query_bridge_events(*, after: int = 0, user_id: int | None = None) -> list[dict]:
    with BRIDGE_LOCK:
        return [
            dict(event)
            for event in BRIDGE_EVENTS
            if event["id"] > after and (user_id is None or event["user_id"] == user_id)
        ]


def build_events_response(*, after: int = 0, user_id: int | None = None) -> dict:
    events = query_bridge_events(after=after, user_id=user_id)
    return {
        "events": events,
        "last_id": events[-1]["id"] if events else after,
    }


def parse_int_query(query: dict, name: str, default: int) -> int:
    raw_value = query.get(name, [str(default)])[0]
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def parse_optional_int_query(query: dict, name: str) -> int | None:
    if name not in query:
        return None
    return parse_int_query(query, name, 0)


def start_desktop_bridge_server(
    host: str,
    port: int,
    default_user_id: int,
    model_name: str,
    reply_callback: Callable[[int, str], str],
) -> ThreadingHTTPServer:
    load_persisted_bridge_events()

    class DesktopBridgeHandler(BaseHTTPRequestHandler):
        def _set_cors_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                (
                    "Content-Type, X-XiaoMiao-User-Id, X-XiaoMiao-Source, "
                    "X-XiaoMiao-Channel, X-XiaoMiao-Chat-Id"
                ),
            )
            self.send_header("Access-Control-Allow-Private-Network", "true")

        def _write_json(self, status: int, payload: dict):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(204)
            self._set_cors_headers()
            self.end_headers()

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/v1/models":
                self._write_json(200, build_models_response(model_name))
                return
            if parsed.path == "/v1/xiaomiao/status":
                self._write_json(200, build_status_response(model_name, default_user_id))
                return
            if parsed.path == "/v1/xiaomiao/config":
                self._write_config_status()
                return
            if parsed.path == "/v1/xiaomiao/state":
                query = parse_qs(parsed.query)
                user_id = int(query.get("user_id", [str(default_user_id)])[0])
                self._write_json(
                    200,
                    LATEST_STATE_BY_USER.get(
                        user_id,
                        {"user_id": user_id, "reply_text": "", "timestamp": 0},
                    ),
                )
                return
            if parsed.path == "/v1/xiaomiao/events":
                query = parse_qs(parsed.query)
                try:
                    after = parse_int_query(query, "after", 0)
                    user_id = parse_optional_int_query(query, "user_id")
                except ValueError as exc:
                    self._write_json(400, {"error": "bad_request", "message": str(exc)})
                    return
                self._write_json(
                    200,
                    build_events_response(after=after, user_id=user_id),
                )
                return
            self._write_json(404, {"error": "not_found"})

        def do_POST(self):
            parsed_path = urlparse(self.path).path
            if parsed_path == "/v1/xiaomiao/config":
                self._write_config_update()
                return
            if parsed_path == "/v1/xiaomiao/events":
                self._write_event_create()
                return
            if parsed_path != "/v1/chat/completions":
                self._write_json(404, {"error": "not_found"})
                return

            self._write_chat_completion()

        def _read_json_payload(self) -> dict:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length) or b"{}")
            if not isinstance(payload, dict):
                raise ValueError("request body must be a JSON object")
            return payload

        def _write_config_status(self):
            try:
                self._write_json(200, load_xiaomiao_agent_config_status())
            except Exception as exc:
                self._write_json(500, {"error": "config_read_failed", "message": str(exc)})

        def _write_config_update(self):
            try:
                payload = self._read_json_payload()
                self._write_json(200, save_xiaomiao_agent_custom_config(payload))
            except ValueError as exc:
                self._write_json(400, {"error": "bad_request", "message": str(exc)})
            except Exception as exc:
                self._write_json(500, {"error": "config_write_failed", "message": str(exc)})

        def _write_event_create(self):
            try:
                payload = self._read_json_payload()
                event = publish_local_bridge_event(payload, default_user_id)
                self._write_json(200, {"event": event})
            except ValueError as exc:
                self._write_json(400, {"error": "bad_request", "message": str(exc)})
            except Exception as exc:
                self._write_json(500, {"error": "event_write_failed", "message": str(exc)})

        def _write_chat_completion(self):
            try:
                payload = self._read_json_payload()
            except ValueError as exc:
                self._write_json(400, {"error": "bad_request", "message": str(exc)})
                return

            user_id = int(self.headers.get("X-XiaoMiao-User-Id", str(default_user_id)))
            source = self.headers.get("X-XiaoMiao-Source", "web")
            channel = self.headers.get("X-XiaoMiao-Channel", source)
            chat_id = self.headers.get("X-XiaoMiao-Chat-Id", "stage-web")
            message_text = extract_last_user_text(payload.get("messages", []))
            try:
                reply_text = reply_callback(user_id, message_text)
            except Exception as exc:
                self._write_json(
                    502,
                    {
                        "error": "reply_failed",
                        "message": str(exc),
                    },
                )
                return
            publish_bridge_exchange(
                source=source,
                channel=channel,
                chat_id=chat_id,
                user_id=user_id,
                user_text=message_text,
                assistant_text=reply_text,
            )
            self._write_json(
                200, build_chat_response(payload.get("model") or model_name, reply_text)
            )

        def log_message(self, format, *args):
            return

    return ThreadingHTTPServer((host, port), DesktopBridgeHandler)
