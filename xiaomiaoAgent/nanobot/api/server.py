"""OpenAI-compatible HTTP API server for a fixed xiaomiaoAgent session.

Provides /v1/chat/completions and /v1/models endpoints.
All requests route to a single persistent API session.
"""

from __future__ import annotations

import asyncio
import contextlib
import json as _json
import time
import uuid
from dataclasses import dataclass
from typing import Any

from aiohttp import web
from loguru import logger

from nanobot.config.paths import get_media_dir
from nanobot.utils.helpers import safe_filename
from nanobot.utils.media_decode import (
    MAX_FILE_SIZE,
)
from nanobot.utils.media_decode import (
    FileSizeExceeded as _FileSizeExceeded,
)
from nanobot.utils.media_decode import (
    save_base64_data_url as _save_base64_data_url,
)
from nanobot.utils.runtime import EMPTY_FINAL_RESPONSE_MESSAGE

__all__ = (
    "MAX_FILE_SIZE",
    "_FileSizeExceeded",
    "_save_base64_data_url",
    "create_app",
    "handle_chat_completions",
)


API_SESSION_KEY = "api:default"
API_CHAT_ID = "default"
DEFAULT_API_USER_ID = "user"
TRUSTED_CHANNEL_POLICY = "trusted"
LOW_RISK_CHANNEL_POLICY = "low_risk"
TRUSTED_PENDING_TOOL_POLICY = "trusted_pending"
TRUSTED_CONFIRMED_TOOL_POLICY = "trusted_confirmed"
LOW_RISK_SOURCE_CHANNELS = frozenset({"qq-group", "qq-private"})
VALID_TOOL_POLICIES = frozenset({
    LOW_RISK_CHANNEL_POLICY,
    TRUSTED_CHANNEL_POLICY,
    TRUSTED_PENDING_TOOL_POLICY,
    TRUSTED_CONFIRMED_TOOL_POLICY,
})


@dataclass(frozen=True)
class RequestSource:
    channel: str
    chat_id: str
    user_id: str
    channel_policy: str
    confirmation_id: str | None = None

    @property
    def metadata(self) -> dict[str, str]:
        metadata = {
            "source_channel": self.channel,
            "source_chat_id": self.chat_id,
            "source_user_id": self.user_id,
            "channel_policy": self.channel_policy,
        }
        if self.confirmation_id:
            metadata["confirmation_id"] = self.confirmation_id
        return metadata


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------


def _error_json(status: int, message: str, err_type: str = "invalid_request_error") -> web.Response:
    return web.json_response(
        {"error": {"message": message, "type": err_type, "code": status}},
        status=status,
    )


def _chat_completion_response(
    content: str,
    model: str,
    tool_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    response = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
    if tool_events:
        response["xiaomiao_tool_events"] = tool_events
    return response


def _response_text(value: Any) -> str:
    """Normalize process_direct output to plain assistant text."""
    if value is None:
        return ""
    if hasattr(value, "content"):
        return str(getattr(value, "content") or "")
    return str(value)


async def _maybe_wait_for(awaitable, timeout_s: float):
    if timeout_s <= 0:
        return await awaitable
    return await asyncio.wait_for(awaitable, timeout=timeout_s)


def _source_text(value: Any, default: str) -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def _source_policy(channel: str) -> str:
    if channel in LOW_RISK_SOURCE_CHANNELS:
        return LOW_RISK_CHANNEL_POLICY
    return TRUSTED_CHANNEL_POLICY


def _tool_policy(value: Any, *, channel: str) -> str:
    if value is None:
        return _source_policy(channel)

    policy = str(value).strip()
    if policy not in VALID_TOOL_POLICIES:
        raise ValueError(f"Invalid tool_policy: {policy}")
    if channel in LOW_RISK_SOURCE_CHANNELS and policy == TRUSTED_CHANNEL_POLICY:
        raise ValueError("QQ sources must use low_risk, trusted_pending, or trusted_confirmed")
    return policy


def _request_source(
    *,
    channel: Any = None,
    chat_id: Any = None,
    user_id: Any = None,
    tool_policy: Any = None,
    confirmation_id: Any = None,
) -> RequestSource:
    resolved_channel = _source_text(channel, "api")
    resolved_policy = _tool_policy(tool_policy, channel=resolved_channel)
    resolved_confirmation_id = _optional_source_text(confirmation_id)
    return RequestSource(
        channel=resolved_channel,
        chat_id=_source_text(chat_id, API_CHAT_ID),
        user_id=_source_text(user_id, DEFAULT_API_USER_ID),
        channel_policy=resolved_policy,
        confirmation_id=resolved_confirmation_id,
    )


def _optional_source_text(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None

# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------


def _sse_chunk(delta: str, model: str, chunk_id: str, finish_reason: str | None = None) -> bytes:
    """Format a single OpenAI-compatible SSE chunk."""
    payload = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {"content": delta} if delta else {},
                "finish_reason": finish_reason,
            }
        ],
    }
    return f"data: {_json.dumps(payload)}\n\n".encode()


_SSE_DONE = b"data: [DONE]\n\n"

# ---------------------------------------------------------------------------
# Upload helpers
# ---------------------------------------------------------------------------


def _parse_json_content(body: dict) -> tuple[str, list[str]]:
    """Parse JSON request body. Returns (text, media_paths)."""
    messages = body.get("messages")
    if not isinstance(messages, list) or len(messages) != 1:
        raise ValueError("Only a single user message is supported")
    message = messages[0]
    if not isinstance(message, dict) or message.get("role") != "user":
        raise ValueError("Only a single user message is supported")

    user_content = message.get("content", "")
    media_dir = get_media_dir("api")
    media_paths: list[str] = []

    if isinstance(user_content, list):
        text_parts: list[str] = []
        for part in user_content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text":
                text_parts.append(part.get("text", ""))
            elif part.get("type") == "image_url":
                url = part.get("image_url", {}).get("url", "")
                if url.startswith("data:"):
                    saved = _save_base64_data_url(url, media_dir)
                    if saved:
                        media_paths.append(saved)
                elif url:
                    raise ValueError(
                        "Remote image URLs are not supported. "
                        "Use base64 data URLs or upload files via multipart/form-data."
                    )
        text = " ".join(text_parts)
    elif isinstance(user_content, str):
        text = user_content
    else:
        raise ValueError("Invalid content format")

    return text, media_paths


async def _parse_multipart(
    request: web.Request,
) -> tuple[str, list[str], str | None, str | None, RequestSource]:
    """Parse multipart/form-data. Returns text, media, session, model, source."""
    media_dir = get_media_dir("api")
    reader = await request.multipart()
    text = ""
    session_id = None
    model = None
    channel = None
    chat_id = None
    user_id = None
    tool_policy = None
    confirmation_id = None
    media_paths: list[str] = []

    while True:
        part = await reader.next()
        if part is None:
            break
        value = None
        if part.name == "message":
            text = (await part.read()).decode("utf-8")
        elif part.name == "session_id":
            session_id = (await part.read()).decode("utf-8").strip()
        elif part.name == "model":
            model = (await part.read()).decode("utf-8").strip()
        elif part.name in {"channel", "chat_id", "user_id", "tool_policy", "confirmation_id"}:
            value = (await part.read()).decode("utf-8").strip()
            if part.name == "channel":
                channel = value
            elif part.name == "chat_id":
                chat_id = value
            elif part.name == "user_id":
                user_id = value
            elif part.name == "tool_policy":
                tool_policy = value
            else:
                confirmation_id = value
        elif part.name == "files":
            raw = await part.read()
            if len(raw) > MAX_FILE_SIZE:
                raise _FileSizeExceeded(
                    f"File '{part.filename}' exceeds {MAX_FILE_SIZE // (1024 * 1024)}MB limit"
                )
            base = safe_filename(part.filename or "upload.bin")
            filename = f"{uuid.uuid4().hex[:12]}_{base}"
            dest = media_dir / filename
            dest.write_bytes(raw)
            media_paths.append(str(dest))

    if not text:
        text = "请分析上传的文件"

    return text, media_paths, session_id, model, _request_source(
        channel=channel,
        chat_id=chat_id,
        user_id=user_id,
        tool_policy=tool_policy,
        confirmation_id=confirmation_id,
    )


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------


async def handle_chat_completions(request: web.Request) -> web.Response:
    """POST /v1/chat/completions — supports JSON and multipart/form-data."""
    content_type = request.content_type or ""
    if not isinstance(content_type, str):
        content_type = ""

    agent_loop = request.app["agent_loop"]
    timeout_s: float = request.app.get("request_timeout", 120.0)
    model_name: str = request.app.get("model_name", "xiaomiaoAgent")

    stream = False
    try:
        if content_type.startswith("multipart/"):
            text, media_paths, session_id, requested_model, source = await _parse_multipart(request)
        else:
            try:
                body = await request.json()
            except Exception:
                return _error_json(400, "Invalid JSON body")
            stream = body.get("stream", False)
            requested_model = body.get("model")
            text, media_paths = _parse_json_content(body)
            session_id = body.get("session_id")
            source = _request_source(
                channel=body.get("channel"),
                chat_id=body.get("chat_id"),
                user_id=body.get("user_id"),
                tool_policy=body.get("tool_policy"),
                confirmation_id=body.get("confirmation_id"),
            )
    except ValueError as e:
        return _error_json(400, str(e))
    except _FileSizeExceeded as e:
        return _error_json(413, str(e), err_type="invalid_request_error")
    except Exception:
        logger.exception("Error parsing upload")
        return _error_json(413, "File too large or invalid upload")

    if requested_model and requested_model != model_name:
        return _error_json(400, f"Only configured model '{model_name}' is available")

    if source.channel in LOW_RISK_SOURCE_CHANNELS:
        timeout_s = 0

    session_key = f"api:{session_id}" if session_id else API_SESSION_KEY
    session_locks: dict[str, asyncio.Lock] = request.app["session_locks"]
    session_lock = session_locks.setdefault(session_key, asyncio.Lock())

    logger.info(
        "API request session_key={} source={}:{} media={} text={} stream={}",
        session_key, source.channel, source.chat_id, len(media_paths), text[:80], stream,
    )
    # -- streaming path --
    if stream:
        resp = web.StreamResponse()
        resp.content_type = "text/event-stream"
        resp.headers["Cache-Control"] = "no-cache"
        resp.headers["Connection"] = "keep-alive"
        await resp.prepare(request)

        chunk_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        queue: asyncio.Queue[str | None] = asyncio.Queue()
        stream_failed = False
        emitted_content = False

        async def _on_stream(token: str) -> None:
            nonlocal emitted_content
            if token:
                emitted_content = True
            await queue.put(token)

        async def _on_stream_end(*_a: Any, **_kw: Any) -> None:
            # Agent stream-end callbacks mark generation segment boundaries.
            # Tool-backed requests may continue after a segment ends, so the
            # HTTP SSE stream is closed only when process_direct returns.
            return None

        async def _run() -> None:
            nonlocal stream_failed
            try:
                async with session_lock:
                    response = await _maybe_wait_for(
                        agent_loop.process_direct(
                            content=text,
                            media=media_paths if media_paths else None,
                            session_key=session_key,
                            channel=source.channel,
                            chat_id=source.chat_id,
                            sender_id=source.user_id,
                            metadata=source.metadata,
                            on_stream=_on_stream,
                            on_stream_end=_on_stream_end,
                        ),
                        timeout_s,
                    )
                    if not emitted_content:
                        response_text = _response_text(response)
                        if response_text.strip():
                            await queue.put(response_text)
            except Exception:
                stream_failed = True
                logger.exception("Streaming error for session {}", session_key)
            finally:
                await queue.put(None)

        task = asyncio.create_task(_run())
        try:
            while True:
                token = await queue.get()
                if token is None:
                    break
                await resp.write(_sse_chunk(token, model_name, chunk_id))
        finally:
            if not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        if not stream_failed:
            await resp.write(_sse_chunk("", model_name, chunk_id, finish_reason="stop"))
            await resp.write(_SSE_DONE)
        return resp

    # -- non-streaming path (original logic) --
    fallback = EMPTY_FINAL_RESPONSE_MESSAGE
    collected_tool_events: list[dict[str, Any]] = []

    async def _on_progress(
        _content: str,
        *,
        tool_hint: bool = False,
        tool_events: list[dict[str, Any]] | None = None,
    ) -> None:
        if tool_events:
            collected_tool_events.extend(tool_events)

    try:
        async with session_lock:
            try:
                response = await _maybe_wait_for(
                    agent_loop.process_direct(
                        content=text,
                        media=media_paths if media_paths else None,
                        session_key=session_key,
                        channel=source.channel,
                        chat_id=source.chat_id,
                        sender_id=source.user_id,
                        metadata=source.metadata,
                        on_progress=_on_progress,
                    ),
                    timeout_s,
                )
                response_text = _response_text(response)

                if not response_text or not response_text.strip():
                    logger.warning("Empty response for session {}, retrying", session_key)
                    retry_response = await _maybe_wait_for(
                        agent_loop.process_direct(
                            content=text,
                            media=media_paths if media_paths else None,
                            session_key=session_key,
                            channel=source.channel,
                            chat_id=source.chat_id,
                            sender_id=source.user_id,
                            metadata=source.metadata,
                            on_progress=_on_progress,
                        ),
                        timeout_s,
                    )
                    response_text = _response_text(retry_response)
                    if not response_text or not response_text.strip():
                        logger.warning("Empty response after retry, using fallback")
                        response_text = fallback

            except asyncio.TimeoutError:
                return _error_json(504, f"Request timed out after {timeout_s}s")
            except Exception:
                logger.exception("Error processing request for session {}", session_key)
                return _error_json(500, "Internal server error", err_type="server_error")
    except Exception:
        logger.exception("Unexpected API lock error for session {}", session_key)
        return _error_json(500, "Internal server error", err_type="server_error")

    return web.json_response(
        _chat_completion_response(
            response_text,
            model_name,
            tool_events=collected_tool_events,
        )
    )


async def handle_models(request: web.Request) -> web.Response:
    """GET /v1/models"""
    model_name = request.app.get("model_name", "xiaomiaoAgent")
    return web.json_response(
        {
            "object": "list",
            "data": [
                {
                    "id": model_name,
                    "object": "model",
                    "created": 0,
                    "owned_by": "xiaomiaoAgent",
                }
            ],
        }
    )


async def handle_health(request: web.Request) -> web.Response:
    """GET /health"""
    return web.json_response({"status": "ok"})


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app(
    agent_loop, model_name: str = "xiaomiaoAgent", request_timeout: float = 120.0
) -> web.Application:
    """Create the aiohttp application.

    Args:
        agent_loop: An initialized AgentLoop instance.
        model_name: Model name reported in responses.
        request_timeout: Per-request timeout in seconds.
    """
    app = web.Application(client_max_size=20 * 1024 * 1024)  # 20MB for base64 images
    app["agent_loop"] = agent_loop
    app["model_name"] = model_name
    app["request_timeout"] = request_timeout
    app["session_locks"] = {}  # per-user locks, keyed by session_key

    app.router.add_post("/v1/chat/completions", handle_chat_completions)
    app.router.add_get("/v1/models", handle_models)
    app.router.add_get("/health", handle_health)
    return app
