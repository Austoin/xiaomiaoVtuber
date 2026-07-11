import asyncio
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from qq_agent_bridge import (  # noqa: E402
    QQ_AGENT_GROUP,
    QQ_AGENT_PRIVATE,
    await_agent_reply_with_wait_notice,
    build_agent_media_from_urls,
    build_qq_agent_reply,
    get_qq_command_args,
    get_market_face_url,
    is_qq_command_alias,
    is_qq_exact_command,
    map_qq_memory_command,
    publish_qq_agent_reply,
    resolve_qq_image_url,
    should_private_message_enter_agent,
)


class QQAgentBridgeTests(unittest.TestCase):
    def test_group_turn_uses_group_source_and_media(self):
        calls = []
        bridge_events = []

        def reply_callback(user_id, channel, chat_id, text, media=()):
            calls.append((user_id, channel, chat_id, text, media))
            return "agent reply"

        result = build_qq_agent_reply(
            source=QQ_AGENT_GROUP,
            user_id=3554978979,
            chat_id=10001,
            text="hello",
            media=("data:image/jpeg;base64,AAA=",),
            reply_callback=reply_callback,
        )
        publish_qq_agent_reply(result, lambda **kwargs: bridge_events.append(kwargs))

        self.assertEqual(result.assistant_text, "agent reply")
        self.assertEqual(
            calls,
            [
                (
                    3554978979,
                    "qq-group",
                    "10001",
                    "hello",
                    ("data:image/jpeg;base64,AAA=",),
                )
            ],
        )
        self.assertEqual(
            bridge_events,
            [
                {
                    "source": "qq-group",
                    "channel": "qq-group",
                    "chat_id": "10001",
                    "user_id": 3554978979,
                    "user_text": "hello",
                    "assistant_text": "agent reply",
                }
            ],
        )

    def test_agent_tool_events_are_published_as_bridge_events(self):
        bridge_exchanges = []
        tool_events = []

        @dataclass(frozen=True)
        class Response:
            assistant_text: str
            tool_events: tuple[dict[str, Any], ...]

        def reply_callback(*_args, **_kwargs):
            return Response(
                assistant_text="queued",
                tool_events=(
                    {
                        "event_type": "tool_start",
                        "tool_name": "xiaomiaobot_action",
                        "risk_level": "high",
                        "confirmation_id": "ABC123",
                        "result_summary": "homeassistant:control",
                    },
                ),
            )

        result = build_qq_agent_reply(
            source=QQ_AGENT_GROUP,
            user_id=3554978979,
            chat_id=10001,
            text="打开台灯",
            reply_callback=reply_callback,
        )
        publish_qq_agent_reply(
            result,
            lambda **kwargs: bridge_exchanges.append(kwargs),
            lambda **kwargs: tool_events.append(kwargs),
        )

        self.assertEqual(result.assistant_text, "queued")
        self.assertEqual(len(bridge_exchanges), 1)
        self.assertEqual(bridge_exchanges[0]["assistant_text"], "queued")
        self.assertEqual(
            tool_events,
            [
                {
                    "source": "qq-group",
                    "channel": "qq-group",
                    "chat_id": "10001",
                    "user_id": 3554978979,
                    "role": "assistant",
                    "content": "homeassistant:control",
                    "event_type": "tool_start",
                    "tool_name": "xiaomiaobot_action",
                    "risk_level": "high",
                    "confirmation_id": "ABC123",
                    "result_summary": "homeassistant:control",
                }
            ],
        )

    def test_private_turn_uses_user_as_chat_id(self):
        calls = []

        def reply_callback(user_id, channel, chat_id, text, media=()):
            calls.append((user_id, channel, chat_id, text, media))
            return "private reply"

        result = build_qq_agent_reply(
            source=QQ_AGENT_PRIVATE,
            user_id=3554978979,
            chat_id=3554978979,
            text="hi",
            reply_callback=reply_callback,
        )

        self.assertEqual(result.assistant_text, "private reply")
        self.assertEqual(
            calls,
            [(3554978979, "qq-private", "3554978979", "hi", ())],
        )

    def test_empty_text_is_visible(self):
        with self.assertRaisesRegex(ValueError, "requires non-empty text"):
            build_qq_agent_reply(
                source=QQ_AGENT_GROUP,
                user_id=1,
                chat_id=2,
                text="   ",
                reply_callback=lambda *_args, **_kwargs: "unused",
            )

    def test_resolve_qq_image_url_prefers_http_file(self):
        self.assertEqual(
            resolve_qq_image_url(
                file_value="https://example.test/image.png",
                url_value="https://fallback.test/image.png",
            ),
            "https://example.test/image.png",
        )

    def test_resolve_qq_image_url_uses_url_for_local_file(self):
        self.assertEqual(
            resolve_qq_image_url(
                file_value="local-cache-id",
                url_value="https://example.test/image.png",
            ),
            "https://example.test/image.png",
        )

    def test_get_market_face_url(self):
        self.assertEqual(
            get_market_face_url("abcdef"),
            "https://gxh.vip.qq.com/club/item/parcel/item/ab/abcdef/raw300.gif",
        )

    def test_build_agent_media_from_urls_keeps_success_and_reports_failures(self):
        async def convert(url):
            if "bad" in url:
                raise RuntimeError("download failed")
            return f"media:{url}"

        media, failures = asyncio.run(
            build_agent_media_from_urls(
                ("https://ok.test/a.png", "https://bad.test/b.png"),
                convert,
            )
        )

        self.assertEqual(media, ("media:https://ok.test/a.png",))
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].url, "https://bad.test/b.png")
        self.assertIn("download failed", failures[0].error)

    def test_exact_command_does_not_match_agent_prompt_words(self):
        prompt = "在桌面agent.txt里面写入一些关于agent的知识"

        self.assertTrue(is_qq_exact_command("关于", "关于"))
        self.assertTrue(is_qq_exact_command("  帮助  ", "帮助"))
        self.assertFalse(is_qq_exact_command(prompt, "关于"))
        self.assertFalse(is_qq_exact_command("帮助我写文件", "帮助"))
        self.assertFalse(is_qq_exact_command("读图总结这张图片", "读图"))

    def test_command_alias_does_not_match_agent_prompt_words(self):
        aliases = ("关于", "about", "info")

        self.assertTrue(is_qq_command_alias("ABOUT", aliases))
        self.assertTrue(is_qq_command_alias(" info ", aliases))
        self.assertFalse(is_qq_command_alias("about this project", aliases))
        self.assertFalse(is_qq_command_alias("关于agent的知识", aliases))

    def test_prefixed_command_args_require_command_boundary(self):
        aliases = ("生图", "pic", "图片", "生成图片")

        self.assertEqual(get_qq_command_args("pic miku", aliases), "miku")
        self.assertEqual(get_qq_command_args(" 图片   白丝 ", aliases), "白丝")
        self.assertEqual(get_qq_command_args("生图", aliases), "")
        self.assertIsNone(get_qq_command_args("图片识别一下", aliases))

    def test_private_bare_text_and_media_enter_agent(self):
        self.assertTrue(
            should_private_message_enter_agent(
                order="抓取网页",
                user_message="抓取网页",
                has_document_segments=False,
                has_media_segments=False,
            )
        )
        self.assertTrue(
            should_private_message_enter_agent(
                order="",
                user_message="",
                has_document_segments=True,
                has_media_segments=False,
            )
        )
        self.assertTrue(
            should_private_message_enter_agent(
                order="",
                user_message="",
                has_document_segments=False,
                has_media_segments=True,
            )
        )
        self.assertFalse(
            should_private_message_enter_agent(
                order="",
                user_message="   ",
                has_document_segments=False,
                has_media_segments=False,
            )
        )

    def test_qq_memory_command_aliases_map_to_agent_slash_commands(self):
        self.assertEqual(map_qq_memory_command("记忆状态"), "/status")
        self.assertEqual(map_qq_memory_command("状态"), "/status")
        self.assertEqual(map_qq_memory_command("status"), "/status")
        self.assertEqual(map_qq_memory_command("STATUS"), "/status")
        self.assertEqual(map_qq_memory_command("整理记忆"), "/dream")
        self.assertEqual(map_qq_memory_command("记忆整理"), "/dream")
        self.assertEqual(map_qq_memory_command("dream"), "/dream")
        self.assertEqual(map_qq_memory_command("记忆日志"), "/dream-log")
        self.assertEqual(map_qq_memory_command("日志"), "/dream-log")
        self.assertEqual(map_qq_memory_command("记忆日志 abc123"), "/dream-log abc123")
        self.assertEqual(map_qq_memory_command("日志 abc123"), "/dream-log abc123")
        self.assertEqual(map_qq_memory_command("恢复记忆"), "/dream-restore")
        self.assertEqual(map_qq_memory_command("记忆恢复"), "/dream-restore")
        self.assertEqual(map_qq_memory_command("DREAM-RESTORE"), "/dream-restore")
        self.assertEqual(map_qq_memory_command("恢复记忆 abc123"), "/dream-restore abc123")
        self.assertEqual(map_qq_memory_command("dream-restore abc123"), "/dream-restore abc123")
        self.assertEqual(map_qq_memory_command("新会话"), "/new")
        self.assertEqual(map_qq_memory_command("new-session"), "/new")
        self.assertEqual(map_qq_memory_command("停止任务"), "/stop")
        self.assertEqual(map_qq_memory_command("停止"), "/stop")

    def test_build_qq_agent_turn_applies_memory_aliases(self):
        calls = []

        def reply_callback(user_id, channel, chat_id, text, media=()):
            calls.append((user_id, channel, chat_id, text, media))
            return "dreaming"

        result = build_qq_agent_reply(
            source=QQ_AGENT_GROUP,
            user_id=3554978979,
            chat_id=10001,
            text="整理记忆",
            reply_callback=reply_callback,
        )

        self.assertEqual(result.assistant_text, "dreaming")
        self.assertEqual(calls[0][3], "/dream")

    def test_wait_notice_is_not_sent_for_fast_agent_reply(self):
        notices = []

        async def notice():
            notices.append("waiting")

        result = asyncio.run(
            await_agent_reply_with_wait_notice(
                lambda: "done",
                notice,
                notice_after_seconds=0.1,
            )
        )

        self.assertEqual(result, "done")
        self.assertEqual(notices, [])

    def test_wait_notice_is_sent_once_before_slow_agent_reply_finishes(self):
        notices = []

        async def notice():
            notices.append("waiting")

        def slow_call():
            import time

            time.sleep(0.05)
            return "done"

        result = asyncio.run(
            await_agent_reply_with_wait_notice(
                slow_call,
                notice,
                notice_after_seconds=0.01,
            )
        )

        self.assertEqual(result, "done")
        self.assertEqual(notices, ["waiting"])


if __name__ == "__main__":
    unittest.main()
