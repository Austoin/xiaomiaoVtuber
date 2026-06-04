from dataclasses import dataclass
from collections.abc import Awaitable
from typing import Callable


QQ_AGENT_GROUP = "qq-group"
QQ_AGENT_PRIVATE = "qq-private"


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


@dataclass(frozen=True)
class QQMediaFailure:
    url: str
    error: str


ReplyCallback = Callable[[int, str, str, str, tuple[str, ...]], str]
PublishCallback = Callable[..., None]
MediaConverter = Callable[[str], Awaitable[str | None]]


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
    return QQAgentReply(turn=turn, assistant_text=reply)


def publish_qq_agent_reply(
    reply: QQAgentReply,
    publish_callback: PublishCallback,
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


def build_qq_agent_turn(
    source: str,
    user_id: int,
    chat_id: int | str,
    text: str,
    media: tuple[str, ...] = (),
) -> QQAgentTurn:
    if source not in {QQ_AGENT_GROUP, QQ_AGENT_PRIVATE}:
        raise ValueError(f"unsupported QQ agent source: {source}")
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("QQ agent turn requires non-empty text")
    return QQAgentTurn(
        source=source,
        user_id=int(user_id),
        chat_id=str(chat_id),
        text=clean_text,
        media=tuple(media),
    )


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
