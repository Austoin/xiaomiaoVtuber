import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from qq_permissions import (  # noqa: E402
    has_agent_tool_permission,
    has_manage_permission,
    has_super_permission,
)


class QQPermissionsTests(unittest.TestCase):
    def test_manage_permission_accepts_manage_super_and_root(self):
        self.assertTrue(
            has_manage_permission(
                10001,
                manage_users=["10001"],
                super_users=[],
                root_users=[],
            )
        )
        self.assertTrue(
            has_manage_permission(
                "20002",
                manage_users=[],
                super_users=["20002"],
                root_users=[],
            )
        )
        self.assertTrue(
            has_manage_permission(
                "30003",
                manage_users=[],
                super_users=[],
                root_users=["30003"],
            )
        )

    def test_manage_permission_rejects_common_user(self):
        self.assertFalse(
            has_manage_permission(
                "40004",
                manage_users=["10001"],
                super_users=["20002"],
                root_users=["30003"],
            )
        )

    def test_super_permission_accepts_super_and_root_only(self):
        self.assertFalse(
            has_super_permission(
                "10001",
                super_users=[],
                root_users=[],
            )
        )
        self.assertTrue(
            has_super_permission(
                "20002",
                super_users=["20002"],
                root_users=[],
            )
        )
        self.assertTrue(
            has_super_permission(
                30003,
                super_users=[],
                root_users=["30003"],
            )
        )

    def test_agent_tool_permission_accepts_allowlist_super_and_root(self):
        self.assertTrue(
            has_agent_tool_permission(
                "10001",
                agent_tool_allowlist=["10001"],
                super_users=[],
                root_users=[],
            )
        )
        self.assertTrue(
            has_agent_tool_permission(
                "20002",
                agent_tool_allowlist=[],
                super_users=["20002"],
                root_users=[],
            )
        )
        self.assertTrue(
            has_agent_tool_permission(
                "30003",
                agent_tool_allowlist=[],
                super_users=[],
                root_users=["30003"],
            )
        )

    def test_agent_tool_permission_rejects_common_user(self):
        self.assertFalse(
            has_agent_tool_permission(
                "40004",
                agent_tool_allowlist=["10001"],
                super_users=["20002"],
                root_users=["30003"],
            )
        )


if __name__ == "__main__":
    unittest.main()
