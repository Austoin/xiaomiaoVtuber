# WebSocket 服务端通道

Nanobot 可以作为 WebSocket 服务端运行，让外部客户端（Web 应用、CLI、脚本）通过持久连接实时与 agent 交互。

## 功能

- 基于 WebSocket 的双向实时通信。
- 支持流式输出，可以逐 token 接收 agent 回复。
- 基于 token 的认证，支持静态 token 和短生命周期签发 token。
- 多聊天复用，一个连接可以同时运行多个 `chat_id`。
- 支持 TLS/SSL（WSS），并强制最低 TLSv1.2。
- 通过 `allowFrom` 配置客户端允许列表。
- 自动清理失效连接。

## 快速开始

### 1. 配置

在 `config.json` 的 `channels.websocket` 下添加：

```json
{
  "channels": {
    "websocket": {
      "enabled": true,
      "host": "127.0.0.1",
      "port": 8765,
      "path": "/",
      "websocketRequiresToken": false,
      "allowFrom": ["*"],
      "streaming": true
    }
  }
}
```

### 2. 启动 nanobot

```bash
nanobot gateway
```

你应该看到：

```text
WebSocket server listening on ws://127.0.0.1:8765/
```

### 3. 连接客户端

```bash
# 使用 websocat
websocat ws://127.0.0.1:8765/?client_id=alice

# 使用 Python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:8765/?client_id=alice") as ws:
        ready = json.loads(await ws.recv())
        print(ready)  # {"event": "ready", "chat_id": "...", "client_id": "alice"}
        await ws.send(json.dumps({"content": "Hello nanobot!"}))
        reply = json.loads(await ws.recv())
        print(reply["text"])

asyncio.run(main())
```

## 连接 URL

```text
ws://{host}:{port}{path}?client_id={id}&token={token}
```

| 参数 | 是否必填 | 说明 |
|-----------|----------|-------------|
| `client_id` | 否 | 用于 `allowFrom` 授权的标识。如果省略，会自动生成为 `anon-xxxxxxxxxxxx`。最长保留 128 个字符。 |
| `token` | 条件必填 | 认证 token。当 `websocketRequiresToken` 为 `true` 或配置了静态密钥 `token` 时必填。 |

## 传输协议

所有帧都是 JSON 文本。每条消息都有一个 `event` 字段。

### Server → Client

**`ready`** - 连接建立后立即发送：

```json
{
  "event": "ready",
  "chat_id": "uuid-v4",
  "client_id": "alice"
}
```

**`message`** - 完整 agent 回复：

```json
{
  "event": "message",
  "chat_id": "uuid-v4",
  "text": "Hello! How can I help?",
  "media": ["/tmp/image.png"],
  "reply_to": "msg-id"
}
```

`media` 和 `reply_to` 只会在适用时出现。

**`delta`** - 流式文本片段（仅当 `streaming: true` 时）：

```json
{
  "event": "delta",
  "chat_id": "uuid-v4",
  "text": "Hello",
  "stream_id": "s1"
}
```

**`stream_end`** - 表示一个流式片段结束：

```json
{
  "event": "stream_end",
  "chat_id": "uuid-v4",
  "stream_id": "s1"
}
```

**`attached`** - 对 `new_chat` / `attach` 入站 envelope 的确认（见[多聊天复用](#多聊天复用)）：

```json
{"event": "attached", "chat_id": "uuid-v4"}
```

**`error`** - 入站 envelope 格式错误时的软错误。连接会保持打开：

```json
{"event": "error", "detail": "invalid chat_id"}
```

### Client → Server

**旧版格式（默认聊天）：** 发送普通字符串，或包含可识别文本字段的 JSON 对象：

```json
"Hello nanobot!"
```

```json
{"content": "Hello nanobot!"}
```

可识别字段：`content`、`text`、`message`，按此顺序检查。无效 JSON 会作为纯文本处理。这些帧会路由到连接的默认 `chat_id`，即 `ready` 中声明的那个。

**Typed envelope（多聊天）：** 任何带字符串 `type` 字段的 JSON 对象都是 typed envelope：

| `type` | 字段 | 效果 |
|--------|--------|--------|
| `new_chat` | 无 | 服务端生成新的 `chat_id`，订阅该连接，并回复 `attached`。 |
| `attach` | `chat_id` | 订阅已有 `chat_id`，例如页面刷新后恢复。回复 `attached`。 |
| `message` | `chat_id`, `content` | 向 `chat_id` 发送 `content`。首次使用会自动 attach，不需要显式 `attach`。 |

完整流程见[多聊天复用](#多聊天复用)。

## 配置参考

所有字段都位于 `config.json` 的 `channels.websocket` 下。

### 连接

| 字段 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `enabled` | bool | `false` | 启用 WebSocket 服务端。 |
| `host` | string | `"127.0.0.1"` | 绑定地址。使用 `"0.0.0.0"` 可接受外部连接。 |
| `port` | int | `8765` | 监听端口。 |
| `path` | string | `"/"` | WebSocket upgrade 路径。尾部斜杠会规范化（根路径 `/` 会保留）。 |
| `maxMessageBytes` | int | `37748736` | 最大入站消息大小，单位字节（1 KB - 40 MB）。默认值 36 MB，可接受最多 4 个 8 MB 的 base64 编码图片附件；如果通道只传文本，可以降低该值。 |

### 认证

| 字段 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `token` | string | `""` | 静态共享密钥。设置后，客户端必须提供与该密钥匹配的 `?token=<value>`（使用 timing-safe 比较）。签发 token 也会作为 fallback 被接受。 |
| `websocketRequiresToken` | bool | `true` | 当为 `true` 且未配置静态 `token` 时，客户端仍必须提供有效签发 token。设为 `false` 可允许免认证连接，只适合本地或可信网络。 |
| `tokenIssuePath` | string | `""` | 签发短生命周期 token 的 HTTP 路径。必须不同于 `path`。见 [Token 签发](#token-签发)。 |
| `tokenIssueSecret` | string | `""` | 通过签发端点获取 token 所需的密钥。如果为空，任何客户端都可以获取 token，并会记录警告。 |
| `tokenTtlS` | int | `300` | 签发 token 的存活时间，单位秒（30 - 86,400）。 |

### 访问控制

| 字段 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `allowFrom` | string 列表 | `["*"]` | 允许的 `client_id` 值。`"*"` 允许所有，`[]` 拒绝所有。 |

### 流式输出

| 字段 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `streaming` | bool | `true` | 启用流式模式。agent 会发送 `delta` + `stream_end` 帧，而不是单个 `message`。 |

### Keep-alive

| 字段 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `pingIntervalS` | float | `20.0` | WebSocket ping 间隔，单位秒（5 - 300）。 |
| `pingTimeoutS` | float | `20.0` | 关闭连接前等待 pong 的时间，单位秒（5 - 300）。 |

### TLS/SSL

| 字段 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `sslCertfile` | string | `""` | TLS 证书文件路径（PEM）。必须同时设置 `sslCertfile` 和 `sslKeyfile` 才能启用 WSS。 |
| `sslKeyfile` | string | `""` | TLS 私钥文件路径（PEM）。最低 TLS 版本会强制为 TLSv1.2。 |

## Token 签发

生产部署中，如果 `websocketRequiresToken: true`，请使用短生命周期 token，而不是把静态密钥嵌入客户端。

### 工作原理

1. 客户端发送 `GET {tokenIssuePath}`，并携带 `Authorization: Bearer {tokenIssueSecret}` 或 `X-Nanobot-Auth` header。
2. 服务端返回一个一次性 token：

```json
{"token": "nbwt_aBcDeFg...", "expires_in": 300}
```

3. 客户端使用 `?token=nbwt_aBcDeFg...&client_id=...` 打开 WebSocket。
4. token 会被消费（单次使用），不能复用。

### 示例配置

```json
{
  "channels": {
    "websocket": {
      "enabled": true,
      "port": 8765,
      "path": "/ws",
      "tokenIssuePath": "/auth/token",
      "tokenIssueSecret": "your-secret-here",
      "tokenTtlS": 300,
      "websocketRequiresToken": true,
      "allowFrom": ["*"],
      "streaming": true
    }
  }
}
```

客户端流程：

```bash
# 1. 获取 token
curl -H "Authorization: Bearer your-secret-here" http://127.0.0.1:8765/auth/token

# 2. 使用 token 连接
websocat "ws://127.0.0.1:8765/ws?client_id=alice&token=nbwt_aBcDeFg..."
```

### 限制

- 签发 token 是单次使用的，每个 token 只能完成一次握手。
- 未使用 token 数量上限为 10,000。超过后请求会返回 HTTP 429。
- 过期 token 会在每次签发或验证请求时惰性清理。

## 多聊天复用

单个 WebSocket 可以承载多个并发聊天。服务端以 fan-out 集合形式跟踪 `chat_id -> {connections}`，因此同一个聊天也可以镜像到多个连接，例如两个浏览器标签页。

### 典型流程（带侧边栏的 Web UI）

```text
client                                server
  | --- connect -------------------->  |
  | <-- {"event":"ready",              |
  |      "chat_id":"d3..."}   (default)|
  |                                     |
  | --- {"type":"new_chat"} --------->  |
  | <-- {"event":"attached",            |
  |      "chat_id":"a1..."}             |
  |                                     |
  | --- {"type":"message",              |
  |      "chat_id":"a1...",             |
  |      "content":"hi"} ------------>  |
  | <-- {"event":"delta", ...}          |
  | <-- {"event":"stream_end", ...}     |
  |                                     |
  | --- {"type":"attach",               |  # after page reload
  |      "chat_id":"a1..."} --------->  |
  | <-- {"event":"attached", ...}       |
```

### 规则

- 每个出站事件都携带 `chat_id`。客户端必须按该字段分发。
- `chat_id` 格式：`^[A-Za-z0-9_:-]{1,64}$`。不匹配的值会返回 `error`。
- `message` 首次使用时会自动 attach。同一连接上由服务端生成（`new_chat`）的聊天，不需要单独 `attach`。
- 错误（无效 envelope、未知 `type`、错误 `chat_id`）是软错误：服务端回复 `{"event":"error","detail":"..."}` 并保持连接打开。

### 向后兼容

只发送纯文本或 `{"content": ...}` 的旧版客户端会保持原样工作。这些帧会路由到连接的默认 `chat_id`，即来自 `ready` 的那个。不需要配置开关。

### 安全边界

`chat_id` 是一种 *capability*：任何持有有效 WebSocket 认证凭据和该 chat_id 的调用方，都可以 attach 到该对话并查看输出。这对 nanobot 的本地单用户模型是安全的。多租户部署应为每个用户命名空间化 chat_id，或引入每租户认证网关；nanobot 当前不提供这一点。

## 安全说明

- **Timing-safe 比较**：静态 token 校验使用 `hmac.compare_digest`，防止时序攻击。
- **纵深防御**：`allowFrom` 会在 HTTP 握手层和消息层同时检查。
- **chat_id 作为 capability**：见[多聊天复用](#多聊天复用)。WebSocket 握手认证是唯一防线，通过认证的调用方可以 attach 到任何已知 chat_id。
- **TLS 强制**：启用 SSL 时，最低允许 TLSv1.2。
- **默认安全**：`websocketRequiresToken` 默认是 `true`。只有在可信网络中才应显式设为 `false`。

## 媒体文件

出站 `message` 事件可能包含 `media` 字段，其中是本地文件系统路径。远程客户端不能直接访问这些文件，需要满足以下任一条件：

- 共享文件系统挂载。
- 提供 nanobot 媒体目录的 HTTP 文件服务器。

## 常见模式

### 可信本地网络（无认证）

```json
{
  "channels": {
    "websocket": {
      "enabled": true,
      "host": "0.0.0.0",
      "port": 8765,
      "websocketRequiresToken": false,
      "allowFrom": ["*"],
      "streaming": true
    }
  }
}
```

### 静态 token（简单认证）

```json
{
  "channels": {
    "websocket": {
      "enabled": true,
      "token": "my-shared-secret",
      "allowFrom": ["alice", "bob"]
    }
  }
}
```

客户端使用 `?token=my-shared-secret&client_id=alice` 连接。

### 使用签发 token 的公共端点

```json
{
  "channels": {
    "websocket": {
      "enabled": true,
      "host": "0.0.0.0",
      "port": 8765,
      "path": "/ws",
      "tokenIssuePath": "/auth/token",
      "tokenIssueSecret": "production-secret",
      "websocketRequiresToken": true,
      "sslCertfile": "/etc/ssl/certs/server.pem",
      "sslKeyfile": "/etc/ssl/private/server-key.pem",
      "allowFrom": ["*"]
    }
  }
}
```

### 自定义路径

```json
{
  "channels": {
    "websocket": {
      "enabled": true,
      "path": "/chat/ws",
      "allowFrom": ["*"]
    }
  }
}
```

客户端连接到 `ws://127.0.0.1:8765/chat/ws?client_id=...`。尾部斜杠会规范化，所以 `/chat/ws/` 的效果相同。
