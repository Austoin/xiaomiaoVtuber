# 项目深度解析与 QQ Agent 能力缺口审计

## Summary

本文档是在 `2026-06-06-qq-agent-xiaomiaobot-capability-integration.md` 基础上的更新版审计与下一阶段计划。

结论：

- 上一个计划书没有“全面完成”。它的基础设施部分完成度较高，包括 QQ 工具权限、确认码、Agent API `tool_policy`、ToolRegistry 二次拦截、bridge event 元数据、QQ 记忆命令、stage `say/tts/subtitle` 最小闭环。
- 当前增量已经把 Computer Use、Twitter、Minecraft 的 Agent MCP 安全 profile 接入配置层：默认关闭，显式启用后使用精确 `enabled_tools`，QQ `low_risk` 仍由 `ToolRegistry.prepare_call()` 二次拦截，高风险工具需要确认后才可见。
- 上一个计划书的最终目标尚未完全达成。尤其是 xiaomiaobot 生态里的 HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension 等能力，仍处于“已有服务/插件/事件面，但尚未形成 QQ 可直接稳定调用的产品级闭环”。stage-pocket 已完成第一批只读 bridge event 同步，但还缺 bridge binding handshake 和动态连接配置。
- 当前项目已经形成三层系统：`xiaomiao` 负责 QQ 与本地 bridge，`xiaomiaoAgent` 负责 Agent 记忆与工具执行，`xiaomiaobot` 负责舞台、TTS、插件和外部服务生态。

本计划目标：

- 明确上一计划完成度。
- 固化最新项目深度解析。
- 给出下一阶段小批次执行路线，优先把高价值能力逐条闭环，而不是继续泛化扩展。

## Project Architecture

### 1. xiaomiao

定位：QQ 机器人入口、本地 desktop bridge、旧命令系统、Agent 权限网关。

已确认能力：

- QQ 到 Agent 后端请求已存在。
- `agent_tool_allowlist`、ROOT、Super 权限复用已接入。
- 高风险请求可生成确认码。
- `确认执行 ABC123` 可绑定用户、群、过期时间和风险动作。
- Agent 返回的工具事件会写入 bridge events。
- `/v1/xiaomiao/state` 已避免被工具事件和舞台动作污染。

关键文件：

- `xiaomiao/main.py`
- `xiaomiao/agent_backend.py`
- `xiaomiao/qq_agent_tools.py`
- `xiaomiao/qq_agent_bridge.py`
- `xiaomiao/desktop_bridge.py`

主要风险：

- `main.py` 仍然过于单体，旧命令、QQ 消息、权限、Agent 网关混在一起。
- 旧的本地命令体系和新的 Agent 工具体系并存，后续必须继续保持权限语义分离。
- bridge 前端连接仍依赖本机固定地址，用户绑定机制还不够通用。

### 2. xiaomiaoAgent

定位：真正的 Agent 大脑，负责记忆、工具调用、MCP、Shell、OpenAI-compatible API。

已确认能力：

- 记忆层真实存在：
  - session JSONL
  - `memory/history.jsonl`
  - `memory/MEMORY.md`
  - `SOUL.md`
  - `USER.md`
  - Dream consolidation
  - Dream 版本记录与恢复
- 工具层真实存在：
  - 文件读写
  - 搜索与 Web
  - Shell `exec`
  - MCP
  - Cron
  - Notebook
  - Subagent
  - 图像生成
  - xiaomiao stage/service 工具
- `tool_policy` 已进入 API 请求上下文。
- `ToolRegistry.prepare_call()` 已作为最后一道工具权限防线。
- `trusted_confirmed` 才能暴露高风险能力。
- `tool/markitdown` 和 `tool/Scrapling` 的第一批低风险能力已接入 Agent 工具层：
  - `markitdown_convert`：workspace 本地文件转 Markdown。
  - `scrapling_get`：公网网页 GET 主内容抽取。

关键文件：

- `xiaomiaoAgent/nanobot/api/server.py`
- `xiaomiaoAgent/nanobot/agent/loop.py`
- `xiaomiaoAgent/nanobot/agent/runner.py`
- `xiaomiaoAgent/nanobot/agent/tools/registry.py`
- `xiaomiaoAgent/nanobot/agent/memory.py`
- `xiaomiaoAgent/nanobot/command/builtin.py`
- `xiaomiaoAgent/nanobot/agent/tools/xiaomiao_stage.py`
- `xiaomiaoAgent/nanobot/agent/tools/xiaomiaobot_services.py`

主要风险：

- MCP 工具的风险分级需要持续维护，不能只靠工具可见性。
- 模型历史上下文可能伪造工具调用，因此 `prepare_call()` 的硬拦截不能弱化。
- Agent 记忆和 xiaomiaobot `memory-pgvector` 仍是两套体系，后续需要评估是否合并。

### 3. xiaomiaobot

定位：虚拟角色舞台、桌面端、网页端、移动端、插件 SDK、服务生态。

已确认能力：

- `stage-web` 可经本地 bridge 发起聊天。
- `stage-tamagotchi` 可轮询 bridge state 和 bridge events。
- `stage_action` 的 `say/tts/subtitle/emotion/background/model/status` 已能被桌面端消费，触发字幕、TTS、表情指令、背景切换、模型切换和状态回传。
- `Stage.vue` 已把 TTS、播放、唇形同步、字幕 broadcast 放在统一播放链上。
- `server-sdk`、`plugin-protocol`、`server-runtime` 提供统一 WebSocket 事件面。
- `Computer Use MCP` 已非常完整，包含桌面观察、截图、点击、键盘、终端、PTY、浏览器 DOM、工作流和审批队列。
- `Twitter service` 已有 MCP adapter，包含搜索、时间线、发帖、点赞、转发等。
- `Minecraft service` 有 debug MCP 与运行时上下文。
- `Browser Extension` 有页面上下文 bridge。
- `Claude Code plugin` 可把 Claude Code hook 输入转发到 channel server。

关键文件：

- `xiaomiaobot/packages/stage-layouts/src/xiaomiao-bridge.ts`
- `xiaomiaobot/apps/stage-tamagotchi/src/renderer/pages/index.vue`
- `xiaomiaobot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.ts`
- `xiaomiaobot/packages/stage-ui/src/components/scenes/Stage.vue`
- `xiaomiaobot/packages/stage-ui/src/stores/character/index.ts`
- `xiaomiaobot/packages/plugin-protocol/src/types/events.ts`
- `xiaomiaobot/packages/server-sdk/src/client.ts`
- `xiaomiaobot/services/computer-use-mcp/src/server/register-tools.ts`
- `xiaomiaobot/services/twitter-services/src/adapters/mcp-adapter.ts`
- `xiaomiaobot/services/minecraft/src/debug/mcp-repl-server.ts`

主要风险：

- xiaomiaobot 能力很多，但除舞台动作外，真正 QQ 可直接调用的服务闭环还少。
- `stage_action` 已覆盖 `say/tts/subtitle/emotion/background/model/status`，未知动作会显式失败。
- HomeAssistant 和 Bilibili 插件入口仍是 `WIP`。
- Chess 插件主要体现为包和依赖，缺少 Agent/QQ 侧调用面。
- stage-pocket 已接入 xiaomiao bridge events 第一批只读同步，可把 chat/tool/confirmation/memory/stage events 合并进移动端聊天历史。

## Previous Plan Completion Audit

上一计划文件：`docs/plans/2026-06-06-qq-agent-xiaomiaobot-capability-integration.md`

### 完成度总评

整体完成度：部分完成。

完成得较扎实的是“权限、确认、Agent API、工具策略、bridge event、QQ 记忆命令、舞台说话/TTS 最小链路”。未全面完成的是“所有 xiaomiaobot 能力都能被 QQ 机器人自然语言或命令直接调用”。

### 分项审计

| 计划项 | 状态 | 说明 |
| --- | --- | --- |
| QQ 工具白名单配置 | 已完成 | 已支持 ROOT/Super/`agent_tool_allowlist`。 |
| 高风险确认码 | 已完成 | 已有确认码、过期、用户/群绑定和确认命令。 |
| 普通 QQ 默认 low_risk | 已完成 | QQ 未确认时只走低风险工具策略。 |
| `tool_policy` API 扩展 | 已完成 | 请求体支持 `low_risk/trusted_pending/trusted_confirmed`。 |
| `confirmation_id` API 扩展 | 已完成 | confirmed 请求要求 confirmation id。 |
| ToolRegistry 二次拦截 | 已完成 | 隐藏工具被直接调用仍会被 prepare_call 拦截。 |
| 工具事件返回给 QQ/bridge | 已完成 | `xiaomiao_tool_events` 已进入响应和 bridge event。 |
| QQ 中文记忆命令 | 已完成 | `记忆状态/整理记忆/记忆日志/恢复记忆/新会话/停止任务` 已映射。 |
| `/dream-restore` 高风险确认 | 已完成或基本完成 | 恢复类命令进入高风险确认模型，需要继续保持回归测试。 |
| bridge event schema 扩展 | 已完成 | 已支持 tool/memory/stage/confirmation 元数据。 |
| stage-web/stage-tamagotchi 展示工具事件 | 已完成 | 前端可渲染确认、工具开始/完成/失败、舞台动作等事件。 |
| stage `say/tts/subtitle` 真实消费 | 已完成 | 桌面端可播报和显示字幕。 |
| bridge state 安全过滤 | 已完成 | 工具事件不再污染 latest desktop state。 |
| 舞台表情/背景/模型切换 | 已完成 | stage-tamagotchi 已消费 `emotion/background/model/status`，失败会显式回传。 |
| MarkItDown 低风险工具 | 已完成 | `markitdown_convert` 已接入 ToolLoader 和 low_risk 白名单，仅允许 workspace 内文件。 |
| Scrapling 低风险工具 | 已完成 | `scrapling_get` 已接入 ToolLoader 和 low_risk 白名单，仅允许公网 GET，阻断内网目标。 |
| Computer Use MCP QQ 接入 | 已完成安全 profile | 已有 opt-in `tools.computer_use_mcp`，显式 allowlist 区分 low_risk 和 trusted_confirmed；真实服务仍需用户自行启动。 |
| Minecraft QQ 接入 | 已完成安全 profile | 已有 opt-in `tools.minecraft_mcp`，只读状态/日志低风险可见，`execute_repl/inject_*` 需确认。 |
| Twitter QQ 接入 | 已完成安全 profile | 已有 opt-in `tools.twitter_mcp`，`search/refresh-timeline/get-my-profile` 低风险可见，发帖/点赞/转发/登录需确认。 |
| HomeAssistant QQ 接入 | 未完成 | 插件入口仍为 `WIP`。 |
| Bilibili QQ 接入 | 未完成 | 插件入口仍为 `WIP`。 |
| Chess QQ 接入 | 未完成 | 缺稳定运行入口和 Agent 工具适配。 |
| Claude Code hook QQ 接入 | 部分完成 | hook 能进 channel server，但不是受控 QQ 工具。 |
| Browser Extension QQ 接入 | 部分完成 | 有 bridge/上下文，未接入 Agent 统一工具面。 |
| stage-pocket event 同步 | 已完成第一步只读同步 | 移动端已轮询 xiaomiao bridge events，并把 chat/tool/confirmation/memory/stage events 合并进聊天历史；仍缺 bridge binding handshake 与动态地址配置。 |
| `memory-pgvector` 合并评估 | 未完成 | 仍需单独设计。 |

## Current Closed Loops

### QQ 到 Agent 普通对话

链路：

`QQ -> xiaomiao/main.py -> agent_backend.py -> xiaomiaoAgent /v1/chat/completions -> AgentLoop -> bridge events`

状态：可用。

### QQ 到 Agent 高风险工具确认

链路：

`QQ 高风险文本 -> qq_agent_tools 风险识别 -> 确认码 -> 用户确认 -> trusted_confirmed -> ToolRegistry 暴露高风险工具`

状态：可用。

### QQ 到记忆命令

链路：

`中文别名 -> Agent slash command -> Dream/status/log/restore/new/stop -> bridge event`

状态：可用。

### QQ 到舞台 TTS/字幕

链路：

`QQ/Agent -> xiaomiao_stage 或 xiaomiaobot_action -> bridge stage_action -> stage-tamagotchi poll -> applyXiaomiaoStageActionEvents -> stage store/character store -> Stage TTS/lipsync/caption/model/background`

状态：可用，已覆盖 `say/tts/subtitle/emotion/background/model/status`。

### QQ/Agent 到 tool 目录低风险工具

链路：

`QQ low_risk -> xiaomiaoAgent ToolRegistry -> markitdown_convert/scrapling_get -> 显式结果或错误`

状态：可用。

边界：

- `markitdown_convert` 只读 workspace 内本地文件，拒绝 URI 和 workspace 外路径。
- `scrapling_get` 只读公网 URL，阻断 localhost/private/link-local/metadata，暂不开放浏览器、stealth、session、cookies/auth/proxy/CDP。

### xiaomiao bridge events 到 stage-pocket

链路：

`stage-pocket mounted -> startXiaomiaoBridgeEventSync -> /v1/xiaomiao/events poll -> append bridge events to chat session`

状态：已完成第一批只读同步。

边界：

- 只消费并展示事件，不直接执行舞台动作。
- 轮询地址仍使用默认本机 bridge URL，后续需要 bridge binding handshake 和动态配置。

## Major Gaps

### Gap 1：舞台动作闭环已补齐，仍需联调打磨

当前：

- `say/tts/subtitle/emotion/background/model/status` 可执行或查询。
- 未知动作、缺失 payload、目标模型/背景不存在时会显式失败。

目标：

- 在真实 QQ 到桌面链路上继续补充端到端验收。
- 为更多舞台状态字段补充 UI 可视化，而不是只在 bridge event 中返回。

### Gap 2：服务适配器多为“事件排队”，不是“动作执行”

当前：

- `xiaomiaobot_status` 能读 bridge status 并发布工具事件。
- `xiaomiaobot_action` 能写入事件流。
- 但 Computer Use、Minecraft、Twitter、HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension 的真实执行适配器并未统一接上。

目标：

- 每个服务都要有明确 adapter：
  - read-only 查询是否直接执行并返回结果。
  - mutating action 是否需要确认。
  - 执行结果是否写回 `tool_finish/tool_error`。

### Gap 3：MCP 配置和风险分级还需产品化

当前：

- Agent 支持 MCP。
- Computer Use/Twitter/Minecraft 各自已有 MCP 或服务形态。
- 但 QQ 入口未形成“默认安全配置 + 白名单确认 + 可观测结果”的产品级配置。

目标：

- 建立 `qq-agent-mcp-profile`。
- 低风险只读工具默认可见。
- 中高风险工具必须确认。
- MCP stdio 启动和外部服务写操作必须写入 bridge event。

### Gap 4：多端 bridge 同步不完整

当前：

- stage-web 和 stage-tamagotchi 已接 bridge events。
- stage-pocket 已接 xiaomiao bridge event 第一批只读同步。
- 前端仍有 `127.0.0.1:5519` 和固定用户绑定。

目标：

- 建立 bridge binding handshake。
- 移除硬编码 owner QQ。
- stage-pocket 在已同步聊天、工具事件、确认事件、记忆事件和舞台事件基础上，补动态连接、用户绑定和更完整的移动端展示。

### Gap 5：双记忆体系未决

当前：

- xiaomiaoAgent 文件记忆体系已可用。
- xiaomiaobot `memory-pgvector` 仍是独立方向。

目标：

- 明确哪个是权威长期记忆。
- 如果合并，定义同步方向、冲突规则、索引刷新和恢复机制。

## Next Execution Plan

### Batch 1：舞台动作补全

目标：把 stage action 从说话扩展为可控舞台。

范围：

- `say`
- `tts`
- `subtitle`
- `emotion`
- `background`
- `model`
- `status`

交付：

- 已定义 `stage_action` payload schema。
- 已让 `xiaomiao_stage` 按 schema 输出。
- 已让 `stage-tamagotchi` 消费 `emotion/background/model/status`。
- 已对未知 action 显式写失败结果，不假成功。

测试：

- Vitest 已覆盖解析、重复事件和未知 action 显式失败。

### Batch 2：Computer Use MCP 安全接入

目标：QQ 白名单可确认后调用本机窗口/终端/浏览器能力。

当前状态：已完成 Agent 配置层安全 profile。该 profile 默认不启动服务，启用后只注册显式 `enabled_tools`；QQ `low_risk` 和 `trusted_pending` 下仍只暴露只读工具，`terminal_exec`、桌面点击、键盘、PTY、workflow 等动作必须进入 `trusted_confirmed`。

低风险默认开放：

- `desktop_get_capabilities`
- `desktop_observe_windows`
- `desktop_screenshot`
- `terminal_get_state`
- `browser_dom_get_bridge_status`
- `browser_dom_read_page`

高风险确认后开放：

- `terminal_exec`
- `desktop_click`
- `desktop_type_text`
- `desktop_press_keys`
- `clipboard_write_text`
- `pty_create`
- `pty_send_input`
- workflow 类动作

交付：

- 已新增 MCP profile 配置。
- 已新增风险分级 allowlist。
- 已补 ToolRegistry 二次拦截测试。
- 待真实服务联调时继续确认 MCP 执行结果是否完整写入 bridge events。

测试：

- 非白名单请求 `terminal_exec` 被拒绝。
- 白名单首次请求只返回确认码。
- 确认后执行只允许指定 confirmation id 对应的动作。

### Batch 2A：tool 目录第一批低风险接入

目标：把 `tool/markitdown` 和 `tool/Scrapling` 收敛为 QQ 可见的低风险 Agent 工具。

交付：

- 已新增 `markitdown_convert`。
- 已新增 `scrapling_get`。
- 已加入 `LOW_RISK_ALLOWED_TOOLS`。
- 已加入 ToolLoader 和 ToolRegistry 测试。
- 已完成缺依赖显式报错、路径边界、URL SSRF、重定向阻断和截断测试。

后续：

- MarkItDown 上传文件 artifacts 输出。
- Scrapling `bulk_get`、`fetch`、`stealthy_fetch`、Spider 的分级确认接入。
- 工具事件进一步统一写入 bridge events。

### Batch 3：Twitter 只读与写操作分层

目标：QQ 可搜索/读取 Twitter，高风险写操作确认。

当前状态：已完成 Agent 配置层安全 profile。`tools.twitter_mcp.enable=true` 后连接本机 Twitter MCP SSE 服务，默认 `enabled_tools` 使用精确列表，不使用 `*`。

低风险：

- `search`
- `refresh-timeline`
- `get-my-profile`
- tweet/profile resource read

高风险：

- `post-tweet`
- `like-tweet`
- `retweet`
- `save-session`
- `login`

交付：

- 已把 Twitter MCP adapter 接入 Agent MCP profile。
- 已补 `refresh-timeline`、`get-my-profile` 连字符工具名的低风险过滤测试。
- QQ 简短摘要与前端完整事件展示依赖统一 Agent tool events，后续真实服务联调时继续验收。

### Batch 4：Minecraft 状态与注入

目标：先做查询和调试注入，再做真实游戏动作。

当前状态：已完成 Agent 配置层安全 profile。`tools.minecraft_mcp.enable=true` 后连接本机 Minecraft debug MCP，默认使用 streamable HTTP，并通过显式 allowlist 区分状态读取和注入/REPL。

低风险：

- `get_state`
- `get_logs`
- `get_last_prompt`
- `get_llm_trace`

中高风险：

- `inject_chat`
- `inject_event`
- `execute_repl`

交付：

- 已把 Minecraft debug MCP 作为只读/高风险分层工具接入 Agent profile。
- 已补 `get_state/get_logs/get_last_prompt/get_llm_trace` 低风险过滤测试。
- 服务不可用时由 MCP 连接/调用路径显式报错，后续真实服务联调时继续验收 bridge `tool_error` 展示。

### Batch 5：WIP 插件处理

目标：对未完成插件做真实状态归类，避免 UI/文档暗示已完成。

范围：

- HomeAssistant
- Bilibili
- Chess
- Claude Code
- Browser Extension
- stage-pocket

交付：

- 每个插件补 `capability_status`：
  - `not_started`
  - `wip`
  - `read_only_ready`
  - `action_ready`
  - `qq_agent_ready`
- `xiaomiaobot_status` 返回真实状态，不只返回 bridge online。
- 已把 stage 标记为 `qq_agent_ready`。
- 已把 Computer Use、Twitter、Minecraft 标记为 `action_ready` + `qq_agent_ready`，并明确它们通过 Agent MCP profile 执行，不通过 `xiaomiaobot_action` 伪造 bridge action。
- HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension 仍按真实情况标记为 `wip`。
- stage-pocket 已完成第一批只读 bridge event 同步，但暂不把移动端动作入口标记为可执行能力。
- 文档和工具描述避免把 WIP 能力描述成可执行能力。

### Batch 5A：stage-pocket bridge event 只读同步

目标：让移动端能看到 QQ/Agent 触发的聊天、工具、确认、记忆和舞台事件。

交付：

- 已新增 stage-pocket 专用 bridge event 同步模块。
- 已在 `App.vue` 初始化聊天会话后启动轮询，卸载时停止。
- 已将 chat/tool_start/tool_finish/tool_error/confirmation_requested/memory_update/stage_action 合并进移动端聊天历史。
- 已补 stage-pocket Vitest 和 workspace 配置。

后续：

- 建立 bridge binding handshake。
- 移除固定本机地址和固定 owner 绑定。
- 增加移动端对工具事件和确认事件的专门 UI，而不是全部映射为聊天消息。

## Acceptance Criteria

### 基础验收

- `python -m pytest test/xiaomiao` 通过。
- `uv run --extra dev pytest tests/test_openai_api.py tests/tools/test_tool_registry.py` 在 `xiaomiaoAgent` 通过。
- `pnpm exec vitest run packages/stage-ui/src/xiaomiao-bridge-events.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.test.ts` 在 `xiaomiaobot` 通过。
- `cmd /c call start-all.cmd --check` 通过。

### 功能验收

- QQ 普通用户请求本机执行命令，被明确拒绝。
- QQ 白名单用户请求本机命令，首次返回确认码。
- QQ 白名单用户确认后，Agent 才能执行对应高风险工具。
- QQ 发送“整理记忆”，能触发 Dream 并返回结果。
- QQ 发送“让桌面小喵说一句话”，stage-tamagotchi 播放 TTS 和字幕。
- QQ 请求未知舞台动作，不静默成功。
- Computer Use 服务不可用时返回显式失败。
- Twitter 写操作未确认时不执行。
- Minecraft 服务不可用时返回显式失败。

## Recommended Priority

优先级建议：

1. 舞台动作补全。
2. tool/MarkItDown/Scrapling 第一批低风险工具接入。
3. Computer Use MCP 安全接入。
4. Twitter 只读/写操作分层。
5. Minecraft 状态/注入。
6. WIP 插件状态暴露。
7. stage-pocket bridge binding handshake 和移动端事件 UI 深化。
8. 记忆体系合并评估。

原因：

- 舞台动作是用户最直观看到的闭环，风险较低。
- Computer Use 是本地电脑执行能力，价值高但风险最高，必须先做权限和审计。
- Twitter/Minecraft 都已有服务基础，适合做第二批产品化适配。
- HomeAssistant/Bilibili/Chess 当前基础不足，先做状态披露，避免误判。

## Final Answer To Audit Question

上一份计划书的内容没有全面完成。

准确说：

- “QQ 直连 Agent 的权限、确认、记忆命令、事件可观测性、舞台 TTS/字幕/表情/背景/模型闭环、stage-pocket 第一批只读 bridge event 同步，以及 `tool/` 第一批低风险 MarkItDown/Scrapling 工具”已经完成。
- “QQ 机器人可以直接调用 xiaomiaobot 全部服务/插件能力”没有完成。
- “Computer Use、Minecraft、Twitter 已完成安全 profile，但真实外部服务联调仍待按需启用；HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension、stage-pocket 动作化与绑定配置全部产品化接入”没有完成。

因此后续应按本计划继续小批次推进，每批都以真实 QQ 可调用、权限可控、失败可见、事件可观测为完成标准。
