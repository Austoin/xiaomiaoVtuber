"""QQ Bot 工具适配器

为 xiaomiao QQ Bot 提供统一的工具调用接口。
"""

import sys
from pathlib import Path

# 添加 tool 目录到 Python path
TOOL_DIR = Path(__file__).parents[2]
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from tool.xiaomiao.permissions import (
    LOW_RISK_TOOL_POLICY,
    TRUSTED_CONFIRMED_TOOL_POLICY,
    AgentToolDecision,
    decide_agent_tool_request,
)


def get_tool_policy(user_id: int | str, has_permission: bool) -> str:
    """
    获取用户的工具策略

    Args:
        user_id: QQ 用户 ID
        has_permission: 用户是否有高权限（ROOT/Super/白名单）

    Returns:
        工具策略字符串 ('low_risk' 或 'trusted_confirmed')
    """
    decision = decide_agent_tool_request(
        text="",
        user_id=user_id,
        chat_id="",
        has_tool_permission=has_permission
    )
    return decision.tool_policy


def decide_tool_request(
    text: str,
    user_id: int | str,
    chat_id: int | str,
    has_tool_permission: bool,
) -> AgentToolDecision:
    """
    决定是否允许工具调用

    这是对 tool.xiaomiao.permissions.decide_agent_tool_request 的直接封装，
    保持与原 qq_agent_tools.py 相同的接口。

    Args:
        text: 用户消息文本
        user_id: QQ 用户 ID
        chat_id: 会话 ID（群号或私聊 ID）
        has_tool_permission: 用户是否有高权限

    Returns:
        AgentToolDecision: 工具调用决策
    """
    return decide_agent_tool_request(
        text=text,
        user_id=user_id,
        chat_id=chat_id,
        has_tool_permission=has_tool_permission
    )


__all__ = [
    "LOW_RISK_TOOL_POLICY",
    "TRUSTED_CONFIRMED_TOOL_POLICY",
    "AgentToolDecision",
    "get_tool_policy",
    "decide_tool_request",
]
