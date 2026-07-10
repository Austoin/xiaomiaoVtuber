# xiaomiaoVirtual

`xiaomiaoVirtual` 是一个 QQ 机器人、Vtuber 桌面角色与轻量 Agent 框架逐步融合的项目。

## 🎭 Live2D 角色系统

**当前已整合 9 个 Live2D 角色，支持 Web 界面和 QQ Bot 无缝切换！**

- ✅ **7 个 xiaomiaobot 原生角色**：Haru (春)、Hiyori (日和)、Mao (真绪)、Mark (马克)、Natori (名取)、Rice (米)、Wanko (小狗)
- ✅ **2 个 Artemis 角色**：Natsume (四季夏目) ⭐、ATRI (亚托莉) ⭐

**快速体验**：
```bash
cd xiaomiaobot/apps/stage-tamagotchi
pnpm dev
# 访问 http://localhost:5173
```

详见：[INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md) | [LIVE2D_COMPLETE_GUIDE.md](LIVE2D_COMPLETE_GUIDE.md)

---

## 系统架构

项目由三个主要子系统组成：

1. `xiaomiao`：Python QQ 机器人，基于 NapCat、OneBot 和 Hyper Bot，负责 QQ 消息接入、命令处理、AI 对话、图片能力和群管理。
2. `xiaomiaobot`：`xiaomiaoVirtual` 的 Web/桌面 Vtuber 表现层，基于 Electron、Vue、TypeScript、Live2D、VRM、TTS 和口型同步能力。内部包名仍保留 `@proj-airi/*` 兼容标识。
3. `xiaomiaoAgent`：轻量 Python Agent 框架，内部 Python 包仍是 `nanobot`，提供 Agent Loop、多平台 Channels、工具调用、记忆、会话管理、OpenAI 兼容 API、Gateway 和 WebUI 能力。

当前已打通统一 Agent 链路：`xiaomiaobot stage-web` 的网页输入、`xiaomiao` 桌面桥接、QQ 群/私聊普通 AI 回复和 `xiaomiaoAgent WebUI` 都会进入同一个 `xiaomiaoAgent` 能力层。`xiaomiao` 在本机暴露 OpenAI 兼容桥接，`stage-web` 通过桥接发消息，QQ 自然语言回复也通过同一个 `agent_backend` 调用 `xiaomiaoAgent` API。

QQ 侧已增加 Agent 工具权限网关：普通用户默认 `low_risk`，ROOT/Super/`agent_tool_allowlist` 用户可以触发高风险工具确认，确认后才会以 `trusted_confirmed` 调用 Agent。命令型 QQ 功能仍保留在 `xiaomiao` 中，包括权限管理、生图、撤回、配置类命令和部分搜索分支。`xiaomiaobot` 继续作为网页端、桌面端和移动端表现层，消费统一回复并同步聊天历史、字幕、语音、口型和桥接事件。

## 架构概览

```text
xiaomiaobot stage-web 文本/语音输入
    ↓ HTTP :5519
xiaomiao desktop_bridge.py
    ↓
xiaomiao agent_backend.py
    ↓ HTTP :8900
xiaomiaoAgent OpenAI 兼容 API
    ↓
xiaomiaoAgent 工具 / 记忆 / 会话
    ↓
stage-web 聊天历史 / 错误消息

QQ 用户 / 群消息
    ↓
NapCat OneBot WebSocket :5004
    ↓
xiaomiao/main.py
    ├── 命令型功能：仍由 xiaomiao 本地处理
    └── 普通 AI 回复：agent_backend.py → xiaomiaoAgent API :8900

xiaomiaobot stage-tamagotchi 桌面端
    ↓
读取 xiaomiao 桥接状态 / 本地桥接回复
    ↓
字幕 / 聊天历史 / TTS / Live2D 口型同步

xiaomiaobot stage-pocket 移动端
    ↓
轮询 xiaomiao 桥接事件
    ↓
聊天 / 工具 / 确认 / 记忆 / 舞台事件只读同步
```

## 目录说明

```text
xiaomiaoVirtual/
├── xiaomiao/       # QQ 机器人主体
├── xiaomiaobot/    # xiaomiaoVirtual Web/桌面 Vtuber 表现层
├── xiaomiaoAgent/  # 轻量 Agent 框架、网关、API 与 WebUI
├── docs/           # 项目文档、启动说明和融合计划
├── test/           # 项目统一测试目录
├── .cache/         # 全项目缓存、运行态、下载和中间产物
├── README.md       # 项目入口说明
└── TECHNICAL.md    # 技术分析文档
```

文件和运行态边界见 `docs/CACHE_DIRECTORY.md`：QQ 下载文件、Agent 产物、缓存、会话、桥接事件和本机数据库统一保存在根目录 `.cache/` 下。

## 快速启动

**📖 完整启动指南** → [docs/00-quick-start/run-and-config.md](docs/00-quick-start/run-and-config.md)

### 0. 一键启动

主目录提供统一启动脚本，会打开必要的 PowerShell 独立终端，并按真实健康状态串行启动。QQ/NapCat 登录窗口保持可见，其它服务窗口默认最小化，仍可从任务栏逐个点开查看日志：

```text
QQ 协议端 :5004
  → xiaomiaoAgent API :8900
  → xiaomiao main.py / 桥接 :5519
  → xiaomiaobot stage-web :5175
```

如果前一个服务没有在超时时间内通过健康检查，脚本会停止，后续终端不会打开。QQ 协议端会复用已登录并正在监听 `5004` 的现有 NapCat/QQ 进程；其他服务不再跳过已占用端口，如果端口已被旧进程占用，脚本会显示 PID 并停止，因为无法把旧进程重新挂到新的 PowerShell 终端。脚本会为本地链路设置 `NO_PROXY=127.0.0.1,localhost,::1`，避免 QQ OneBot WebSocket 被本机代理转走。

```powershell
cd F:\xiaomiaoVirtual
start-all.cmd
```

一键启动打开的服务窗口统一使用 PowerShell。QQ/NapCat 窗口保持可见，用于登录和扫码；其它服务窗口默认最小化。

只检查依赖路径、端口占用和 HTTP 健康状态，不启动窗口：

```powershell
start-all.cmd --check
```

### 1. 启动 xiaomiaoAgent API

`stage-web`、桌面 bridge 和 QQ 普通 AI 回复都依赖该 API：

```powershell
cd F:\xiaomiaoVirtual
conda activate xiaomiao
python -m xiaomiao_agent serve --config F:\xiaomiaoVirtual\.cache\agent\nanobot\config.json
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

### 3. 启动 xiaomiaobot Web 或桌面端

进入 `xiaomiaobot`：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot
corepack enable
corepack prepare pnpm@10.33.0 --activate
pnpm install
cd apps\stage-web
pnpm exec vite --host 127.0.0.1 --port 5175
```

或启动 Electron 桌面端：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot
pnpm dev:tamagotchi
```

`stage-web` 会把文本输入和录音转文字结果发送到 `xiaomiao` 桥接服务；桌面端会读取桥接状态，并将机器人回复同步到 Vtuber 表现层。

## 核心能力

- QQ 群聊与私聊消息接入。
- QQ 普通 AI 对话统一进入 xiaomiaoAgent。
- QQ Agent 工具权限网关：普通用户 `low_risk`，白名单高风险动作二次确认。
- QQ 中文记忆命令：`记忆状态`、`整理记忆`、`记忆日志`、`恢复记忆`、`新会话`、`停止任务`。
- QQ 群文件上传和 file 消息段会保存到 `.cache/xiaomiao/qq_workspace/downloads/qq/`，再由 Agent 调用 `markitdown_convert` 转 Markdown 和总结。
- QQ 可通过 Agent 低风险工具抓取公网网页正文：`scrapling_get` 负责结构化抽取，仍阻断内网和本机地址。
- `stage-web` 文本输入和语音转文字入口统一进入 xiaomiao 桥接服务。
- 人设切换：女朋友、姐姐、妈妈、高级程序员。
- 图片理解、图片生成、名言图片生成。
- 群管理和定时消息。
- 本地 OpenAI 兼容桥接接口。
- xiaomiaoAgent OpenAI 兼容 API、统一会话和记忆/工具能力层。
- xiaomiaoAgent 低风险工具：`markitdown_convert`、`scrapling_get`。
- xiaomiaoAgent MCP 安全配置档：Computer Use、Twitter、Minecraft 默认关闭，启用后按低风险/确认策略暴露。
- Electron 桌面 Vtuber 展示。
- Live2D / VRM 模型渲染。
- TTS 语音播报。
- Live2D 口型同步。
- 字幕和聊天历史同步。
- xiaomiaoAgent Loop 与多轮任务执行能力。
- xiaomiaoAgent 工具系统、MCP、Web 搜索、Cron 和记忆系统。
- 网页端、桌面端、移动端桥接事件和 QQ 普通 AI 回复已统一到 xiaomiaoAgent。
- TUI 终端界面，快速命令行交互。

## 关键文件

`xiaomiao`：

- `main.py`：QQ 机器人主入口，包含事件监听、命令解析、AI 回复和桥接启动。
- `desktop_bridge.py`：本地 OpenAI 兼容桥接服务。
- `agent_backend.py`：调用 xiaomiaoAgent OpenAI 兼容 API 的统一 Agent 后端。
- `qq_agent_tools.py`：QQ Agent 工具策略、确认码和中文记忆命令映射。
- `qq_permissions.py`：ROOT/Super/Agent 工具白名单权限判断。
- `qq_workspace.py`：QQ 文件下载、工作区归档、安全校验和文档转 Markdown Agent 提示构造。
- `GoogleAI.py`：OpenAI 兼容模型调用封装。
- `SearchOnline.py`：备用模型调用封装。
- `prerequisites.py`：人设提示词和角色选择。
- `config.json`：QQ Bot、OneBot、人设和本地命令配置；统一模型配置在主目录 `config.json`。

`xiaomiaobot`：

- `apps/stage-tamagotchi`：Electron 桌面端入口。
- `apps/stage-web/src/pages/index.vue`：stage-web 页面级语音转文字入口，发送到 xiaomiao 桥接服务。
- `packages/stage-layouts/src/xiaomiao-bridge.ts`：stage-web 本地桥接客户端。
- `packages/stage-layouts/src/components/Widgets/ChatArea.vue`：桌面布局文本聊天入口，Web 模式发送到桥接服务。
- `packages/stage-layouts/src/components/Layouts/MobileInteractiveArea.vue`：移动布局文本聊天入口，Web 模式发送到桥接服务。
- `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.ts`：读取小喵桥接状态。
- `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.ts`：把桥接回复分发到字幕、聊天历史和语音。
- `apps/stage-pocket/src/modules/xiaomiao-bridge-events.ts`：移动端只读同步 xiaomiao 桥接事件。
- `apps/stage-tamagotchi/src/renderer/stores/chat-sync.ts`：桌面聊天同步和小喵桥接调用。
- `packages/stage-ui/src/components/scenes/Stage.vue`：Vtuber 舞台、TTS 和口型同步。
- `packages/stage-ui-live2d`：Live2D 组件与状态管理。
- `packages/model-driver-lipsync`：口型同步模型驱动。

`xiaomiaoAgent`：

- `xiaomiaoAgent/nanobot/agent/loop.py`：Agent 主循环，负责上下文构建和 turn 协调。
- `xiaomiaoAgent/nanobot/agent/runner.py`：LLM 对话循环、工具调用和流式响应执行器。
- `xiaomiaoAgent/nanobot/channels/`：Telegram、Discord、Slack、Feishu、QQ、WeChat、WebSocket 等通道适配。
- `xiaomiaoAgent/nanobot/agent/tools/`：文件系统、Shell、Web、MCP、Cron、Notebook、Subagent 等工具能力。
- `xiaomiaoAgent/nanobot/agent/tools/markitdown_tool.py`：Agent 工作区和项目 `.cache/xiaomiao/qq_workspace/` 文件转 Markdown 的低风险工具。
- `xiaomiaoAgent/nanobot/agent/tools/scrapling_tool.py`：公网网页主内容抽取的低风险工具。
- `xiaomiaoAgent/nanobot/agent/tools/xiaomiao_stage.py`：舞台动作工具。
- `xiaomiaoAgent/nanobot/agent/tools/xiaomiaobot_services.py`：xiaomiaobot 服务状态/动作适配。
- `xiaomiaoAgent/nanobot/agent/memory.py`：会话记忆和 Dream 两阶段记忆整理。

## xiaomiaoAgent 接入状态

`xiaomiaoAgent` 当前以内部 `nanobot` Python 包运行，通过 OpenAI 兼容 API 接入，不直接由 `xiaomiao` import AgentLoop。模型、提供方和中转站 API 配置统一写在主目录 `config.json` 的 `nanobot` 段：

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
xiaomiaobot stage-web 文本/语音输入
    ↓ HTTP POST http://127.0.0.1:5519/v1/chat/completions
xiaomiao desktop_bridge.py
    ↓
xiaomiao agent_backend.py
    ↓ HTTP POST http://127.0.0.1:8900/v1/chat/completions
xiaomiaoAgent OpenAI 兼容 API
    ↓ 提供方=custom, model=nanobot.model
第三方 OpenAI 兼容中转站
    ↓
xiaomiaoAgent 回复
    ↓
xiaomiao 桥接状态 / stage-web 聊天历史 / 桌面字幕与 TTS

QQ 群/私聊普通 AI 回复
    ↓
NapCat OneBot WebSocket :5004
    ↓
xiaomiao/main.py
    ↓
xiaomiao agent_backend.py
    ↓ HTTP POST http://127.0.0.1:8900/v1/chat/completions
xiaomiaoAgent → 第三方 OpenAI 兼容中转站

TUI 终端界面
    ↓ 直接调用 AgentLoop
xiaomiaoAgent 工具 / 记忆 / 会话
```

配置规则：

1. `nanobot.model` 是最终生效并返回给调用方的模型名。
2. `nanobot.provider` 使用 `custom`，表示任意第三方 OpenAI 兼容中转站。
3. `nanobot.providers.custom.baseUrl` 填中转站 `/v1` 地址，不要填 `/v1/chat/completions`。
4. `nanobot_agent.base_url` 是 `xiaomiao` 访问本机 xiaomiaoAgent API 的地址，必须保持本机 `8900`。
5. `nanobot_agent.model` 保持空值，避免 `xiaomiao` 请求时覆盖 `nanobot.model`。
6. 修改 `config.json` 后需要重启 `xiaomiaoAgent` 和 `xiaomiao`，web、QQ、桌面端才会加载新配置。

当前边界：

1. `stage-web` 必须走 `xiaomiao` bridge；bridge 不可用时在聊天历史写入明确错误。
2. QQ 群/私聊普通 AI 回复走同一个 `agent_backend`。
3. QQ 工具型请求由 `qq_agent_tools.py` 分级：普通用户只能低风险，白名单高风险动作必须先收到 `确认执行 <code>`。
4. 统一会话默认为 `xiaomiao-unified`，避免网页端、QQ、桌面端、TUI 上下文分裂。
5. QQ 本地命令 `帮助`、`关于`、`读图` 使用精确匹配；普通问题里包含这些词时仍作为 AI 请求进入 xiaomiaoAgent。
6. Computer Use、Twitter、Minecraft 通过显式启用的 MCP 安全配置档暴露；HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension 仍按开发中能力处理。
7. TUI 终端界面直接调用 `AgentLoop`，使用 `trusted_confirmed` 策略，拥有完整工具权限。

## 验证矩阵

当前最小回归矩阵：

```powershell
python -m pytest --basetemp .pytest-tmp-xiaomiao-verify test\xiaomiao
cd xiaomiaoAgent
uv run --extra dev pytest --basetemp ..\.pytest-tmp-agent-verify tests\test_openai_api.py tests\tools\test_tool_registry.py tests\tools\test_tool_loader.py tests\tools\test_computer_use_mcp_profile.py tests\tools\test_markitdown_tool.py tests\tools\test_scrapling_tool.py tests\tools\test_xiaomiao_stage_tool.py tests\tools\test_xiaomiaobot_services_tool.py
cd ..\xiaomiaobot
pnpm exec vitest run apps/stage-pocket/src/modules/xiaomiao-bridge-events.test.ts packages/stage-ui/src/xiaomiao-bridge-events.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.test.ts
cd ..
start-all.cmd --check
```

最近验证结果：`test/xiaomiao` 77 passed，`xiaomiaoAgent` 95 passed，前端 Vitest 4 files / 32 tests passed，`start-all.cmd --check` passed。

快速 TUI 测试：

```powershell
start-tui.cmd
```

## 文档

- `TECHNICAL.md`：完整技术结构、运行链路、桥接协议、风险和演进建议。
- `docs/getting-started/README.md`：本地启动步骤、端口、验证和常见问题。
- `docs/04-development/file-workspace-hygiene.md`：文件追踪、工作区、QQ 下载资源、运行态缓存和清理规则。
- `docs/subsystems/xiaomiao/README.md`：QQ 机器人部署和功能说明。
- `docs/subsystems/xiaomiaobot/README.md`：历史命名下的 xiaomiaobot / xiaomiaoVirtual 表现层启动和模块说明。
- `docs/05-tools/tool-directory-analysis.md`：`tool/markitdown` 与 `tool/Scrapling` 精简源码和接入边界。
- `docs/archive/plans/2026-06-06-qq-agent-xiaomiaobot-capability-integration.md`：QQ 直连 Agent/xiaomiaobot 能力计划与执行批次。
- `docs/archive/plans/2026-06-06-project-deep-analysis-and-qq-agent-gap-audit.md`：上一计划完成度审计、剩余缺口和下一阶段路线。

## 安全注意

不要把真实 API Key、机器人账号凭据或生产配置提交到仓库。主目录 `config.json` 是本地私有配置；仓库内只保留 `config.example.json` 作为结构示例。
