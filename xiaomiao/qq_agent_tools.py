from dataclasses import dataclass


LOW_RISK_TOOL_POLICY = "low_risk"
TRUSTED_CONFIRMED_TOOL_POLICY = "trusted_confirmed"


@dataclass(frozen=True)
class AgentToolDecision:
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
    if not has_tool_permission:
        return AgentToolDecision(allowed=True, tool_policy=LOW_RISK_TOOL_POLICY)

    return AgentToolDecision(allowed=True, tool_policy=TRUSTED_CONFIRMED_TOOL_POLICY)
