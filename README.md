# xiaomiaoVirtual

`xiaomiaoVirtual` 是一个 QQ 机器人、Vtuber 桌面角色与轻量 Agent 框架逐步融合的项目。

项目由三个主要子系统组成：

1. `xiaomiao`：Python QQ 机器人，基于 NapCat、OneBot 和 Hyper Bot，负责 QQ 消息接入、命令处理、AI 对话、图片能力和群管理。
2. `AuBot`：`xiaomiaoVirtual` 的 Web/桌面 Vtuber 表现层，基于 Electron、Vue、TypeScript、Live2D、VRM、TTS 和口型同步能力。
3. `nanobot`：轻量 Python Agent 框架，提供 Agent Loop、多平台 Channels、工具调用、记忆、会话管理、OpenAI 兼容 API 和 WebUI 能力。

当前已打通统一 Agent 链路：`AuBot stage-web` 的网页输入、`xiaomiao` 桌面 bridge 和 QQ 群/私聊普通 AI 回复都会进入同一个 `xiaomiaoAgent` 能力层。`xiaomiao` 在本机暴露 OpenAI 兼容 bridge，`stage-web` 通过 bridge 发消息，QQ 自然语言回复也通过同一个 `agent_backend` 调用 `xiaomiaoAgent` API。

命令型 QQ 功能仍保留在 `xiaomiao` 中，包括权限管理、生图、撤回、配置类命令和部分搜索分支。`AuBot` 继续作为 Web/桌面 Vtuber 表现层，消费统一回复并同步聊天历史、字幕、语音和口型。

## 架构概览

```text
AuBot stage-web 文本/语音输入
    ↓ HTTP :5519
xiaomiao desktop_bridge.py
    ↓
xiaomiao agent_backend.py
    ↓ HTTP :8900
xiaomiaoAgent OpenAI-compatible API
    ↓
xiaomiaoAgent Tools / Memory / Session
    ↓
stage-web 聊天历史 / 错误消息

QQ 用户 / 群消息
    ↓
NapCat OneBot WebSocket :5004
    ↓
xiaomiao/main.py
    ├── 命令型功能：仍由 xiaomiao 本地处理
    └── 普通 AI 回复：agent_backend.py → xiaomiaoAgent API :8900

AuBot stage-tamagotchi 桌面端
    ↓
读取 xiaomiao bridge state / 本地 bridge 回复
    ↓
字幕 / 聊天历史 / TTS / Live2D 口型同步
```

## 目录说明

```text
xiaomiaoVirtual/
├── xiaomiao/       # QQ 机器人主体
├── AuBot/          # xiaomiaoVirtual Web/桌面 Vtuber 表现层
├── nanobot/        # 轻量 Agent 框架与 WebUI
├── docs/           # 项目文档、启动说明和融合计划
├── test/           # 项目统一测试目录
├── README.md       # 项目入口说明
└── TECHNICAL.md    # 技术分析文档
```

## 快速启动

### 0. 一键启动

主目录提供统一启动脚本，会依次启动 QQ 协议端、`xiaomiao/main.py`、`xiaomiaoAgent` API 和 `AuBot stage-web`：

```powershell
cd F:\xiaomiaoVirtual
start-all.cmd
```

只检查依赖路径，不启动窗口：

```powershell
start-all.cmd --check
```

### 1. 启动 xiaomiaoAgent API

`stage-web`、桌面 bridge 和 QQ 普通 AI 回复都依赖该 API：

```powershell
cd F:\xiaomiaoVirtual
conda activate xiaomiao
xiaomiao serve --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

默认监听：

- xiaomiaoAgent OpenAI 兼容 API：`127.0.0.1:8900`

### 2. 启动 QQ / xiaomiao bridge

进入 `xiaomiao`：

```powershell
cd F:\xiaomiaoVirtual\xiaomiao
conda activate xiaomiao
python main.py
```

运行前需要先启动 NapCat，并确保 `xiaomiao/config.json` 中的 OneBot 连接配置指向本机 NapCat WebSocket。`python main.py` 会先启动本地 bridge，然后继续连接 OneBot；如果 NapCat 未启动或 WebSocket 配置不一致，程序会在 `Listener.run()` 阶段退出，bridge 也会随进程结束。

默认关键端口：

- NapCat OneBot WebSocket：`127.0.0.1:5004`
- 小喵桌面桥接服务：`127.0.0.1:5519`

### 3. 启动 AuBot Web 或桌面端

进入 `AuBot`：

```powershell
corepack enable
corepack prepare pnpm@10.33.0 --activate
pnpm install
pnpm dev:web
```

或启动 Electron 桌面端：

```powershell
pnpm dev:tamagotchi
```

`stage-web` 会把文本输入和录音转文字结果发送到 `xiaomiao` bridge；桌面端会读取 bridge state，并将机器人回复同步到 Vtuber 表现层。

## 核心能力

- QQ 群聊与私聊消息接入。
- QQ 普通 AI 对话统一进入 xiaomiaoAgent。
- `stage-web` 文本输入和语音转文字入口统一进入 xiaomiao bridge。
- 人设切换：女朋友、姐姐、妈妈、高级程序员。
- 图片理解、图片生成、名言图片生成。
- 群管理和定时消息。
- 本地 OpenAI 兼容桥接接口。
- xiaomiaoAgent OpenAI 兼容 API、统一 session 和记忆/工具能力层。
- Electron 桌面 Vtuber 展示。
- Live2D / VRM 模型渲染。
- TTS 语音播报。
- Live2D 口型同步。
- 字幕和聊天历史同步。
- xiaomiaoAgent Loop 与多轮任务执行能力。
- xiaomiaoAgent 工具系统、MCP、Web 搜索、Cron 和记忆系统。
- Web、桌面 bridge 和 QQ 普通 AI 回复已统一到 xiaomiaoAgent。

## 关键文件

`xiaomiao`：

- `main.py`：QQ 机器人主入口，包含事件监听、命令解析、AI 回复和桥接启动。
- `desktop_bridge.py`：本地 OpenAI 兼容桥接服务。
- `agent_backend.py`：调用 xiaomiaoAgent OpenAI 兼容 API 的统一 Agent backend。
- `GoogleAI.py`：OpenAI 兼容模型调用封装。
- `SearchOnline.py`：备用模型调用封装。
- `prerequisites.py`：人设提示词和角色选择。
- `config.json`：QQ Bot、OneBot、人设和本地命令配置；统一模型配置在主目录 `config.json`。

`AuBot`：

- `apps/stage-tamagotchi`：Electron 桌面端入口。
- `apps/stage-web/src/pages/index.vue`：stage-web 页面级语音转文字入口，发送到 xiaomiao bridge。
- `packages/stage-layouts/src/xiaomiao-bridge.ts`：stage-web 本地 bridge client。
- `packages/stage-layouts/src/components/Widgets/ChatArea.vue`：桌面布局文本聊天入口，Web 模式发送到 bridge。
- `packages/stage-layouts/src/components/Layouts/MobileInteractiveArea.vue`：移动布局文本聊天入口，Web 模式发送到 bridge。
- `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.ts`：读取小喵桥接状态。
- `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.ts`：把桥接回复分发到字幕、聊天历史和语音。
- `apps/stage-tamagotchi/src/renderer/stores/chat-sync.ts`：桌面聊天同步和小喵桥接调用。
- `packages/stage-ui/src/components/scenes/Stage.vue`：Vtuber 舞台、TTS 和口型同步。
- `packages/stage-ui-live2d`：Live2D 组件与状态管理。
- `packages/model-driver-lipsync`：口型同步模型驱动。

`nanobot` / `xiaomiaoAgent`：

- `nanobot/agent/loop.py`：Agent 主循环，负责上下文构建和 turn 协调。
- `nanobot/agent/runner.py`：LLM 对话循环、工具调用和流式响应执行器。
- `nanobot/channels/`：Telegram、Discord、Slack、Feishu、QQ、WeChat、WebSocket 等通道适配。
- `nanobot/agent/tools/`：文件系统、Shell、Web、MCP、Cron、Notebook、Subagent 等工具能力。
- `nanobot/agent/memory.py`：会话记忆和 Dream 两阶段记忆整理。
- `nanobot/webui/`：React/Vite WebUI，通过 gateway 与后端通信。

## xiaomiaoAgent 接入状态

`nanobot` 代码包当前以用户可见品牌 `xiaomiaoAgent` 运行，通过 OpenAI 兼容 API 接入，不直接由 `xiaomiao` import AgentLoop。模型、provider 和中转站 API 配置统一写在主目录 `config.json` 的 `nanobot` 段：

```json
{
  "nanobot": {
    "provider": "custom",
    "model": "deepseek-v4-flash",
    "providers": {
      "custom": {
        "apiKey": "你的中转站密钥",
        "baseUrl": "https://你的中转站地址/v1"
      }
    }
  },
  "nanobot_agent": {
    "enabled": true,
    "base_url": "http://127.0.0.1:8900/v1/chat/completions",
    "model": "",
    "session_id": "xiaomiao-unified",
    "timeout_seconds": 30
  }
}
```

统一请求链路：

```text
AuBot stage-web 文本/语音输入
    ↓ HTTP POST http://127.0.0.1:5519/v1/chat/completions
xiaomiao desktop_bridge.py
    ↓
xiaomiao agent_backend.py
    ↓ HTTP POST http://127.0.0.1:8900/v1/chat/completions
xiaomiaoAgent OpenAI-compatible API
    ↓ provider=custom, model=nanobot.model
第三方 OpenAI-compatible 中转站
    ↓
xiaomiaoAgent 回复
    ↓
xiaomiao bridge state / stage-web 聊天历史 / 桌面字幕与 TTS

QQ 群/私聊普通 AI 回复
    ↓
NapCat OneBot WebSocket :5004
    ↓
xiaomiao/main.py
    ↓
xiaomiao agent_backend.py
    ↓ HTTP POST http://127.0.0.1:8900/v1/chat/completions
xiaomiaoAgent → 第三方 OpenAI-compatible 中转站
```

配置规则：

1. `nanobot.model` 是最终生效并返回给调用方的模型名。
2. `nanobot.provider` 使用 `custom`，表示任意第三方 OpenAI-compatible 中转站。
3. `nanobot.providers.custom.baseUrl` 填中转站 `/v1` 地址，不要填 `/v1/chat/completions`。
4. `nanobot_agent.base_url` 是 `xiaomiao` 访问本机 xiaomiaoAgent API 的地址，必须保持本机 `8900`。
5. `nanobot_agent.model` 保持空值，避免 `xiaomiao` 请求时覆盖 `nanobot.model`。
6. 修改 `config.json` 后需要重启 `xiaomiaoAgent` 和 `xiaomiao`，web、QQ、桌面端才会加载新配置。

当前边界：

1. `stage-web` 必须走 `xiaomiao` bridge；bridge 不可用时在聊天历史写入明确错误。
2. QQ 群/私聊普通 AI 回复走同一个 `agent_backend`。
3. 命令型功能、权限管理、生图、撤回、配置命令和 `SearchOnline(...)` 分支先保留原逻辑。
4. 统一 session 默认为 `xiaomiao-unified`，避免 Web、QQ、桌面端上下文分裂。

## 文档

- `TECHNICAL.md`：完整技术结构、运行链路、桥接协议、风险和演进建议。
- `docs/STARTUP.md`：本地启动步骤、端口、验证和常见问题。
- `docs/xiaomiao/README.md`：QQ 机器人部署和功能说明。
- `docs/AuBot/README.md`：AuBot / xiaomiaoVirtual 表现层启动和模块说明。
- `docs/plans/2026-05-12-xiaomiao-console-fusion.md`：小喵控制台与 xiaomiaoAgent 融合路线计划。

## 安全注意

不要把真实 API Key、机器人账号凭据或生产配置提交到仓库。主目录 `config.json` 是本地私有配置；仓库内只保留 `config.example.json` 作为结构示例。
