import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from qq_agent_bridge import (  # noqa: E402
    QQ_AGENT_GROUP,
    QQ_AGENT_PRIVATE,
    build_agent_media_from_urls,
    build_qq_agent_reply,
    get_market_face_url,
    is_qq_exact_command,
    publish_qq_agent_reply,
    resolve_qq_image_url,
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


if __name__ == "__main__":
    unittest.main()
