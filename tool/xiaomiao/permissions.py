"""QQ Bot 工具权限策略

从 xiaomiao/qq_agent_tools.py 提取的权限判断逻辑。
"""

from dataclasses import dataclass


LOW_RISK_TOOL_POLICY = "low_risk"
TRUSTED_CONFIRMED_TOOL_POLICY = "trusted_confirmed"


@dataclass(frozen=True)
class AgentToolDecision:
    """工具调用决策"""
    allowed: bool
    tool_policy: str
    message: str = ""


def decide_agent_tool_request(
    *,
    text: str,
    user_id: int | str,
    chat_id: int | str,
    has_tool_permission: bool,
) -> AgentToolDecision:
    """
    决定是否允许工具调用及使用何种策略

    Args:
        text: 用户消息文本
        user_id: 用户 ID
        chat_id: 会话 ID
        has_tool_permission: 用户是否有高权限（ROOT/Super/白名单）

    Returns:
        AgentToolDecision: 工具调用决策
    """
    if not has_tool_permission:
        # 普通用户：只能使用低风险工具
        return AgentToolDecision(allowed=True, tool_policy=LOW_RISK_TOOL_POLICY)

    # 高权限用户：可以使用所有工具
    return AgentToolDecision(allowed=True, tool_policy=TRUSTED_CONFIRMED_TOOL_POLICY)


__all__ = [
    "LOW_RISK_TOOL_POLICY",
    "TRUSTED_CONFIRMED_TOOL_POLICY",
    "AgentToolDecision",
    "decide_agent_tool_request",
]
