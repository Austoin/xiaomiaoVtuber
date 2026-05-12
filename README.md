# xiaomiaoVirtual

`xiaomiaoVirtual` 是一个 QQ 机器人、Vtuber 桌面角色与轻量 Agent 框架逐步融合的项目。

项目由三个主要子系统组成：

1. `xiaomiao`：Python QQ 机器人，基于 NapCat、OneBot 和 Hyper Bot，负责 QQ 消息接入、命令处理、AI 对话、图片能力和群管理。
2. `AuBot`：Project AIRI 桌面端/多端虚拟角色工程，基于 Electron、Vue、TypeScript、Live2D、VRM、TTS 和口型同步能力。
3. `nanobot`：轻量 Python Agent 框架，提供 Agent Loop、多平台 Channels、工具调用、记忆、会话管理、OpenAI 兼容 API 和 WebUI 能力。

当前已打通 `xiaomiao` 与 `AuBot` 的本地 HTTP 桥接：`xiaomiao` 在本机暴露 OpenAI 兼容接口，`AuBot` 的 Electron 桌面端读取并消费机器人回复，把文本同步到字幕、聊天历史、语音播报和 Live2D 口型。

后续计划把 `nanobot` 的 Agent、工具、记忆、多通道和 WebUI 能力逐步融合进来，让小喵从“QQ Bot + 桌面角色”演进为“多通道个人 Agent + Vtuber 表现层”。

## 架构概览

```text
QQ 用户 / 群消息
    ↓
NapCat OneBot WebSocket :5004
    ↓
xiaomiao/main.py
    ↓
OpenAI-compatible LLM / DeepSeek / Gemini 中转
    ↓
xiaomiao/desktop_bridge.py :5519
    ↓
AuBot apps/stage-tamagotchi
    ↓
字幕 / 聊天历史 / TTS / Live2D 口型同步

nanobot
    ├── Agent Loop / Agent Runner
    ├── Tools / MCP / Web Search / Cron
    ├── Memory / Session Management
    ├── Channels / OpenAI-compatible API
    └── WebUI / Gateway
```

## 目录说明

```text
xiaomiaoVirtual/
├── xiaomiao/       # QQ 机器人主体
├── AuBot/          # AIRI / Vtuber 桌面端与多端 monorepo
├── nanobot/        # 轻量 Agent 框架与 WebUI
├── docs/           # 项目文档、启动说明和融合计划
├── test/           # 项目统一测试目录
├── README.md       # 项目入口说明
└── TECHNICAL.md    # 技术分析文档
```

## 快速启动

### 1. 启动 QQ 机器人

进入 `xiaomiao`：

```powershell
pip install -r requirements.txt
python main.py
```

运行前需要先启动 NapCat，并确保 `config.json` 中的 OneBot 连接配置指向本机 NapCat WebSocket。

默认关键端口：

- NapCat OneBot WebSocket：`127.0.0.1:5004`
- 小喵桌面桥接服务：`127.0.0.1:5519`

### 2. 启动 Vtuber 桌面端

进入 `AuBot`：

```powershell
corepack enable
corepack prepare pnpm@10.33.0 --activate
pnpm install
pnpm dev:tamagotchi
```

桌面端启动后会读取 `xiaomiao` 的本地桥接接口，并将机器人回复同步到 Vtuber 表现层。

## 核心能力

- QQ 群聊与私聊消息接入。
- AI 对话与多轮上下文。
- 人设切换：女朋友、姐姐、妈妈、高级程序员。
- 图片理解、图片生成、名言图片生成。
- 群管理和定时消息。
- 本地 OpenAI 兼容桥接接口。
- Electron 桌面 Vtuber 展示。
- Live2D / VRM 模型渲染。
- TTS 语音播报。
- Live2D 口型同步。
- 字幕和聊天历史同步。
- nanobot Agent Loop 与多轮任务执行能力。
- nanobot 工具系统、MCP、Web 搜索、Cron 和记忆系统。
- 后续可统一 QQ、WebUI、WebSocket 等多通道入口。

## 关键文件

`xiaomiao`：

- `main.py`：QQ 机器人主入口，包含事件监听、命令解析、AI 回复和桥接启动。
- `desktop_bridge.py`：本地 OpenAI 兼容桥接服务。
- `GoogleAI.py`：OpenAI 兼容模型调用封装。
- `SearchOnline.py`：备用模型调用封装。
- `prerequisites.py`：人设提示词和角色选择。
- `config.json`：机器人、模型和连接配置。

`AuBot`：

- `apps/stage-tamagotchi`：Electron 桌面端入口。
- `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.ts`：读取小喵桥接状态。
- `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.ts`：把桥接回复分发到字幕、聊天历史和语音。
- `apps/stage-tamagotchi/src/renderer/stores/chat-sync.ts`：桌面聊天同步和小喵桥接调用。
- `packages/stage-ui/src/components/scenes/Stage.vue`：Vtuber 舞台、TTS 和口型同步。
- `packages/stage-ui-live2d`：Live2D 组件与状态管理。
- `packages/model-driver-lipsync`：口型同步模型驱动。

`nanobot`：

- `nanobot/agent/loop.py`：Agent 主循环，负责上下文构建和 turn 协调。
- `nanobot/agent/runner.py`：LLM 对话循环、工具调用和流式响应执行器。
- `nanobot/channels/`：Telegram、Discord、Slack、Feishu、QQ、WeChat、WebSocket 等通道适配。
- `nanobot/agent/tools/`：文件系统、Shell、Web、MCP、Cron、Notebook、Subagent 等工具能力。
- `nanobot/agent/memory.py`：会话记忆和 Dream 两阶段记忆整理。
- `nanobot/webui/`：React/Vite WebUI，通过 gateway 与后端通信。

## nanobot 融合方向

`nanobot` 暂时作为独立子系统保留，后续按低风险顺序融合：

1. 只读接入：在小喵控制台展示 nanobot gateway、WebUI、会话和通道状态。
2. 能力复用：让 `xiaomiao` 可调用 nanobot 的工具、记忆和 Web 搜索能力。
3. 通道统一：评估是否把 QQ、WebSocket、WebUI 等入口收敛到 nanobot 的 Channel/MessageBus 模型。
4. 表现统一：AuBot 继续作为 Vtuber 表现层，消费来自 `xiaomiao` 或 nanobot 的统一回复事件。
5. 渐进替换：在保留现有 QQ Bot 可运行的前提下，逐步把长任务、工具调用和记忆迁移到 nanobot。

## 文档

- `TECHNICAL.md`：完整技术结构、运行链路、桥接协议、风险和演进建议。
- `docs/STARTUP.md`：本地启动步骤、端口、验证和常见问题。
- `docs/xiaomiao/README.md`：QQ 机器人部署和功能说明。
- `docs/AuBot/README.md`：AIRI monorepo 启动和模块说明。
- `docs/plans/2026-05-12-xiaomiao-console-fusion.md`：小喵控制台与 nanobot 融合路线计划。

## 安全注意

不要把真实 API Key、机器人账号凭据或生产配置提交到仓库。当前项目配置应优先迁移到本地私有配置或环境变量中。
