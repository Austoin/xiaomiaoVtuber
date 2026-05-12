# xiaomiaoVirtual

`xiaomiaoVirtual` 是一个 QQ 机器人与 Vtuber 桌面角色初步结合的项目。

项目由两个主要子系统组成：

1. `xiaomiao`：Python QQ 机器人，基于 NapCat、OneBot 和 Hyper Bot，负责 QQ 消息接入、命令处理、AI 对话、图片能力和群管理。
2. `AuBot`：Project AIRI 桌面端/多端虚拟角色工程，基于 Electron、Vue、TypeScript、Live2D、VRM、TTS 和口型同步能力。

两者通过本地 HTTP 桥接服务连接：`xiaomiao` 在本机暴露 OpenAI 兼容接口，`AuBot` 的 Electron 桌面端读取并消费机器人回复，把文本同步到字幕、聊天历史、语音播报和 Live2D 口型。

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
```

## 目录说明

```text
xiaomiaoVirtual/
├── xiaomiao/       # QQ 机器人主体
├── AuBot/          # AIRI / Vtuber 桌面端与多端 monorepo
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

## 文档

- `TECHNICAL.md`：完整技术结构、运行链路、桥接协议、风险和演进建议。
- `docs/xiaomiao/README.md`：QQ 机器人部署和功能说明。
- `docs/AuBot/README.md`：AIRI monorepo 启动和模块说明。

## 安全注意

不要把真实 API Key、机器人账号凭据或生产配置提交到仓库。当前项目配置应优先迁移到本地私有配置或环境变量中。
