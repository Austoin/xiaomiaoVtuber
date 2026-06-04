import os
import json
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path
from urllib import request

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from desktop_bridge import (
    publish_bridge_exchange,
    reset_bridge_state,
    start_desktop_bridge_server,
)

DEFAULT_USER_ID = 3554978979
MODEL_NAME = "deepseek-chat"


class DesktopBridgePersistenceTests(unittest.TestCase):
    def setUp(self):
        reset_bridge_state()

    def tearDown(self):
        reset_bridge_state()
        os.environ.pop("XIAOMIAO_BRIDGE_EVENT_STORE", None)

    def test_bridge_events_reload_from_local_store_on_startup(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.environ["XIAOMIAO_BRIDGE_EVENT_STORE"] = str(
                Path(tmp_dir) / "bridge_events.jsonl"
            )
            publish_bridge_exchange(
                source="qq-private",
                channel="qq-private",
                chat_id="42",
                user_id=42,
                user_text="重启前问题",
                assistant_text="重启前回答",
            )
            reset_bridge_state()

            with _bridge_server() as port:
                body = _json_get(
                    f"http://127.0.0.1:{port}/v1/xiaomiao/events?user_id=42"
                )

        self.assertEqual(body["last_id"], 2)
        self.assertEqual([item["content"] for item in body["events"]], ["重启前问题", "重启前回答"])
        self.assertEqual(body["events"][0]["schema_version"], 1)
        self.assertEqual(body["events"][0]["conversation_id"], "qq-private:42")
        self.assertEqual(body["events"][0]["message_id"], "bridge:1")

    def test_bridge_events_preserve_client_message_id_after_reload(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.environ["XIAOMIAO_BRIDGE_EVENT_STORE"] = str(
                Path(tmp_dir) / "bridge_events.jsonl"
            )
            publish_bridge_exchange(
                source="web",
                channel="web",
                chat_id="stage-web",
                user_id=42,
                user_text="带客户端消息的问题",
                assistant_text="带客户端消息的回答",
                client_message_id="stage-web-local-1",
            )
            reset_bridge_state()

            with _bridge_server() as port:
                body = _json_get(
                    f"http://127.0.0.1:{port}/v1/xiaomiao/events?user_id=42"
                )

        self.assertEqual(body["last_id"], 2)
        self.assertEqual(
            [item["client_message_id"] for item in body["events"]],
            ["stage-web-local-1", "stage-web-local-1"],
        )

    def test_bridge_events_isolate_invalid_persisted_lines(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            event_store = Path(tmp_dir) / "bridge_events.jsonl"
            os.environ["XIAOMIAO_BRIDGE_EVENT_STORE"] = str(event_store)
            event_store.write_text(
                "\n".join([
                    json.dumps({
                        "id": 1,
                        "source": "qq-private",
                        "channel": "qq-private",
                        "chat_id": "42",
                        "user_id": 42,
                        "role": "user",
                        "content": "有效问题",
                        "timestamp": 1780399501,
                    }, ensure_ascii=False),
                    "{bad json",
                    json.dumps({
                        "id": 2,
                        "source": "qq-private",
                        "channel": "qq-private",
                        "chat_id": "42",
                        "user_id": 42,
                        "role": "assistant",
                        "content": "有效回答",
                        "timestamp": 1780399502,
                    }, ensure_ascii=False),
                ]),
                encoding="utf-8",
            )

            with _bridge_server() as port:
                body = _json_get(
                    f"http://127.0.0.1:{port}/v1/xiaomiao/events?user_id=42"
                )

            invalid_store = event_store.with_suffix(".invalid.jsonl")
            invalid_exists = invalid_store.exists()

        self.assertEqual(body["last_id"], 2)
        self.assertEqual([item["content"] for item in body["events"]], ["有效问题", "有效回答"])
        self.assertTrue(invalid_exists)

    def test_local_event_post_writes_bridge_event_without_agent_reply(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.environ["XIAOMIAO_BRIDGE_EVENT_STORE"] = str(
                Path(tmp_dir) / "bridge_events.jsonl"
            )
            with _bridge_server() as port:
                created = _json_post(
                    f"http://127.0.0.1:{port}/v1/xiaomiao/events",
                    {
                        "source": "agent-webui",
                        "channel": "agent-webui",
                        "chat_id": "xiaomiao-unified",
                        "role": "user",
                        "content": "Agent 端发言",
                    },
                )
                body = _json_get(
                    f"http://127.0.0.1:{port}/v1/xiaomiao/events?user_id={DEFAULT_USER_ID}"
                )

        self.assertEqual(created["event"]["id"], 1)
        self.assertEqual(body["last_id"], 1)
        self.assertEqual(body["events"][0]["source"], "agent-webui")
        self.assertEqual(body["events"][0]["content"], "Agent 端发言")


@contextmanager
def _bridge_server(reply_callback=None):
    callback = reply_callback or (lambda user_id, text: f"{user_id}:{text}")
    server = start_desktop_bridge_server(
        "127.0.0.1",
        0,
        DEFAULT_USER_ID,
        MODEL_NAME,
        callback,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1.0)


def _json_get(url: str) -> dict:
    with request.urlopen(url) as response:
        import json

        return json.loads(response.read().decode("utf-8"))


def _json_post(url: str, payload: dict) -> dict:
    import json

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))
