"""Tests for atomic session save and corrupt-file repair."""

import json
from datetime import datetime
from pathlib import Path

from nanobot.session.manager import Session, SessionManager


class TestAtomicSave:
    def test_save_creates_valid_jsonl(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        session = Session(key="test:1")
        session.add_message("user", "hello")
        session.add_message("assistant", "hi")

        mgr.save(session)

        path = mgr._get_session_path("test:1")
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3

        meta = json.loads(lines[0])
        assert meta["_type"] == "metadata"
        assert meta["key"] == "test:1"

        msg1 = json.loads(lines[1])
        assert msg1["role"] == "user"
        assert msg1["content"] == "hello"

    def test_no_tmp_file_left_after_successful_save(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        session = Session(key="test:clean")
        mgr.save(session)

        tmp_files = list(mgr.sessions_dir.glob("*.tmp"))
        assert tmp_files == []

    def test_tmp_file_cleaned_up_on_write_failure(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        session = Session(key="test:fail")
        path = mgr._get_session_path("test:fail")
        tmp_path_file = path.with_suffix(".jsonl.tmp")

        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path_file.write_text("stale")

        class BadMessage:
            def __init__(self, data):
                self.data = data

        original_dumps = json.dumps

        def failing_dumps(obj, **kwargs):
            if isinstance(obj, dict) and obj.get("role") == "assistant":
                raise OSError("simulated disk full")
            return original_dumps(obj, **kwargs)

        session = Session(key="test:fail")
        session.messages = [
            {"role": "user", "content": "ok"},
            {"role": "assistant", "content": "will fail"},
        ]

        import unittest.mock
        with unittest.mock.patch("nanobot.session.manager.json.dumps", side_effect=failing_dumps):
            try:
                mgr.save(session)
            except OSError:
                pass

        assert not tmp_path_file.exists()

    def test_overwrite_preserves_latest_data(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        session = Session(key="test:overwrite")

        session.add_message("user", "first")
        mgr.save(session)

        session.add_message("user", "second")
        mgr.save(session)

        mgr.invalidate("test:overwrite")
        loaded = mgr.get_or_create("test:overwrite")
        assert len(loaded.messages) == 2
        assert loaded.messages[0]["content"] == "first"
        assert loaded.messages[1]["content"] == "second"

    def test_consecutive_saves_are_consistent(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        session = Session(key="test:consistency")

        for i in range(5):
            session.add_message("user", f"msg{i}")
            mgr.save(session)

        mgr.invalidate("test:consistency")
        loaded = mgr.get_or_create("test:consistency")
        assert len(loaded.messages) == 5
        for i in range(5):
            assert loaded.messages[i]["content"] == f"msg{i}"

    def test_stale_cached_save_preserves_messages_from_another_manager(self, tmp_path: Path):
        manager_a = SessionManager(tmp_path)
        manager_b = SessionManager(tmp_path)

        stale_session = manager_a.get_or_create("api:xiaomiao-unified")
        stale_session.add_message("user", "from-a-1")
        manager_a.save(stale_session)

        concurrent_session = manager_b.get_or_create("api:xiaomiao-unified")
        concurrent_session.add_message("assistant", "from-b-1")
        manager_b.save(concurrent_session)

        stale_session.add_message("user", "from-a-2")
        manager_a.save(stale_session)

        loaded = SessionManager(tmp_path).get_or_create("api:xiaomiao-unified")
        assert [msg["content"] for msg in loaded.messages] == [
            "from-a-1",
            "from-b-1",
            "from-a-2",
        ]

    def test_empty_save_still_clears_existing_session_file(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        session = mgr.get_or_create("api:xiaomiao-unified")
        session.add_message("user", "old-message")
        mgr.save(session)

        session.clear()
        mgr.save(session)

        loaded = SessionManager(tmp_path).get_or_create("api:xiaomiao-unified")
        assert loaded.messages == []

    def test_replace_save_drops_archived_disk_prefix(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        session = mgr.get_or_create("api:xiaomiao-unified")
        for content in ("old-1", "old-2", "recent-1", "recent-2"):
            session.add_message("user", content)
        mgr.save(session)

        session.messages = session.messages[-2:]
        mgr.save(session, merge_disk=False)

        loaded = SessionManager(tmp_path).get_or_create("api:xiaomiao-unified")
        assert [msg["content"] for msg in loaded.messages] == ["recent-1", "recent-2"]

    def test_merged_save_keeps_advanced_consolidation_cursor(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        session = mgr.get_or_create("api:xiaomiao-unified")
        session.add_message("user", "archived")
        session.add_message("assistant", "recent")
        mgr.save(session)

        session.last_consolidated = 1
        mgr.save(session)

        loaded = SessionManager(tmp_path).get_or_create("api:xiaomiao-unified")
        assert loaded.last_consolidated == 1


class TestRepairCorruptFile:
    def _write_corrupt_jsonl(self, path: Path, lines: list[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_truncated_last_line_recovered(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        path = mgr._get_session_path("test:trunc")

        valid_meta = json.dumps({
            "_type": "metadata",
            "key": "test:trunc",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {},
            "last_consolidated": 0,
        })
        valid_msg = json.dumps({"role": "user", "content": "hello"})

        self._write_corrupt_jsonl(path, [
            valid_meta,
            valid_msg,
            '{"role": "assistant", "content": "partial...',
        ])

        session = mgr._load("test:trunc")
        assert session is not None
        assert len(session.messages) == 1
        assert session.messages[0]["content"] == "hello"

    def test_corrupt_metadata_line_skipped(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        path = mgr._get_session_path("test:badmeta")

        self._write_corrupt_jsonl(path, [
            "NOT VALID JSON!!!",
            '{"role": "user", "content": "survived"}',
        ])

        session = mgr._load("test:badmeta")
        assert session is not None
        assert len(session.messages) == 1
        assert session.messages[0]["content"] == "survived"

    def test_all_corrupt_lines_returns_none(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        path = mgr._get_session_path("test:allbad")

        self._write_corrupt_jsonl(path, [
            "garbage line 1",
            "garbage line 2",
            "{{invalid json",
        ])

        session = mgr._load("test:allbad")
        assert session is None

    def test_empty_file_returns_empty_session(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        path = mgr._get_session_path("test:empty")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

        session = mgr._load("test:empty")
        assert session is not None
        assert session.messages == []
        assert session.key == "test:empty"

    def test_repair_preserves_valid_messages_amid_corruption(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        path = mgr._get_session_path("test:mixed")

        self._write_corrupt_jsonl(path, [
            json.dumps({"_type": "metadata", "key": "test:mixed",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "metadata": {}, "last_consolidated": 0}),
            "BROKEN",
            json.dumps({"role": "user", "content": "msg1"}),
            '{"role": "assistant", "content": "broken',
            json.dumps({"role": "user", "content": "msg2"}),
        ])

        session = mgr._load("test:mixed")
        assert session is not None
        assert len(session.messages) == 2
        assert session.messages[0]["content"] == "msg1"
        assert session.messages[1]["content"] == "msg2"

    def test_repair_with_bad_timestamp_uses_fallback(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        path = mgr._get_session_path("test:badts")

        self._write_corrupt_jsonl(path, [
            json.dumps({"_type": "metadata", "key": "test:badts",
                        "created_at": "not-a-date",
                        "updated_at": "also-bad",
                        "metadata": {}, "last_consolidated": 5}),
            json.dumps({"role": "user", "content": "hi"}),
        ])

        session = mgr._load("test:badts")
        assert session is not None
        assert session.last_consolidated == 5
        assert isinstance(session.created_at, datetime)

    def test_read_session_file_repairs_corrupt_jsonl(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        path = mgr._get_session_path("test:read-repair")

        self._write_corrupt_jsonl(path, [
            json.dumps({
                "_type": "metadata",
                "key": "test:read-repair",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "metadata": {"source": "repair"},
                "last_consolidated": 0,
            }),
            json.dumps({"role": "user", "content": "survived"}),
            '{"role": "assistant", "content": "partial...',
        ])

        payload = mgr.read_session_file("test:read-repair")
        assert payload is not None
        assert payload["key"] == "test:read-repair"
        assert payload["metadata"] == {"source": "repair"}
        assert payload["messages"] == [{"role": "user", "content": "survived"}]

    def test_list_sessions_keeps_repaired_corrupt_file(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        path = mgr._get_session_path("test:list-repair")

        self._write_corrupt_jsonl(path, [
            "NOT VALID JSON",
            json.dumps({
                "_type": "metadata",
                "key": "test:list-repair",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "metadata": {},
                "last_consolidated": 0,
            }),
            json.dumps({"role": "user", "content": "hello"}),
        ])

        sessions = mgr.list_sessions()
        assert any(s["key"] == "test:list-repair" for s in sessions)

    def test_get_or_create_returns_new_session_for_corrupt_file(self, tmp_path: Path):
        mgr = SessionManager(tmp_path)
        path = mgr._get_session_path("test:fallback")

        self._write_corrupt_jsonl(path, ["{{{{"])

        session = mgr.get_or_create("test:fallback")
        assert session is not None
        assert session.messages == []
        assert session.key == "test:fallback"
