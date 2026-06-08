import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from qq_agent_tools import (  # noqa: E402
    decide_agent_tool_request,
)


class QQAgentToolsTests(unittest.TestCase):
    def test_permissioned_normal_prompt_uses_confirmed_policy_without_keyword_gate(self):
        decision = decide_agent_tool_request(
            text="抓取网页内容并整理成一个本地说明文件",
            user_id=1,
            chat_id=2,
            has_tool_permission=True,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.tool_policy, "trusted_confirmed")

    def test_common_user_normal_prompt_stays_low_risk_without_keyword_gate(self):
        decision = decide_agent_tool_request(
            text="抓取网页内容并整理成一个本地说明文件",
            user_id=1,
            chat_id=2,
            has_tool_permission=False,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.tool_policy, "low_risk")

    def test_high_risk_without_permission_stays_low_risk_for_agent_side_block(self):
        decision = decide_agent_tool_request(
            text="帮我在本机执行 dir",
            user_id=1,
            chat_id=2,
            has_tool_permission=False,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.tool_policy, "low_risk")
        self.assertEqual(decision.message, "")

    def test_high_risk_with_permission_uses_confirmed_policy_without_second_confirmation(self):
        decision = decide_agent_tool_request(
            text="帮我在本机执行 dir",
            user_id=1,
            chat_id=2,
            has_tool_permission=True,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.tool_policy, "trusted_confirmed")
        self.assertEqual(decision.message, "")


if __name__ == "__main__":
    unittest.main()
