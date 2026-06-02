import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import parse_qs, urlparse


LATEST_STATE_BY_USER = {}


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
    LATEST_STATE_BY_USER[user_id] = {
        "user_id": user_id,
        "reply_text": reply_text,
        "timestamp": int(time.time()),
    }


def start_desktop_bridge_server(
    host: str,
    port: int,
    default_user_id: int,
    model_name: str,
    reply_callback: Callable[[int, str], str],
) -> ThreadingHTTPServer:
    class DesktopBridgeHandler(BaseHTTPRequestHandler):
        def _set_cors_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type, X-XiaoMiao-User-Id",
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
            self._write_json(404, {"error": "not_found"})

        def do_POST(self):
            if urlparse(self.path).path != "/v1/chat/completions":
                self._write_json(404, {"error": "not_found"})
                return

            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length) or b"{}")
            user_id = int(self.headers.get("X-XiaoMiao-User-Id", str(default_user_id)))
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
            publish_desktop_state(user_id, reply_text)
            self._write_json(
                200, build_chat_response(payload.get("model") or model_name, reply_text)
            )

        def log_message(self, format, *args):
            return

    return ThreadingHTTPServer((host, port), DesktopBridgeHandler)
