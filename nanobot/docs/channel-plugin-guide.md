# 通道插件指南

构建自定义 nanobot 通道只需要三步：继承、打包、安装。

> **注意：** 建议基于 nanobot 源码 checkout（`pip install -e .`）开发通道插件，而不是基于 PyPI 发布版。这样你始终可以使用最新的基础通道功能和 API。

## 工作原理

nanobot 通过 Python [entry points](https://packaging.python.org/en/latest/specifications/entry-points/) 发现通道插件。`nanobot gateway` 启动时会扫描：

1. `nanobot/channels/` 中的内置通道。
2. 注册到 `nanobot.channels` entry point group 下的外部包。

如果匹配的配置段包含 `"enabled": true`，该通道就会被实例化并启动。

## 快速开始

我们将构建一个最小 webhook 通道：通过 HTTP POST 接收消息，并发送回复。

### 项目结构

```text
nanobot-channel-webhook/
├── nanobot_channel_webhook/
│   ├── __init__.py          # 重新导出 WebhookChannel
│   └── channel.py           # 通道实现
└── pyproject.toml
```

### 1. 创建通道

```python
# nanobot_channel_webhook/__init__.py
from nanobot_channel_webhook.channel import WebhookChannel

__all__ = ["WebhookChannel"]
```

```python
# nanobot_channel_webhook/channel.py
import asyncio
from typing import Any

from aiohttp import web
from loguru import logger
from pydantic import Field

from nanobot.channels.base import BaseChannel
from nanobot.bus.events import OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.config.schema import Base


class WebhookConfig(Base):
    """Webhook channel configuration."""
    enabled: bool = False
    port: int = 9000
    allow_from: list[str] = Field(default_factory=list)


class WebhookChannel(BaseChannel):
    name = "webhook"
    display_name = "Webhook"

    def __init__(self, config: Any, bus: MessageBus):
        if isinstance(config, dict):
            config = WebhookConfig(**config)
        super().__init__(config, bus)

    @classmethod
    def default_config(cls) -> dict[str, Any]:
        return WebhookConfig().model_dump(by_alias=True)

    async def start(self) -> None:
        """Start an HTTP server that listens for incoming messages.

        IMPORTANT: start() must block forever (or until stop() is called).
        If it returns, the channel is considered dead.
        """
        self._running = True
        port = self.config.port

        app = web.Application()
        app.router.add_post("/message", self._on_request)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info("Webhook listening on :{}", port)

        # 阻塞直到停止
        while self._running:
            await asyncio.sleep(1)

        await runner.cleanup()

    async def stop(self) -> None:
        self._running = False

    async def send(self, msg: OutboundMessage) -> None:
        """Deliver an outbound message.

        msg.content  — markdown text (convert to platform format as needed)
        msg.media    — list of local file paths to attach
        msg.chat_id  — the recipient (same chat_id you passed to _handle_message)
        msg.metadata — may contain "_progress": True for streaming chunks
        """
        logger.info("[webhook] -> {}: {}", msg.chat_id, msg.content[:80])
        # 真实插件中：POST 到 callback URL，或通过 SDK 发送等。

    async def _on_request(self, request: web.Request) -> web.Response:
        """Handle an incoming HTTP POST."""
        body = await request.json()
        sender = body.get("sender", "unknown")
        chat_id = body.get("chat_id", sender)
        text = body.get("text", "")
        media = body.get("media", [])       # URL 列表

        # 这是关键调用：先验证 allowFrom，然后把消息放入 bus 交给 agent 处理。
        await self._handle_message(
            sender_id=sender,
            chat_id=chat_id,
            content=text,
            media=media,
        )

        return web.json_response({"ok": True})
```

### 2. 注册 Entry Point

```toml
# pyproject.toml
[project]
name = "nanobot-channel-webhook"
version = "0.1.0"
dependencies = ["nanobot-ai", "aiohttp"]

[project.entry-points."nanobot.channels"]
webhook = "nanobot_channel_webhook:WebhookChannel"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["nanobot_channel_webhook"]
```

key（`webhook`）会成为配置段名称。value 指向你的 `BaseChannel` 子类。

### 3. 安装并配置

```bash
pip install -e .
nanobot plugins list      # 确认 "Webhook" 显示为 "plugin"
nanobot onboard           # 自动为检测到的插件添加默认配置
```

编辑 `~/.nanobot/config.json`：

```json
{
  "channels": {
    "webhook": {
      "enabled": true,
      "port": 9000,
      "allowFrom": ["*"]
    }
  }
}
```

### 4. 运行并测试

```bash
nanobot gateway
```

在另一个终端中：

```bash
curl -X POST http://localhost:9000/message \
  -H "Content-Type: application/json" \
  -d '{"sender": "user1", "chat_id": "user1", "text": "Hello!"}'
```

agent 会收到消息并处理。回复会进入你的 `send()` 方法。

## BaseChannel API

### 必需方法（abstract）

| 方法 | 说明 |
|--------|-------------|
| `async start()` | **必须永久阻塞。** 连接到平台、监听消息，并对每条消息调用 `_handle_message()`。如果该方法返回，通道会被视为已死亡。 |
| `async stop()` | 设置 `self._running = False` 并清理资源。gateway 关闭时会调用。 |
| `async send(msg: OutboundMessage)` | 将出站消息投递到平台。 |

### 交互式登录

如果你的通道需要交互式认证（例如扫描二维码），请覆盖 `login(force=False)`：

```python
async def login(self, force: bool = False) -> bool:
    """
    Perform channel-specific interactive login.

    Args:
        force: If True, ignore existing credentials and re-authenticate.

    Returns True if already authenticated or login succeeds.
    """
    # 对于基于二维码的登录：
    # 1. 如果 force 为 True，清除已保存凭据
    # 2. 检查是否已认证（从磁盘/状态加载）
    # 3. 如果未认证，显示二维码并轮询确认
    # 4. 成功后保存 token
```

不需要交互式登录的通道（例如使用 bot token 的 Telegram、Discord）会继承默认 `login()`，它只返回 `True`。

用户通过以下命令触发交互式登录：

```bash
nanobot channels login <channel_name>
nanobot channels login <channel_name> --force  # 重新认证
```

### Base 提供的方法

| 方法 / 属性 | 说明 |
|-------------------|-------------|
| `_handle_message(sender_id, chat_id, content, media?, metadata?, session_key?)` | **收到消息时调用它。** 它会检查 `is_allowed()`，然后发布到 bus。如果 `supports_streaming` 为 true，会自动设置 `_wants_stream`。 |
| `is_allowed(sender_id)` | 按 `config.allow_from` 检查权限；`"*"` 允许所有，`[]` 拒绝所有。 |
| `default_config()`（classmethod） | 返回供 `nanobot onboard` 使用的默认配置 dict。覆盖它以声明你的字段。 |
| `transcribe_audio(file_path)` | 通过 Groq Whisper 转写音频（如果已配置）。 |
| `supports_streaming`（property） | 当配置包含 `"streaming": true` 且子类覆盖 `send_delta()` 时为 `True`。 |
| `is_running` | 返回 `self._running`。 |
| `login(force=False)` | 执行交互式登录，例如扫码。如果已经认证或登录成功则返回 `True`。支持交互式登录的子类应覆盖它。 |

### 可选方法（streaming）

| 方法 | 说明 |
|--------|-------------|
| `async send_delta(chat_id, delta, metadata?)` | 覆盖它以接收流式片段。详见[流式支持](#流式支持)。 |

### 消息类型

```python
@dataclass
class OutboundMessage:
    channel: str        # 你的通道名称
    chat_id: str        # 接收者（与传给 _handle_message 的值相同）
    content: str        # markdown 文本，按需转换为平台格式
    media: list[str]    # 要附加的本地文件路径（图片、音频、文档）
    metadata: dict      # 可能包含："_progress" (bool)，表示流式片段；
                        #              "message_id"，用于回复串联
```

## 流式支持

通道可以选择加入实时 streaming，agent 会逐 token 发送内容，而不是只发送一条最终消息。这完全可选；没有 streaming 时通道也能正常工作。

### 工作原理

当同时满足以下两个条件时，agent 会通过你的通道流式输出内容：

1. 配置包含 `"streaming": true`。
2. 你的子类覆盖了 `send_delta()`。

如果缺少任一条件，agent 会回退到普通的一次性 `send()` 路径。

### 实现 `send_delta`

覆盖 `send_delta` 以处理两类调用：

```python
async def send_delta(self, chat_id: str, delta: str, metadata: dict[str, Any] | None = None) -> None:
    meta = metadata or {}

    if meta.get("_stream_end"):
        # Streaming 结束，执行最终格式化、清理等。
        return

    # 常规 delta：追加文本，更新屏幕上的消息。
    # delta 包含一小段文本（几个 token）。
```

**Metadata 标志：**

| 标志 | 含义 |
|------|---------|
| `_stream_delta: True` | 内容片段，delta 包含新文本 |
| `_stream_end: True` | Streaming 结束，delta 为空 |

### 示例：支持 Streaming 的 Webhook

```python
class WebhookChannel(BaseChannel):
    name = "webhook"
    display_name = "Webhook"

    def __init__(self, config: Any, bus: MessageBus):
        if isinstance(config, dict):
            config = WebhookConfig(**config)
        super().__init__(config, bus)
        self._buffers: dict[str, str] = {}

    async def send_delta(self, chat_id: str, delta: str, metadata: dict[str, Any] | None = None) -> None:
        meta = metadata or {}
        if meta.get("_stream_end"):
            text = self._buffers.pop(chat_id, "")
            # 最终投递：格式化并发送完整消息。
            await self._deliver(chat_id, text, final=True)
            return

        self._buffers.setdefault(chat_id, "")
        self._buffers[chat_id] += delta
        # 增量更新：把部分文本推送给客户端。
        await self._deliver(chat_id, self._buffers[chat_id], final=False)

    async def send(self, msg: OutboundMessage) -> None:
        # 非 streaming 路径保持不变。
        await self._deliver(msg.chat_id, msg.content, final=True)
```

### 配置

按通道启用 streaming：

```json
{
  "channels": {
    "webhook": {
      "enabled": true,
      "streaming": true,
      "allowFrom": ["*"]
    }
  }
}
```

当 `streaming` 为 `false`（默认）或省略时，只会调用 `send()`，没有 streaming 开销。

### BaseChannel Streaming API

| 方法 / 属性 | 说明 |
|-------------------|-------------|
| `async send_delta(chat_id, delta, metadata?)` | 覆盖它以处理流式片段。默认 no-op。 |
| `supports_streaming`（property） | 当配置包含 `streaming: true` 且子类覆盖 `send_delta` 时返回 `True`。 |

## 配置

### 为什么必须使用 Pydantic model

`BaseChannel.is_allowed()` 通过 `getattr(self.config, "allow_from", [])` 读取权限列表。这对 Pydantic model 有效，因为 `allow_from` 是真实 Python 属性，但对普通 `dict` 会**静默失败**。`dict` 没有 `allow_from` 属性，所以 `getattr` 总是返回默认值 `[]`，导致所有消息都被拒绝。

内置通道使用 Pydantic 配置模型（继承自 `nanobot.config.schema.Base`）。插件通道也**必须这么做**。

### 模式

1. 定义一个继承 `nanobot.config.schema.Base` 的 Pydantic model：

```python
from pydantic import Field
from nanobot.config.schema import Base

class WebhookConfig(Base):
    """Webhook channel configuration."""
    enabled: bool = False
    port: int = 9000
    allow_from: list[str] = Field(default_factory=list)
```

`Base` 配置了 `alias_generator=to_camel` 和 `populate_by_name=True`，所以 JSON key 中的 `"allowFrom"` 和 `"allow_from"` 都可接受。

2. 在 `__init__` 中将 `dict` 转为 model：

```python
from typing import Any
from nanobot.bus.queue import MessageBus

class WebhookChannel(BaseChannel):
    def __init__(self, config: Any, bus: MessageBus):
        if isinstance(config, dict):
            config = WebhookConfig(**config)
        super().__init__(config, bus)
```

3. 用属性方式访问配置，不要用 `.get()`：

```python
async def start(self) -> None:
    port = self.config.port
    token = self.config.token
```

`allowFrom` 会由 `_handle_message()` 自动处理，你不需要自己检查。

覆盖 `default_config()`，让 `nanobot onboard` 自动填充 `config.json`：

```python
@classmethod
def default_config(cls) -> dict[str, Any]:
    return WebhookConfig().model_dump(by_alias=True)
```

> **注意：** `default_config()` 返回普通 `dict`（不是 Pydantic model），因为它会被序列化到 `config.json`。推荐方式是实例化你的配置模型并调用 `model_dump(by_alias=True)`，这会自动使用 camelCase key（`allowFrom`），并让默认值保持单一事实来源。

如果未覆盖，基类会返回 `{"enabled": false}`。

## 命名约定

| 内容 | 格式 | 示例 |
|------|--------|---------|
| PyPI 包 | `nanobot-channel-{name}` | `nanobot-channel-webhook` |
| Entry point key | `{name}` | `webhook` |
| 配置段 | `channels.{name}` | `channels.webhook` |
| Python 包 | `nanobot_channel_{name}` | `nanobot_channel_webhook` |

## 本地开发

```bash
git clone https://github.com/you/nanobot-channel-webhook
cd nanobot-channel-webhook
pip install -e .
nanobot plugins list    # 应显示 "Webhook" 为 "plugin"
nanobot gateway         # 端到端测试
```

## 验证

```bash
$ nanobot plugins list

  Name       Source    Enabled
  telegram   builtin  yes
  discord    builtin  no
  webhook    plugin   yes
```
