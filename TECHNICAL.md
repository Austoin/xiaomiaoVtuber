# 技术架构

## 单一 Agent 边界

`xiaomiaoAgent` 是项目唯一具有模型推理、上下文编排、记忆和工具执行职责的组件。

通道层不得：

- 直接调用聊天 Provider。
- 在 Agent 请求失败时回退到本地模型。
- 自行执行 Agent 工具。
- 返回伪造成功或空回复替代文本。

通道层可以保留 TTS、ASR、Live2D、VRM、音频和图像展示能力，这些不属于聊天智能体推理。

## 请求链路

### QQ

```text
NapCat :5004
  -> xiaomiao/main.py
  -> xiaomiao/agent_backend.py
  -> POST xiaomiaoAgent :8900/v1/chat/completions
```

QQ 层负责权限映射、文件/图片转码、OneBot 消息发送和错误展示。Agent API 根据 `channel`、`chat_id`、`user_id` 和 `tool_policy` 执行统一会话。

### Web、Pocket、Electron

```text
stage-ui/libs/xiaomiao-agent.ts
  -> POST :8900/v1/chat/completions
  -> session_id=xiaomiao-unified
```

所有共享聊天、语音转文字后的聊天、视觉推理、自主绘图分析、Spark 通知和 Markdown 压测在线请求都经过该客户端。

### Discord、Telegram、WebUI

这些入口由 `xiaomiaoAgent/nanobot/channels/` 直接托管，共用同一个 `AgentLoop`、`SessionManager` 和工具注册表。内嵌 WebUI 的静态文件由 WebSocket 通道在 `:8765` 提供；Gateway 自身健康端口是 `:18790`。

### Minecraft 与 Twitter

Minecraft 的 Mineflayer 运行时负责游戏连接和动作执行，规划请求统一发送到 `:8900/v1/chat/completions`，不持有 Provider 或 API Key。Twitter 是 Playwright 驱动的 MCP 工具服务，不执行模型推理。两者需要的 MCP 配置由 Agent 工具层加载。

## Agent API

| 路由 | 方法 | 用途 |
| --- | --- | --- |
| `/health` | GET | 服务健康检查 |
| `/v1/models` | GET | 固定 Agent 模型信息 |
| `/v1/chat/completions` | POST | 统一聊天和工具执行 |
| `/v1/xiaomiao/events` | GET/POST | 跨端事件同步与 Stage 动作 |
| `/v1/xiaomiao/config` | GET/POST | 安全配置状态与自定义 Provider 更新 |

API 只允许本机 Web Origin 获得 CORS 响应。空 Agent 回复返回明确 `502`，不会重试或使用兜底文本。

## 工具

工具实现位于：

```text
xiaomiaoAgent/nanobot/agent/tools/
```

核心工具包括文件读写、搜索、Shell、Notebook、Web、MCP、定时任务、消息、子任务、图像生成、MarkItDown、Scrapling 和 Stage/xiaomiaobot 动作。第三方裁剪源码位于 `xiaomiaoAgent/vendor/`。

QQ 只把通道权限映射为 Agent `tool_policy`，不持有工具实现。

## 前端协议包

`xiaomiaobot/packages/core-agent` 仅保留：

- 聊天消息和切片类型。
- Hook/Context/Session 协议。
- 会话消息合并。
- Spark Notify schema 与控制类型。

该包不再包含 Provider LLM runtime 或浏览器 Agent。

## 启动顺序

`scripts/start-all.cmd` 顺序启动：

1. NapCat OneBot `:5004`。
2. xiaomiaoAgent API `:8900`。
3. QQ 通道适配器 `xiaomiao/main.py`。
4. Stage Web `:5175`。

按需服务不由 `start-all` 自动启动：WebUI `:8765`、Twitter MCP `:8080`、Minecraft MCP `:3001`。不存在独立桌面 bridge 端口。

## 失败语义

- HTTP、配置、工具和 Provider 错误必须显式返回。
- 前端把 Agent 请求失败写入聊天 `error` 消息。
- QQ 把失败发送给对应用户/群。
- 事件持久化文件损坏会在加载时抛错，不静默跳过。

## 测试层级

1. Python 单元测试和 API 测试。
2. Ruff、Python 编译检查。
3. 前端契约测试和 Vitest。
4. workspace 类型检查。
5. Web/Electron 构建与本机 API 启动检查。
