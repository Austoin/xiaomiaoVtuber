"""xiaomiaoAgent 工具适配器

为 xiaomiaoAgent (nanobot) 提供统一的工具注册接口。
从 tool/ 目录加载工具并注册到 nanobot 的工具系统。
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

# 添加 tool 目录到 Python path
TOOL_DIR = Path(__file__).parents[2]
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

if TYPE_CHECKING:
    from tool.core.registry import ToolRegistry


def register_all_tools(registry: "ToolRegistry") -> None:
    """
    注册所有工具到 xiaomiaoAgent

    这个函数会被 xiaomiaoAgent 在启动时调用，
    将 tool/ 目录下的所有工具注册到工具注册表。

    Args:
        registry: xiaomiaoAgent 的工具注册表
    """
    # 核心工具已经通过原有的 nanobot 系统加载
    # 这里只需要注册项目专属工具

    try:
        # 导入项目专属工具（这些工具已经在 tool/core/ 中）
        # xiaomiaoAgent 会自动发现并加载它们
        pass
    except ImportError as e:
        # 如果导入失败，记录错误但不中断启动
        import logging
        logging.warning(f"Failed to load some xiaomiao tools: {e}")


def get_tool_policy_for_user(user_id: str, has_permission: bool) -> str:
    """
    获取用户的工具策略

    Args:
        user_id: 用户 ID
        has_permission: 用户是否有高权限

    Returns:
        工具策略字符串 ('low_risk' 或 'trusted_confirmed')
    """
    from tool.xiaomiao.permissions import decide_agent_tool_request

    decision = decide_agent_tool_request(
        text="",
        user_id=user_id,
        chat_id="",
        has_tool_permission=has_permission
    )
    return decision.tool_policy


__all__ = ["register_all_tools", "get_tool_policy_for_user"]
