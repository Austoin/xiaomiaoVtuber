from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from nanobot.bus.events import OutboundMessage
from nanobot.channels import websocket as websocket_module
from nanobot.channels.websocket import WebSocketChannel


def _channel(bus: Any) -> WebSocketChannel:
    return WebSocketChannel(
        {
            "enabled": True,
            "allowFrom": ["*"],
            "host": "127.0.0.1",
            "port": 29940,
            "path": "/",
            "websocketRequiresToken": False,
        },
        bus,
    )


@pytest.mark.asyncio
async def test_xiaomiao_unified_user_message_mirrors_to_bridge(monkeypatch) -> None:
    mirrored: list[dict[str, Any]] = []

    async def fake_post(payload: dict[str, Any]) -> None:
        mirrored.append(payload)

    monkeypatch.setattr(websocket_module, "_post_xiaomiao_bridge_event", fake_post)
    bus = MagicMock()
    bus.publish_inbound = AsyncMock()
    channel = _channel(bus)

    await channel._dispatch_envelope(
        MagicMock(remote_address=("127.0.0.1", 50000)),
        "browser",
        {
            "type": "message",
            "chat_id": "xiaomiao-unified",
            "content": "Agent 端问题",
            "webui": True,
        },
    )

    assert mirrored == [
        {
            "source": "agent-webui",
            "channel": "agent-webui",
            "chat_id": "xiaomiao-unified",
            "role": "user",
            "content": "Agent 端问题",
        }
    ]


@pytest.mark.asyncio
async def test_non_unified_user_message_does_not_mirror_to_bridge(monkeypatch) -> None:
    mirrored: list[dict[str, Any]] = []

    async def fake_post(payload: dict[str, Any]) -> None:
        mirrored.append(payload)

    monkeypatch.setattr(websocket_module, "_post_xiaomiao_bridge_event", fake_post)
    bus = MagicMock()
    bus.publish_inbound = AsyncMock()
    channel = _channel(bus)

    await channel._dispatch_envelope(
        MagicMock(remote_address=("127.0.0.1", 50000)),
        "browser",
        {
            "type": "message",
            "chat_id": "websocket-private-chat",
            "content": "私有 WebSocket 会话",
            "webui": True,
        },
    )

    assert mirrored == []


@pytest.mark.asyncio
async def test_xiaomiao_unified_streaming_reply_mirrors_once(monkeypatch) -> None:
    mirrored: list[dict[str, Any]] = []

    async def fake_post(payload: dict[str, Any]) -> None:
        mirrored.append(payload)

    monkeypatch.setattr(websocket_module, "_post_xiaomiao_bridge_event", fake_post)
    connection = MagicMock()
    connection.send = AsyncMock()
    channel = _channel(MagicMock())
    channel._subs["xiaomiao-unified"] = {connection}

    await channel.send_delta("xiaomiao-unified", "o")
    await channel.send_delta("xiaomiao-unified", "k")
    await channel.send_delta("xiaomiao-unified", "", metadata={"_stream_end": True})

    assert mirrored == [
        {
            "source": "agent-webui",
            "channel": "agent-webui",
            "chat_id": "xiaomiao-unified",
            "role": "assistant",
            "content": "ok",
        }
    ]


@pytest.mark.asyncio
async def test_xiaomiao_unified_non_streaming_reply_mirrors_to_bridge(monkeypatch) -> None:
    mirrored: list[dict[str, Any]] = []

    async def fake_post(payload: dict[str, Any]) -> None:
        mirrored.append(payload)

    monkeypatch.setattr(websocket_module, "_post_xiaomiao_bridge_event", fake_post)
    connection = MagicMock()
    connection.send = AsyncMock()
    channel = _channel(MagicMock())
    channel._subs["xiaomiao-unified"] = {connection}

    await channel.send(
        OutboundMessage(
            channel="websocket",
            chat_id="xiaomiao-unified",
            content="非流式回答",
        )
    )

    assert mirrored == [
        {
            "source": "agent-webui",
            "channel": "agent-webui",
            "chat_id": "xiaomiao-unified",
            "role": "assistant",
            "content": "非流式回答",
        }
    ]
