import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from qq_agent_tools import (  # noqa: E402
    AgentToolConfirmationStore,
    HIGH_RISK_CONFIRM_PREFIX,
    decide_agent_tool_request,
    detect_agent_tool_risk,
    parse_confirmation_command,
)


class QQAgentToolsTests(unittest.TestCase):
    def test_detect_agent_tool_risk_marks_exec_language_high(self):
        self.assertEqual(detect_agent_tool_risk("帮我在本机执行 dir"), "high")
        self.assertEqual(detect_agent_tool_risk("用 powershell 看一下目录"), "high")
        self.assertEqual(detect_agent_tool_risk("普通聊天"), "low")

    def test_detect_agent_tool_risk_marks_memory_restore_high(self):
        self.assertEqual(detect_agent_tool_risk("/dream-restore"), "high")
        self.assertEqual(detect_agent_tool_risk("恢复记忆"), "high")
        self.assertEqual(detect_agent_tool_risk("请回滚记忆到上一个版本"), "high")

    def test_parse_confirmation_command(self):
        self.assertEqual(parse_confirmation_command(f"{HIGH_RISK_CONFIRM_PREFIX} ABC123"), "ABC123")
        self.assertIsNone(parse_confirmation_command("确认 ABC123"))

    def test_high_risk_without_permission_is_rejected(self):
        decision = decide_agent_tool_request(
            text="帮我在本机执行 dir",
            user_id=1,
            chat_id=2,
            has_tool_permission=False,
            confirmation_store=AgentToolConfirmationStore(),
        )

        self.assertFalse(decision.allowed)
        self.assertIn("高风险工具权限", decision.message)

    def test_high_risk_with_permission_creates_confirmation(self):
        store = AgentToolConfirmationStore(ttl_seconds=300)
        decision = decide_agent_tool_request(
            text="帮我在本机执行 dir",
            user_id=1,
            chat_id=2,
            has_tool_permission=True,
            confirmation_store=store,
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.tool_policy, "trusted_pending")
        self.assertIsNotNone(decision.pending_request)
        self.assertIn("确认码", decision.message)

    def test_confirmation_grants_trusted_confirmed_once(self):
        store = AgentToolConfirmationStore(ttl_seconds=300)
        pending = store.create(
            user_id=1,
            chat_id=2,
            text="帮我在本机执行 dir",
            risk_level="high",
        )

        decision = decide_agent_tool_request(
            text=f"{HIGH_RISK_CONFIRM_PREFIX} {pending.confirmation_id}",
            user_id=1,
            chat_id=2,
            has_tool_permission=True,
            confirmation_store=store,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.tool_policy, "trusted_confirmed")
        self.assertEqual(decision.confirmation_id, pending.confirmation_id)

        second = store.confirm(
            confirmation_id=pending.confirmation_id,
            user_id=1,
            chat_id=2,
            now=101,
        )
        self.assertIsNone(second)

    def test_confirmation_rejects_wrong_user_or_expired_code(self):
        store = AgentToolConfirmationStore(ttl_seconds=5)
        pending = store.create(
            user_id=1,
            chat_id=2,
            text="帮我在本机执行 dir",
            risk_level="high",
            now=100,
        )

        self.assertIsNone(
            store.confirm(
                confirmation_id=pending.confirmation_id,
                user_id=99,
                chat_id=2,
                now=101,
            )
        )
        self.assertIsNone(
            store.confirm(
                confirmation_id=pending.confirmation_id,
                user_id=1,
                chat_id=2,
                now=106,
            )
        )


if __name__ == "__main__":
    unittest.main()
