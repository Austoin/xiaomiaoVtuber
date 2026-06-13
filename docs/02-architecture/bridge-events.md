# Bridge Event 协议

Bridge event 是 xiaomiao、xiaomiaoAgent、stage-web、stage-tamagotchi 和 stage-pocket 之间共享动作结果的本地事件流。

## 用途

| 场景 | 作用 |
|------|------|
| QQ 普通对话 | 把用户消息和助手回复写入统一事件 |
| Agent 工具调用 | 展示工具开始、完成、错误和确认请求 |
| 记忆命令 | 同步记忆状态、整理和恢复结果 |
| 舞台动作 | 触发字幕、TTS、表情、背景、模型切换 |
| 移动端同步 | stage-pocket 只读查看聊天和工具事件 |

## 存储位置

默认事件文件：

```text
xiaomiao/runtime/bridge_events.jsonl
```

可通过环境变量覆盖：

```powershell
set XIAOMIAO_BRIDGE_EVENT_STORE=<项目根目录>\workspace\tmp\bridge_events.jsonl
```

运行态事件文件不应提交到仓库。

## HTTP 接口

bridge 服务由 `xiaomiao/main.py` 启动，默认监听：

```text
http://127.0.0.1:5519
```

常用接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/v1/xiaomiao/status` | bridge 状态 |
| `GET` | `/v1/xiaomiao/state?user_id=3554978979` | 最近助手回复 |
| `GET` | `/v1/xiaomiao/events?after=0` | 查询事件流 |
| `GET` | `/v1/xiaomiao/events?after=0&user_id=3554978979` | 查询指定用户事件 |
| `POST` | `/v1/xiaomiao/events` | 写入本地事件 |
| `POST` | `/v1/chat/completions` | OpenAI 兼容 bridge 聊天入口 |

bridge 只接受本机 loopback 客户端。

## 事件字段

必填字段：

| 字段 | 说明 |
|------|------|
| `id` | 本地递增事件 ID |
| `source` | 来源，例如 `qq-group`、`agent-webui`、`xiaomiao-agent-tool` |
| `channel` | 通道，例如 `qq-group`、`qq-private`、`agent-webui` |
| `chat_id` | 群号、私聊用户号或会话 ID |
| `user_id` | QQ 用户或本地用户 ID |
| `role` | `user` 或 `assistant` |
| `content` | 事件正文 |
| `timestamp` | 秒级时间戳 |

自动补充字段：

| 字段 | 说明 |
|------|------|
| `schema_version` | 当前为 `1` |
| `conversation_id` | 默认 `{channel}:{chat_id}` |
| `message_id` | 默认 `bridge:{id}` 或 `client:{client_message_id}:{role}` |

可选字段：

| 字段 | 说明 |
|------|------|
| `client_message_id` | 前端或调用方传入的消息 ID |
| `event_type` | 事件类型 |
| `tool_name` | 工具名 |
| `risk_level` | `low`、`medium`、`high` |
| `confirmation_id` | 高风险确认码 |
| `result_summary` | 工具或动作摘要 |

## 事件类型

| 类型 | 说明 |
|------|------|
| `chat` | 普通聊天 |
| `tool_start` | 工具开始 |
| `tool_finish` | 工具完成 |
| `tool_error` | 工具失败 |
| `confirmation_requested` | 请求用户二次确认 |
| `memory_update` | 记忆更新 |
| `stage_action` | 舞台动作 |

当前空值或 `chat` 会更新桌面端最近回复状态；其它事件主要进入事件流展示。

## 写入示例

```json
{
  "source": "qq-group",
  "channel": "qq-group",
  "chat_id": "10001",
  "user_id": 3554978979,
  "role": "assistant",
  "content": "检测到高风险工具请求，需要二次确认。",
  "event_type": "confirmation_requested",
  "tool_name": "exec",
  "risk_level": "high",
  "confirmation_id": "ABC123",
  "result_summary": "等待确认"
}
```

舞台动作示例：

```json
{
  "source": "xiaomiao-agent-tool",
  "channel": "qq-group",
  "chat_id": "10001",
  "user_id": 3554978979,
  "role": "assistant",
  "content": "{\"service\":\"stage\",\"action\":\"say\",\"payload\":{\"text\":\"你好\"}}",
  "event_type": "stage_action",
  "tool_name": "xiaomiao_stage",
  "risk_level": "high",
  "result_summary": "say"
}
```

## 消费端

| 消费端 | 行为 |
|--------|------|
| `stage-web` | 同步聊天历史和错误信息 |
| `stage-tamagotchi` | 轮询状态和事件，驱动字幕、TTS、聊天历史、舞台动作 |
| `stage-pocket` | 只读展示聊天、工具、确认、记忆和舞台事件 |
| `xiaomiaoAgent WebUI` | 通过 gateway 会话同步，并镜像到 bridge event |

## 故障边界

- JSONL 某行损坏时，会写入同名 `.invalid.jsonl`，不会静默吞掉。
- 高风险动作失败必须写入 `tool_error` 或明确错误文本。
- bridge 不应暴露到公网，只允许本机访问。
- QQ 上传文件和网页抓取结果都按不可信用户内容处理，不能当作系统指令执行。

