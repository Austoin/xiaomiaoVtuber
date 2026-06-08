from dataclasses import dataclass
from collections.abc import Awaitable
import asyncio
from typing import Any, Callable


QQ_AGENT_GROUP = "qq-group"
QQ_AGENT_PRIVATE = "qq-private"

QQ_MEMORY_COMMAND_ALIASES = {
    "记忆状态": "/status",
    "整理记忆": "/dream",
    "记忆日志": "/dream-log",
    "新会话": "/new",
    "停止任务": "/stop",
}
QQ_MEMORY_PREFIX_ALIASES = {
    "记忆日志 ": "/dream-log ",
    "恢复记忆 ": "/dream-restore ",
}


@dataclass(frozen=True)
class QQAgentTurn:
    source: str
    user_id: int
    chat_id: str
    text: str
    media: tuple[str, ...] = ()


@dataclass(frozen=True)
class QQAgentReply:
    turn: QQAgentTurn
    assistant_text: str
    tool_events: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True)
class QQMediaFailure:
    url: str
    error: str


ReplyCallback = Callable[[int, str, str, str, tuple[str, ...]], Any]
PublishCallback = Callable[..., None]
EventPublishCallback = Callable[..., None]
MediaConverter = Callable[[str], Awaitable[str | None]]
SyncAgentCall = Callable[[], Any]
WaitNoticeCallback = Callable[[], Awaitable[None]]


def is_qq_exact_command(order: str, command: str) -> bool:
    return order.strip() == command


def build_qq_agent_reply(
    *,
    source: str,
    user_id: int,
    chat_id: int | str,
    text: str,
    reply_callback: ReplyCallback,
    media: tuple[str, ...] = (),
) -> QQAgentReply:
    turn = build_qq_agent_turn(source, user_id, chat_id, text, media)
    reply = reply_callback(
        turn.user_id,
        turn.source,
        turn.chat_id,
        turn.text,
        turn.media,
    )
    assistant_text = getattr(reply, "assistant_text", reply)
    tool_events = getattr(reply, "tool_events", ())
    return QQAgentReply(
        turn=turn,
        assistant_text=str(assistant_text),
        tool_events=tuple(dict(event) for event in tool_events),
    )


def publish_qq_agent_reply(
    reply: QQAgentReply,
    publish_callback: PublishCallback,
    event_publish_callback: EventPublishCallback | None = None,
) -> None:
    turn = reply.turn
    publish_callback(
        source=turn.source,
        channel=turn.source,
        chat_id=turn.chat_id,
        user_id=turn.user_id,
        user_text=turn.text,
        assistant_text=reply.assistant_text,
    )
    if event_publish_callback is None:
        return
    for event in reply.tool_events:
        event_publish_callback(
            source=turn.source,
            channel=turn.source,
            chat_id=turn.chat_id,
            user_id=turn.user_id,
            role="assistant",
            content=str(event.get("result_summary") or reply.assistant_text),
            event_type=str(event.get("event_type") or "tool_finish"),
            tool_name=_optional_event_text(event, "tool_name"),
            risk_level=_optional_event_text(event, "risk_level"),
            confirmation_id=_optional_event_text(event, "confirmation_id"),
            result_summary=_optional_event_text(event, "result_summary"),
        )


async def await_agent_reply_with_wait_notice(
    call: SyncAgentCall,
    wait_notice_callback: WaitNoticeCallback,
    *,
    notice_after_seconds: float = 300.0,
) -> Any:
    task = asyncio.create_task(asyncio.to_thread(call))
    try:
        return await asyncio.wait_for(
            asyncio.shield(task),
            timeout=notice_after_seconds,
        )
    except asyncio.TimeoutError:
        await wait_notice_callback()
        return await task


def _optional_event_text(event: dict[str, Any], name: str) -> str | None:
    value = event.get(name)
    if value is None:
        return None
    return str(value)


def build_qq_agent_turn(
    source: str,
    user_id: int,
    chat_id: int | str,
    text: str,
    media: tuple[str, ...] = (),
) -> QQAgentTurn:
    if source not in {QQ_AGENT_GROUP, QQ_AGENT_PRIVATE}:
        raise ValueError(f"unsupported QQ agent source: {source}")
    clean_text = map_qq_memory_command(text)
    if not clean_text:
        raise ValueError("QQ agent turn requires non-empty text")
    return QQAgentTurn(
        source=source,
        user_id=int(user_id),
        chat_id=str(chat_id),
        text=clean_text,
        media=tuple(media),
    )


def map_qq_memory_command(text: str) -> str:
    clean_text = text.strip()
    if clean_text in QQ_MEMORY_COMMAND_ALIASES:
        return QQ_MEMORY_COMMAND_ALIASES[clean_text]
    for prefix, mapped_prefix in QQ_MEMORY_PREFIX_ALIASES.items():
        if clean_text.startswith(prefix):
            return mapped_prefix + clean_text[len(prefix):].strip()
    if clean_text == "恢复记忆":
        return "/dream-restore"
    return clean_text


def get_market_face_url(face_id: str) -> str:
    return f"https://gxh.vip.qq.com/club/item/parcel/item/{face_id[:2]}/{face_id}/raw300.gif"


def resolve_qq_image_url(file_value: str, url_value: str) -> str:
    if file_value.startswith("http"):
        return file_value
    return url_value


async def build_agent_media_from_urls(
    urls: tuple[str, ...],
    convert: MediaConverter,
) -> tuple[tuple[str, ...], tuple[QQMediaFailure, ...]]:
    media: list[str] = []
    failures: list[QQMediaFailure] = []
    for url in urls:
        try:
            media_item = await convert(url)
        except Exception as exc:
            failures.append(QQMediaFailure(url=url, error=str(exc)))
            continue
        if media_item:
            media.append(media_item)
    return tuple(media), tuple(failures)
