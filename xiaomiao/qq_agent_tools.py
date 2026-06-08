import secrets
import time
from dataclasses import dataclass
from typing import Literal


LOW_RISK_TOOL_POLICY = "low_risk"
TRUSTED_PENDING_TOOL_POLICY = "trusted_pending"
TRUSTED_CONFIRMED_TOOL_POLICY = "trusted_confirmed"
HIGH_RISK_CONFIRM_PREFIX = "确认执行"
CONFIRMATION_REQUIRED_PREFIX = "CONFIRMATION_REQUIRED"
DEFAULT_CONFIRMATION_TTL_SECONDS = 300

RiskLevel = Literal["low", "medium", "high"]

HIGH_RISK_KEYWORDS = (
    "执行",
    "运行命令",
    "本机命令",
    "电脑命令",
    "shell",
    "powershell",
    "cmd",
    "终端",
    "启动程序",
    "打开程序",
    "删除文件",
    "写入文件",
    "修改文件",
    "homeassistant",
    "minecraft",
    "发推",
    "发帖",
    "点赞",
    "转发",
    "claude code",
    "computer use",
    "/dream-restore",
    "dream-restore",
    "恢复记忆",
    "还原记忆",
    "回滚记忆",
)


@dataclass(frozen=True)
class PendingAgentToolRequest:
    confirmation_id: str
    user_id: str
    chat_id: str
    text: str
    risk_level: RiskLevel
    expires_at: float


@dataclass(frozen=True)
class AgentToolDecision:
    allowed: bool
    tool_policy: str
    confirmation_id: str | None = None
    pending_request: PendingAgentToolRequest | None = None
    message: str = ""


class AgentToolConfirmationStore:
    def __init__(self, ttl_seconds: int = DEFAULT_CONFIRMATION_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._pending: dict[str, PendingAgentToolRequest] = {}

    def create(
        self,
        *,
        user_id: int | str,
        chat_id: int | str,
        text: str,
        risk_level: RiskLevel,
        now: float | None = None,
    ) -> PendingAgentToolRequest:
        created_at = time.time() if now is None else now
        confirmation_id = self._new_confirmation_id()
        request = PendingAgentToolRequest(
            confirmation_id=confirmation_id,
            user_id=str(user_id),
            chat_id=str(chat_id),
            text=text.strip(),
            risk_level=risk_level,
            expires_at=created_at + self.ttl_seconds,
        )
        self._pending[confirmation_id] = request
        return request

    def confirm(
        self,
        *,
        confirmation_id: str,
        user_id: int | str,
        chat_id: int | str,
        now: float | None = None,
    ) -> PendingAgentToolRequest | None:
        current_time = time.time() if now is None else now
        request = self._pending.get(confirmation_id)
        if request is None:
            return None
        if request.expires_at < current_time:
            self._pending.pop(confirmation_id, None)
            return None
        if request.user_id != str(user_id) or request.chat_id != str(chat_id):
            return None
        self._pending.pop(confirmation_id, None)
        return request

    def _new_confirmation_id(self) -> str:
        while True:
            confirmation_id = secrets.token_hex(3).upper()
            if confirmation_id not in self._pending:
                return confirmation_id


def detect_agent_tool_risk(text: str) -> RiskLevel:
    normalized = text.strip().lower()
    if any(keyword in normalized for keyword in HIGH_RISK_KEYWORDS):
        return "high"
    return "low"


def parse_confirmation_command(text: str) -> str | None:
    clean_text = text.strip()
    if not clean_text.startswith(HIGH_RISK_CONFIRM_PREFIX):
        return None
    confirmation_id = clean_text[len(HIGH_RISK_CONFIRM_PREFIX):].strip()
    return confirmation_id or None


def decide_agent_tool_request(
    *,
    text: str,
    user_id: int | str,
    chat_id: int | str,
    has_tool_permission: bool,
    confirmation_store: AgentToolConfirmationStore,
) -> AgentToolDecision:
    confirmation_id = parse_confirmation_command(text)
    if confirmation_id:
        request = confirmation_store.confirm(
            confirmation_id=confirmation_id,
            user_id=user_id,
            chat_id=chat_id,
        )
        if request is None:
            return AgentToolDecision(
                allowed=False,
                tool_policy=LOW_RISK_TOOL_POLICY,
                message="确认码无效、已过期，或不属于当前用户/会话。",
            )
        return AgentToolDecision(
            allowed=True,
            tool_policy=TRUSTED_CONFIRMED_TOOL_POLICY,
            confirmation_id=request.confirmation_id,
            pending_request=request,
        )

    risk_level = detect_agent_tool_risk(text)
    if not has_tool_permission:
        return AgentToolDecision(allowed=True, tool_policy=LOW_RISK_TOOL_POLICY)

    return AgentToolDecision(allowed=True, tool_policy=TRUSTED_PENDING_TOOL_POLICY)


def build_confirmation_request(
    *,
    text: str,
    user_id: int | str,
    chat_id: int | str,
    confirmation_store: AgentToolConfirmationStore,
    risk_level: RiskLevel = "high",
) -> AgentToolDecision:
    request = confirmation_store.create(
        user_id=user_id,
        chat_id=chat_id,
        text=text,
        risk_level=risk_level,
    )
    return AgentToolDecision(
        allowed=False,
        tool_policy=TRUSTED_PENDING_TOOL_POLICY,
        pending_request=request,
        message=format_confirmation_message(request, confirmation_store.ttl_seconds),
    )


def format_confirmation_message(
    request: PendingAgentToolRequest,
    ttl_seconds: int,
) -> str:
    return (
        f"检测到高风险工具请求，需要二次确认。\n"
        f"确认码：{request.confirmation_id}\n"
        f"请在 {ttl_seconds // 60} 分钟内发送："
        f"{HIGH_RISK_CONFIRM_PREFIX} {request.confirmation_id}"
    )


def agent_event_requires_confirmation(event: dict) -> bool:
    for name in ("error", "result_summary", "detail", "content"):
        value = event.get(name)
        if isinstance(value, str) and value.strip().startswith(CONFIRMATION_REQUIRED_PREFIX):
            return True
    return False
