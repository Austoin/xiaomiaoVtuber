# OpenAI 兼容 API

xiaomiaoAgent 默认绑定 `127.0.0.1:8900`，是 QQ、Stage Web、Pocket 和 Electron 的唯一 Agent HTTP 层。

## 启动

```powershell
python -m xiaomiao_agent serve --config ..\.cache\agent\nanobot\config.json
```

## 路由

| 路由 | 方法 | 说明 |
| --- | --- | --- |
| `/health` | GET | 健康状态 |
| `/v1/models` | GET | 固定模型信息 |
| `/v1/chat/completions` | POST | 聊天、媒体和工具执行 |
| `/v1/xiaomiao/events` | GET/POST | 跨端事件同步与 Stage 动作 |
| `/v1/xiaomiao/config` | GET/POST | 统一 Provider 配置状态和更新 |

## 聊天请求

每次请求必须包含一条 `user` 消息。`session_id` 用于会话隔离；项目四端使用 `xiaomiao-unified`。

```json
{
  "session_id": "xiaomiao-unified",
  "channel": "web",
  "chat_id": "stage-client",
  "user_id": "stage-client",
  "client_message_id": "stage-web-1",
  "messages": [
    { "role": "user", "content": "你好" }
  ]
}
```

QQ 请求还可以传递：

```json
{
  "tool_policy": "low_risk|trusted_pending|trusted_confirmed",
  "confirmation_id": "ABC123"
}
```

权限只由可信通道适配器设置。`ToolRegistry` 在实际执行前仍会校验工具策略。

## 图片

支持 OpenAI 多模态 data URL：

```json
{
  "messages": [{
    "role": "user",
    "content": [
      { "type": "text", "text": "描述图片" },
      { "type": "image_url", "image_url": { "url": "data:image/png;base64,..." } }
    ]
  }]
}
```

远程图片 URL 不被接受。也可以使用 `multipart/form-data` 上传文件。

## 事件

查询增量事件：

```text
GET /v1/xiaomiao/events?after=10&user_id=42
```

发布结构化事件：

```json
{
  "source": "xiaomiao-agent-tool",
  "channel": "qq-group",
  "chat_id": "10001",
  "user_id": 42,
  "role": "assistant",
  "content": "动作已执行",
  "event_type": "tool_finish",
  "tool_name": "xiaomiao_stage"
}
```

## 配置

`GET /v1/xiaomiao/config` 只返回是否已配置，不返回密钥。`POST` 接受：

```json
{
  "apiKey": "...",
  "baseUrl": "https://api.example.com/v1",
  "model": "model-name"
}
```

## 错误

- 无效请求返回 `400`。
- Agent 超时返回 `504`。
- Agent 空回复返回 `502`，不重试、不伪造兜底文本。
- 内部处理失败返回 `500`。
- 浏览器 CORS 只允许本机 Origin。
