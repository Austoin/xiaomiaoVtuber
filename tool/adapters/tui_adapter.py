"""TUI 终端适配器

为 TUI 终端界面提供统一的工具调用接口。
TUI 默认使用 trusted_confirmed 策略，拥有完整工具权限。
"""

import sys
from pathlib import Path

# 添加 tool 目录到 Python path
TOOL_DIR = Path(__file__).parents[2]
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from tool.xiaomiao.permissions import TRUSTED_CONFIRMED_TOOL_POLICY


def get_tui_tool_policy() -> str:
    """
    获取 TUI 的工具策略

    TUI 是本地终端界面，默认拥有完整工具权限。

    Returns:
        始终返回 'trusted_confirmed'
    """
    return TRUSTED_CONFIRMED_TOOL_POLICY


def setup_tui_tools():
    """
    为 TUI 设置工具环境

    TUI 通过 xiaomiaoAgent 的 AgentLoop 直接调用工具，
    无需额外设置，这个函数保留用于未来扩展。
    """
    pass


__all__ = [
    "get_tui_tool_policy",
    "setup_tui_tools",
]
