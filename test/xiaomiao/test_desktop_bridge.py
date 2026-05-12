import json
import sys
import threading
import time
import unittest
from pathlib import Path
from urllib import request

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from desktop_bridge import extract_last_user_text, start_desktop_bridge_server


class DesktopBridgeTests(unittest.TestCase):
    def test_extract_last_user_text_prefers_latest_user_message(self):
        payload = [
            {"role": "system", "content": "ignore"},
            {"role": "user", "content": "第一句"},
            {"role": "assistant", "content": "回复"},
            {"role": "user", "content": [{"type": "text", "text": "最后一句"}]},
        ]

        self.assertEqual(extract_last_user_text(payload), "最后一句")

    def test_openai_compatible_routes_return_models_and_reply(self):
        server = start_desktop_bridge_server(
            host="127.0.0.1",
            port=0,
            default_user_id=3554978979,
            model_name="deepseek-chat",
            reply_callback=lambda user_id, text: f"{user_id}:{text}",
        )

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            time.sleep(0.1)
            port = server.server_address[1]

            models_response = request.urlopen(f"http://127.0.0.1:{port}/v1/models")
            models_json = json.loads(models_response.read().decode("utf-8"))
            self.assertEqual(models_json["data"][0]["id"], "deepseek-chat")

            body = json.dumps(
                {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "你好"}],
                }
            ).encode("utf-8")
            chat_request = request.Request(
                f"http://127.0.0.1:{port}/v1/chat/completions",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            chat_response = request.urlopen(chat_request)
            chat_json = json.loads(chat_response.read().decode("utf-8"))

            self.assertEqual(
                chat_json["choices"][0]["message"]["content"],
                "3554978979:你好",
            )

            state_response = request.urlopen(
                f"http://127.0.0.1:{port}/v1/xiaomiao/state?user_id=3554978979"
            )
            state_json = json.loads(state_response.read().decode("utf-8"))
            self.assertEqual(state_json["reply_text"], "3554978979:你好")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def test_bridge_supports_cors_preflight_and_headers(self):
        server = start_desktop_bridge_server(
            host="127.0.0.1",
            port=0,
            default_user_id=3554978979,
            model_name="deepseek-chat",
            reply_callback=lambda user_id, text: text,
        )

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            time.sleep(0.1)
            port = server.server_address[1]

            preflight = request.Request(
                f"http://127.0.0.1:{port}/v1/xiaomiao/state?user_id=3554978979",
                method="OPTIONS",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Content-Type,X-XiaoMiao-User-Id",
                    "Access-Control-Request-Private-Network": "true",
                },
            )
            response = request.urlopen(preflight)

            self.assertEqual(response.status, 204)
            self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")
            self.assertIn(
                "GET", response.headers.get("Access-Control-Allow-Methods", "")
            )
            self.assertIn(
                "X-XiaoMiao-User-Id",
                response.headers.get("Access-Control-Allow-Headers", ""),
            )
            self.assertEqual(
                response.headers.get("Access-Control-Allow-Private-Network"), "true"
            )

            models_response = request.urlopen(f"http://127.0.0.1:{port}/v1/models")
            self.assertEqual(
                models_response.headers.get("Access-Control-Allow-Origin"), "*"
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def test_status_route_returns_bridge_runtime_state(self):
        server = start_desktop_bridge_server(
            host="127.0.0.1",
            port=0,
            default_user_id=3554978979,
            model_name="deepseek-chat",
            reply_callback=lambda user_id, text: text,
        )

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            time.sleep(0.1)
            port = server.server_address[1]

            status_response = request.urlopen(
                f"http://127.0.0.1:{port}/v1/xiaomiao/status"
            )
            status_json = json.loads(status_response.read().decode("utf-8"))

            self.assertEqual(
                status_json,
                {
                    "ok": True,
                    "service": "xiaomiao-desktop-bridge",
                    "model": "deepseek-chat",
                    "default_user_id": 3554978979,
                },
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)


if __name__ == "__main__":
    unittest.main()
