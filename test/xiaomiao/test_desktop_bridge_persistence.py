import os
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
