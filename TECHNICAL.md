# xiaomiaoVirtual 技术文档

## 1. 项目定位

`xiaomiaoVirtual` 是一个 QQ 机器人、Vtuber 桌面角色和轻量 Agent 框架的融合项目。当前由三个子系统组成：

1. `xiaomiao`：Python QQ 机器人，负责 QQ 消息、命令、人设、模型调用、图片能力、群管理和本地桥接。
2. `xiaomiaobot`：`xiaomiaoVirtual` 的 Electron/Vue Vtuber 表现层，负责 Web/桌面角色、Live2D/VRM、字幕、TTS 和口型同步。内部包名保留 `@proj-airi/*` 兼容标识。
3. `xiaomiaoAgent`：Python Agent 框架，内部包名仍是 `nanobot`，负责 Agent Loop、通道抽象、工具调用、记忆、会话管理、OpenAI 兼容 API、Gateway 和 WebUI。

当前项目已经打通统一 Agent 闭环：`xiaomiaobot stage-web`、`xiaomiao` 桌面 bridge、QQ 群/私聊普通 AI 回复和 `xiaomiaoAgent WebUI` 都会进入同一个 `xiaomiaoAgent` 能力层。QQ 侧已增加 Agent 工具权限网关，普通用户默认 `low_risk`，ROOT/Super/`agent_tool_allowlist` 用户的高风险动作必须二次确认后才会以 `trusted_confirmed` 调用 Agent。命令型 QQ 功能仍由 `xiaomiao` 本地处理，`xiaomiaobot` 继续承担 Web/桌面/移动端表现层。

当前目标不再是“后续引入 Agent”，而是维护清楚的边界：外部入口统一到 `xiaomiao` bridge / `agent_backend`，Agent 能力由 `xiaomiaoAgent` OpenAI 兼容 API 提供，确定性命令继续留在 `xiaomiao`。

## 2. 总体架构

```text
[xiaomiaobot stage-web 文本/语音]
    ↓ HTTP :5519
[xiaomiao desktop_bridge.py]
    ↓
[xiaomiao agent_backend.py]
    ↓ HTTP :8900
[xiaomiaoAgent OpenAI 兼容 API]
    ↓
[AgentLoop / AgentRunner / 工具 / 记忆 / 会话]
    ↓
[stage-web 聊天会话]

[xiaomiaoAgent WebUI :5174]
    ↓ WebSocket
[xiaomiaoAgent 网关 :8765]
    ↓ chat_id=xiaomiao-unified
[xiaomiaoAgent 会话 / 工具 / 记忆]
    ↓ 镜像同步
[xiaomiao 桥接事件 :5519]

[QQ 用户]
    ↓
[NapCat / OneBot WebSocket :5004]
    ↓
[xiaomiao main.py]
    ├── 命令型分支：权限 / 生图 / 撤回 / 配置 / 搜索保留原逻辑
    └── 普通 AI 回复：agent_backend.py → xiaomiaoAgent API :8900

[xiaomiaobot stage-tamagotchi]
    ↓
[xiaomiao 桥接状态 / 本地桥接回复]
    ↓
[字幕 / 聊天历史 / TTS / Live2D LipSync]

[xiaomiaobot stage-pocket]
    ↓
[xiaomiao 桥接事件 :5519]
    ↓
[聊天 / 工具 / 确认 / 记忆 / 舞台事件只读同步]
```

## 3. xiaomiao 子系统

`xiaomiao` 是 QQ 机器人主体，核心入口是 `xiaomiao/main.py`。

主要职责：

- 连接 NapCat 的 OneBot WebSocket。
- 监听群消息、入群、邀请等 QQ 事件。
- 解析命令前缀和 `@机器人` 消息。
- 对 Agent 工具型请求做权限分级、确认码生成和确认码校验。
- 转发中文记忆命令到 xiaomiaoAgent slash command。
- 接收 QQ 群文件上传和 file 消息段，将支持的文档下载到项目 `workspace/downloads/qq/`。
- 根据用户角色选择人设提示词。
- 普通自然语言回复调用 `agent_backend.py`，再转发到 xiaomiaoAgent OpenAI 兼容 API。
- 支持图片识别、图片获取、名言图片、系统状态和群管理。
- 启动本地桌面桥接服务供 xiaomiaobot 消费。

关键文件：

```text
xiaomiao/
├── main.py              # QQ 机器人主入口
├── desktop_bridge.py    # 本地 OpenAI 兼容桥接服务
├── agent_backend.py     # xiaomiaoAgent OpenAI 兼容 API 调用封装
├── qq_agent_tools.py    # QQ Agent 工具策略、确认码和记忆命令映射
├── qq_permissions.py    # ROOT/Super/Agent 工具白名单权限判断
├── qq_workspace.py      # QQ 文件下载、工作区归档和文档转换提示
├── GoogleAI.py          # OpenAI SDK 兼容模型封装
├── SearchOnline.py      # 备用 OpenAI 对话封装
├── prerequisites.py     # 人设和角色选择
├── Quote.py             # 名言图片生成
├── config.json          # 主配置
├── requirements.txt     # Python 依赖
└── runtime/             # 权限、角色、定时消息和黑名单配置
```

## 4. xiaomiaobot 子系统

`xiaomiaobot` 是多端 Vtuber monorepo。当前用户可见品牌为 `xiaomiaoVirtual`；内部包名、目录和 `@proj-airi/*` 标识保留兼容。当前与小喵联动的主要入口包括 `apps/stage-web`、`apps/stage-tamagotchi` 和 `apps/stage-pocket`。

主要职责：

- 在 `stage-web` 中把网页文本输入、移动端输入和页面级录音转文字结果发送到 `xiaomiao` bridge。
- 启动 Electron 桌面角色窗口。
- 渲染 Live2D、VRM 或 Godot stage。
- 管理聊天会话、字幕、TTS 和语音输入。
- 读取 `xiaomiao` 本地桥接状态。
- 把 QQ 机器人回复表现为桌面角色说话、字幕和口型同步。
- 在 stage-pocket 中只读同步 xiaomiao 桥接事件。

关键目录：

```text
xiaomiaobot/
├── apps/stage-tamagotchi/         # Electron 桌面 Vtuber 入口
├── apps/stage-web/                # Web 版 Vtuber 入口
├── apps/stage-pocket/             # 移动端入口，已同步第一批桥接事件
├── packages/stage-layouts/        # stage-web 文本/移动输入和桥接辅助
├── packages/stage-ui/             # 舞台、TTS、聊天、设置等核心 UI/业务
├── packages/stage-ui-live2d/      # Live2D 组件、状态和工具
├── packages/stage-ui-three/       # VRM / Three.js 渲染
├── packages/model-driver-lipsync/ # 口型同步驱动
├── packages/pipelines-audio/      # 音频流水线
└── services/                      # 其他机器人和平台适配
```

## 5. xiaomiaoAgent 子系统

`xiaomiaoAgent` 是一个轻量 Agent 框架，内部 Python 包名仍是 `nanobot`，核心入口包括 `nanobot/cli/commands.py`、`nanobot/nanobot.py` 和网关/WebUI 相关模块。

主要职责：

- 通过 `MessageBus` 解耦外部通道和 Agent 核心。
- 使用 `AgentLoop` 构建上下文、管理会话键、处理 hooks 和轮次生命周期。
- 使用 `AgentRunner` 执行 LLM 对话循环、工具调用和流式响应。
- 支持 Telegram、Discord、Slack、Feishu、Matrix、QQ、WeChat、WebSocket 等通道。
- 提供文件系统、Shell、Web Search/Fetch、MCP、Cron、Notebook、Subagent 等工具能力。
- 提供 `Memory` 和会话管理，支持会话历史、上下文压缩和 Dream 两阶段记忆整理。
- 提供 React/Vite WebUI 和网关，可作为后续小喵控制台或多通道管理入口参考。
- 通过 `tool_policy` 将 QQ 入口限制为 `low_risk`、`trusted_pending` 或 `trusted_confirmed`。
- 已接入 `markitdown_convert`、`scrapling_get` 低风险工具，以及 Computer Use/Twitter/Minecraft 显式启用的 MCP 安全配置档。
- `markitdown_convert` 可读取 Agent 工作区和项目根 `workspace/` 内文件，用于 QQ 文档上传后的 Markdown 转换。

关键目录：

```text
xiaomiaoAgent/
├── nanobot/agent/loop.py       # Agent turn 协调
├── nanobot/agent/runner.py     # LLM + tool 调用循环
├── nanobot/agent/tools/        # 工具系统
│   ├── markitdown_tool.py      # Agent 工作区 / 项目工作区文件转 Markdown 低风险工具
│   ├── scrapling_tool.py       # 公网网页主内容抽取低风险工具
│   ├── xiaomiao_stage.py       # 舞台动作工具
│   └── xiaomiaobot_services.py # xiaomiaobot 服务状态/动作适配
├── nanobot/channels/           # 多平台通道
├── nanobot/providers/          # LLM 提供方抽象
├── nanobot/session/            # 会话管理
├── nanobot/agent/memory.py     # 记忆管理
├── nanobot/api/server.py       # API / 网关
└── webui/                      # React/Vite WebUI
```

### 5.1 与现有系统的融合边界

`xiaomiaoAgent` 当前通过 HTTP API 接入，不直接由 `xiaomiao` import `AgentLoop`。当前融合边界是：

```text
stage-web / QQ 普通 AI 回复 / 桌面桥接
    ↓
xiaomiao bridge 或 agent_backend
    ↓
xiaomiaoAgent OpenAI 兼容 API
    ↓
统一会话: xiaomiao-unified
    ↓
Agent 回复

xiaomiaoAgent WebUI
    ↓ 网关 WebSocket :8765
chat_id=xiaomiao-unified
    ↓
会话 API:xiaomiao-unified
    ↓
镜像到 xiaomiao 桥接事件
```

`xiaomiao` 继续负责 QQ Bot 的稳定运行、命令分支、权限网关和确认码。`xiaomiaoAgent` 负责普通自然语言 Agent 回复、工具、记忆和统一会话。长期再评估是否把 QQ 原生接入迁移到 `nanobot/channels/qq.py` 或统一 MessageBus。

### 5.2 推荐融合优先级

1. 已完成：`stage-web` 文本/语音入口通过 `xiaomiao` bridge 接入 xiaomiaoAgent。
2. 已完成：QQ 群/私聊普通 AI 回复通过 `agent_backend.py` 接入 xiaomiaoAgent。
3. 已完成：默认统一会话为 `xiaomiao-unified`。
4. 已完成：QQ Agent 工具权限、确认码、中文记忆命令、桥接工具事件。
5. 已完成：`markitdown_convert`、`scrapling_get` 第一批低风险工具。
6. 已完成：Computer Use、Twitter、Minecraft MCP 安全配置档，默认关闭，启用后按风险策略暴露。
7. 已完成第一步：stage-pocket 只读同步桥接事件。
8. 待推进：把图片理解和更多多模态能力迁移到 xiaomiaoAgent tools。
9. 待评估：是否启用 xiaomiaoAgent 原生 QQ/channel，并与现有 `xiaomiao` 命令系统合并。

## 6. 运行链路

### 6.1 QQ 消息进入机器人

`xiaomiao/config.json` 中的 `Connection` 配置指向本机 NapCat：

```json
{
  "mode": "FWS",
  "host": "127.0.0.1",
  "port": 5004,
  "listener_host": "127.0.0.1",
  "listener_port": 5003
}
```

群消息进入后的主流程：

1. 读取用户消息文本。
2. 获取用户昵称。
3. 选择用户对应人设。
4. 判断是否为命令、快捷命令或 `@机器人` 消息。
5. 若是 Agent 工具型请求，计算风险等级和用户权限。
6. 高风险请求首次生成 `确认执行 <code>`；确认通过后才发送 `trusted_confirmed`。
7. 若是中文记忆命令，转发到 `/status`、`/dream`、`/dream-log`、`/dream-restore`、`/new`、`/stop`。
8. 若消息包含 QQ 文件段或群文件上传，先经 `qq_workspace.py` 校验扩展名、大小和 URL，再保存到 `workspace/downloads/qq/`。
9. 根据命令分支执行具体能力。
10. 如果是普通 AI 对话，调用 `generate_agent_reply()` 转发到 xiaomiaoAgent API。
11. 将回复发送回 QQ。
12. 调用 `publish_desktop_state()` 或桥接事件存储同步到 Web/桌面/移动端。

### 6.2 模型调用

模型/Agent 调用分为三个封装：

- `agent_backend.py`：当前普通 AI 回复主路径，调用 xiaomiaoAgent OpenAI 兼容 API。
- `GoogleAI.py`：OpenAI SDK 兼容封装，支持自定义 `base_url`。
- `SearchOnline.py`：备用 OpenAI 风格对话封装。

`agent_backend.py` 默认请求 `http://127.0.0.1:8900/v1/chat/completions`，并传入 `session_id = "xiaomiao-unified"`。QQ 请求还会附带 `channel`、`chat_id`、`user_id`、`tool_policy`、`confirmation_id`。`GoogleAI.Context` 和 `SearchOnline(...)` 仍保留，用于图片、搜索或未迁移分支。

QQ 侧工具策略：

```text
普通用户
    ↓
tool_policy=low_risk
    ↓
只读文件 / 搜索 / Web / 状态 / markitdown_convert / scrapling_get

白名单用户高风险请求
    ↓
confirmation_requested: 确认执行 <code>
    ↓
用户确认
    ↓
tool_policy=trusted_confirmed + confirmation_id
    ↓
exec / 写文件 / 高风险 MCP / 外部服务写操作
```

`tool_policy` 只由后端权限网关生成，用户文本伪造无效；`ToolRegistry.prepare_call()` 在工具执行前仍会做最后拦截。

### 6.3 QQ 文档资源链路

QQ 文档转换链路已经接入群文件上传事件和普通 file 消息段：

```text
QQ 群文件上传 / file 消息段
    ↓
qq_workspace.py 校验文件名、扩展名、大小和下载 URL
    ↓
workspace/downloads/qq/<channel>/<chat>/<date>/
    ↓
Agent 请求文本追加 workspace_path 和不可信数据提示
    ↓
markitdown_convert(path=workspace_path)
    ↓
Markdown 摘要返回 QQ，并同步桥接事件
```

支持的第一批格式包括 `.txt`、`.md`、`.pdf`、`.docx`、`.xlsx`、`.pptx`、`.xls`、`.csv`、`.json`、`.xml`、`.html`、`.htm`、`.epub`、`.rtf`。普通 file 消息段会阻断 localhost/private/link-local 下载地址；群上传通知通过 OneBot `get_group_file_url` 获取的临时地址允许本机/private URL，因为 NapCat 可能返回本地下载地址。`markitdown_convert` 仍只读取 Agent 工作区和项目根 `workspace/`，拒绝 URL、`file:`、`data:` 和其它本机路径。

### 6.4 stage-web 输入进入 Agent

`stage-web` 的三个入口都会调用 `requestXiaomiaoBridgeReply()`：

```text
apps/stage-web/src/pages/index.vue                    # 页面级录音转文字
packages/stage-layouts/src/components/Widgets/ChatArea.vue
packages/stage-layouts/src/components/Layouts/MobileInteractiveArea.vue
```

请求链路：

```text
stage-web 聊天文本
    ↓ POST http://127.0.0.1:5519/v1/chat/completions
desktop_bridge.py
    ↓ reply_callback -> generate_desktop_reply()
agent_backend.py
    ↓ POST http://127.0.0.1:8900/v1/chat/completions
xiaomiaoAgent
    ↓
stage-web 当前聊天会话追加 user/assistant
```

桥接不可用、HTTP 非 2xx 或空回复时，stage-web 会把 user/error 消息写入聊天历史，不静默回退到 xiaomiaobot 提供方。

## 7. 桌面桥接协议

`xiaomiao/desktop_bridge.py` 默认监听：

```text
http://127.0.0.1:5519
```

提供核心接口：

```text
GET  /v1/models
GET  /v1/xiaomiao/status
GET  /v1/xiaomiao/config
GET  /v1/xiaomiao/state?user_id=<qq>
GET  /v1/xiaomiao/events?after=<id>&user_id=<qq>
POST /v1/xiaomiao/config
POST /v1/chat/completions
```

接口作用：

- `/v1/models`：返回当前桥接模型名称。
- `/v1/xiaomiao/status`：返回桥接服务运行状态、模型名称和默认用户 ID。
- `/v1/xiaomiao/config`：读取或更新主目录 `config.json` 的 `nanobot.providers.custom` 配置；GET 不返回明文 API Key。
- `/v1/xiaomiao/state`：返回某个用户最近一次机器人回复。
- `/v1/xiaomiao/events`：返回桥接记录的 chat/tool/confirmation/memory/stage 事件，供 Web/桌面/移动端同步。
- `/v1/chat/completions`：OpenAI 兼容聊天接口，让 xiaomiaobot 可主动向小喵发送文本并获得回复。
- `POST /v1/xiaomiao/events`：允许 xiaomiaoAgent WebUI 镜像 user/assistant 事件，不触发模型回复。

状态保存方式：

```text
LATEST_STATE_BY_USER[user_id] = 最近一条 assistant 普通回复
BridgeEventStore = chat/tool/confirmation/memory/stage 事件流
```

`/v1/xiaomiao/state` 会过滤工具、确认、记忆和舞台事件，避免桌面字幕或 TTS 被工具事件污染。

当前 `POST /v1/chat/completions` 会调用启动时注入的 `reply_callback`。在 `main.py` 中该 callback 是 `generate_desktop_reply()`，最终进入 `generate_agent_reply()` 和 xiaomiaoAgent API。

xiaomiaobot 侧的小喵桥接模块：

- `packages/stage-layouts/src/xiaomiao-bridge.ts`：stage-web 桥接客户端。
- `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.ts`：读取 `/v1/xiaomiao/state`。
- `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-chat.ts`：把桥接回复写入聊天历史。
- `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.ts`：把桥接回复分发到字幕、聊天历史、语音和口型同步。
- `apps/stage-pocket/src/modules/xiaomiao-bridge-events.ts`：移动端只读同步桥接事件。

`stage-tamagotchi` 主舞台挂载后会初始化聊天同步、确保桥接语音提供方可用，并轮询小喵桥接状态和事件。`stage-pocket` 挂载后启动只读桥接事件轮询，卸载时停止。

## 8. Vtuber 表现链路

桥接回复进入 xiaomiaobot 后，会被同步到三个表现面：

```text
桥接回复
    ├── postCaption() → 字幕窗口显示
    ├── appendBridgeAssistantReply() → 聊天历史追加 assistant 消息
    └── characterStore.emitTextOutput()
            ↓
        Stage.vue speechPipeline
            ↓
        TTS 生成音频
            ↓
        AudioContext 播放
            ↓
        Live2D LipSync 驱动嘴型
```

`Stage.vue` 是 Vtuber 表现核心：

- `speechPipeline` 负责文本到语音。
- `playbackManager` 负责音频播放队列。
- `setupLipSync()` 初始化口型同步。
- `mouthOpenSize` 传入 `Live2DScene` 驱动嘴部开合。

当前代码已经处理桥接语音绕过普通聊天 orchestrator 的问题，在音频播放边界统一初始化 analyser 和 lip sync，避免“有声音但嘴不动”。

舞台动作事件已覆盖：

- `say`
- `tts`
- `subtitle`
- `emotion`
- `background`
- `model`
- `status`

未知舞台动作、缺失 payload、目标模型/背景不存在时会显式写入失败事件，不静默假成功。stage-pocket 当前只展示事件，不执行舞台动作。

## 9. 配置与端口

统一模型配置文件：

```text
F:\xiaomiaoVirtual\config.json
```

关键配置：

- `nanobot.provider`：当前统一使用 `custom`。
- `nanobot.model`：最终生效并返回给调用方的模型名。
- `nanobot.providers.custom.apiKey`：第三方 OpenAI 兼容中转站密钥。
- `nanobot.providers.custom.baseUrl`：第三方中转站 `/v1` 地址。
- `nanobot_agent.enabled`：是否启用统一 xiaomiaoAgent 后端。
- `nanobot_agent.base_url`：默认 `http://127.0.0.1:8900/v1/chat/completions`。
- `nanobot_agent.model`：可选请求模型；默认留空，由 `nanobot.model` 决定。
- `nanobot_agent.session_id`：默认 `xiaomiao-unified`。
- `nanobot_agent.timeout_seconds`：默认 `30`。

`xiaomiao/config.json` 仍用于 QQ Bot 本地运行配置：

- `Connection.host` / `Connection.port`：NapCat OneBot 地址。
- `Others.bot_name`：机器人中文名。
- `Others.ROOT_User`：超级用户。
- `Others.agent_tool_allowlist`：可触发 Agent 高风险工具确认的独立白名单。
- `Others.personas`：人设提示词。

默认端口：

```text
5004  NapCat OneBot WebSocket
5003  Hyper 监听端口
5519  xiaomiao 桥接服务
8765  xiaomiaoAgent 网关
8900  xiaomiaoAgent OpenAI 兼容 API
5174  xiaomiaoAgent WebUI
5175  xiaomiaobot stage-web
6099  NapCat WebUI，可选
3000  NapCat HTTP API，可选
```

xiaomiaobot 常用脚本：

```text
cd F:\xiaomiaoVirtual\xiaomiaobot\apps\stage-web
pnpm exec vite --host 127.0.0.1 --port 5175

cd F:\xiaomiaoVirtual\xiaomiaobot
pnpm dev:tamagotchi   # Electron 桌面版
pnpm dev:docs         # 文档站
pnpm build:tamagotchi # 构建桌面版
pnpm typecheck        # 类型检查
pnpm lint             # 代码规范检查
```

xiaomiaoAgent 常用命令：

```text
python -m xiaomiao_agent serve --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
python -m xiaomiao_agent gateway --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
cd F:\xiaomiaoVirtual\xiaomiaoAgent\webui
npm run dev -- --host 127.0.0.1 --port 5174
```

旧 `nanobot` 命令入口仍保留兼容；新文档和用户提示统一使用 `xiaomiao`。

根目录 `start-all.cmd` 是当前推荐启动入口。它按 `5004 → 8900 → 8765 → 5519 → 5175 → 5174` 串行启动，并对 API、网关、桥接服务、WebUI 做健康检查；前一步未就绪时停止，不打开后续终端。QQ 协议端可复用已登录的现有 NapCat/QQ 进程；其他服务遇到已占用端口会显示 PID 并停止，不再把端口监听误判为可用服务；`--check` 只检查当前状态，不启动窗口。脚本会设置 `NO_PROXY=127.0.0.1,localhost,::1`，避免本机代理影响 QQ OneBot 直连。

## 10. 工程风险

### 10.1 明文密钥

主目录 `config.json` 当前承担统一模型配置，属于本机私有配置；仓库只保留 `config.example.json`。真实 API Key 不应写入可提交源码文件。

### 10.2 文件与运行态污染

项目根 `workspace/` 只提交目录骨架，QQ 下载文件、Agent 工具产物和临时文件不进入仓库。`xiaomiaoAgent/.nanobot/`、`xiaomiao/runtime/bridge_events.jsonl`、`xiaomiaobot/.cache/`、`xiaomiaobot/services/satori-bot/data/db.json` 和 `.understand-anything/` 都属于本机运行态或缓存，已由 `.gitignore` 排除。详细规则见 `docs/file-workspace-hygiene.md`。

### 10.3 主程序职责过重

`xiaomiao/main.py` 同时负责事件监听、命令解析、权限判断、模型调用、图片处理、桥接发布和系统命令。后续建议拆为 `commands/`、`services/llm.py`、`services/bridge.py`、`services/roles.py`、`services/images.py` 和 `permissions.py`。

### 10.4 桥接配置硬编码

xiaomiaobot 中桥接地址和绑定用户仍是原型硬编码：`http://127.0.0.1:5519` 和 `BOUND_XIAOMIAO_USER_ID`。这会限制多用户、多账号、多机器人实例场景。

### 10.5 桥接协议缺少鉴权

桥接服务默认只监听 `127.0.0.1`，风险较低，但本机任意进程仍可访问。如果后续开放到局域网或跨设备，应增加 token、签名或一次性配对机制。

### 10.6 系统命令能力风险

`runcommand` 类能力天然高危。当前新增的 Agent 工具确认链路与旧 `runcommand` 分离：Agent 本机命令需白名单用户触发确认码，确认通过才进入 `trusted_confirmed`。旧 `runcommand` 后续仍建议改为白名单命令或移除远程系统命令执行能力。

### 10.7 Agent 工具权限风险

`xiaomiaoAgent` 提供文件系统、Shell、Web、MCP、Cron、Subagent 等工具能力。当前已经用 `tool_policy`、QQ 白名单、确认码和 `ToolRegistry.prepare_call()` 分层拦截。Computer Use、Twitter、Minecraft MCP 安全配置档默认关闭，启用后只注册显式 `enabled_tools`；HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension 仍按待产品化能力处理。

### 10.8 双 Agent 状态分裂

当前普通 AI 回复已默认使用 `xiaomiao-unified` 会话，降低 Web、QQ、桌面端上下文分裂风险。后续如果启用多用户会话映射或 xiaomiaoAgent 原生 QQ/channel，需要重新定义用户映射和事件 ID，避免同一用户跨入口状态漂移。

## 11. 测试现状

当前最小验证矩阵：

```text
python -m pytest --basetemp .pytest-tmp-xiaomiao-verify test\xiaomiao
uv run --extra dev pytest --basetemp ..\.pytest-tmp-agent-verify tests\test_openai_api.py tests\tools\test_tool_registry.py tests\tools\test_tool_loader.py tests\tools\test_computer_use_mcp_profile.py tests\tools\test_markitdown_tool.py tests\tools\test_scrapling_tool.py tests\tools\test_xiaomiao_stage_tool.py tests\tools\test_xiaomiaobot_services_tool.py
pnpm exec vitest run apps/stage-pocket/src/modules/xiaomiao-bridge-events.test.ts packages/stage-ui/src/xiaomiao-bridge-events.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.test.ts
cmd /c call start-all.cmd --check
```

最近一次完整验证结果：

```text
test/xiaomiao: 77 passed
xiaomiaoAgent selected tests: 95 passed
xiaomiaobot bridge Vitest: 4 files / 32 tests passed
start-all.cmd --check: passed
```

覆盖范围包括：

- QQ 权限、确认码、错用户/错群/过期确认拒绝。
- `tool_policy` 不能被用户文本伪造。
- `ToolRegistry` 对低风险和高风险工具二次拦截。
- MarkItDown/Scrapling 低风险工具边界。
- Computer Use/Twitter/Minecraft MCP 安全配置档过滤。
- 桥接状态过滤和桥接事件展示。
- stage-tamagotchi 舞台动作消费。
- stage-pocket 只读桥接事件同步。

## 12. 演进路线

1. 配置安全：移除源码中的真实 API Key，补充 `.env.example` 或本机配置模板。
2. 桥接配置：把桥接端口、绑定用户、模型名称变成可配置项。
3. 桥接协议：增加消息 ID、健康检查、用户绑定握手和最小鉴权机制。
4. Python 拆分：从 `main.py` 中继续拆出命令、权限、模型、桥接、图片和角色服务。
5. 桥接绑定：为 stage-web/stage-tamagotchi/stage-pocket 增加用户绑定握手、动态桥接 URL 和最小鉴权。
6. Vtuber 增强：支持 QQ 用户到桌面会话映射，并根据回复情绪驱动 Live2D 表情。
7. xiaomiaoAgent 状态观测：在小喵控制台展示 `serve :8900`、WebUI/网关、会话和工具状态。
8. xiaomiaoAgent 能力深化：逐步把图片理解、Web 搜索、Cron 和更多工具迁移到 xiaomiaoAgent。
9. 待产品化服务：HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension。
10. 记忆体系评估：明确 xiaomiaoAgent 文件记忆与 xiaomiaobot `memory-pgvector` 的权威来源和同步方向。
11. 渐进迁移：在现有 QQ Bot 可运行的前提下，评估是否启用 xiaomiaoAgent 原生 QQ/channel。

## 13. 当前结论

项目已经完成 `stage-web`、桌面桥接、QQ 普通 AI 回复到 `xiaomiaoAgent` 的统一接入，并补齐了 QQ Agent 工具权限/确认码、中文记忆命令、低风险 MarkItDown/Scrapling 工具、Computer Use/Twitter/Minecraft MCP 安全配置档、舞台动作闭环和 stage-pocket 第一批只读桥接事件同步。当前剩余重点是桥接绑定、待产品化服务、记忆体系合并评估，以及继续拆分 Python Bot 单体边界。
