# QQ 直连 xiaomiaoAgent / xiaomiaobot 能力计划书

## 摘要

目标是让 QQ 机器人通过自然语言或明确命令调用 xiaomiaoAgent 的记忆、工具、本机指令，以及 xiaomiaobot 的舞台、服务和插件能力。

现状：

- `xiaomiaoAgent` 已有记忆层：短期会话、`memory/history.jsonl`、`SOUL.md`、`USER.md`、`memory/MEMORY.md`、Dream 和记忆版本记录。
- `xiaomiaoAgent` 已有工具层：文件读写、搜索、Web、Shell `exec`、MCP、Cron、Notebook、Subagent、图像生成等。
- `tool/markitdown` 与 `tool/Scrapling` 的第一批低风险能力已接入 xiaomiaoAgent：`markitdown_convert`、`scrapling_get`。
- Computer Use、Twitter、Minecraft 已有 xiaomiaoAgent MCP 安全配置档：默认关闭，启用后只注册显式 `enabled_tools`，低风险/高风险仍由 `ToolRegistry` 和 QQ 确认层二次控制。
- QQ 普通对话已接入 `xiaomiaoAgent API :8900`，但 `qq-group` 当前默认是 `low_risk`，只能用读文件、搜索和 Web 抓取等低风险能力。
- `xiaomiaobot` 还有部分能力尚未从 QQ 侧产品化接入：HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension、stage-pocket 动作化与动态绑定、`memory-pgvector` 合并等。stage-pocket 已完成第一批只读桥接事件同步。

目标效果：

- QQ 普通用户只能调用低风险工具。
- ROOT/Super/显式白名单用户可以触发本机指令和高风险工具。
- 高风险动作必须先生成确认码，用户二次确认后才执行。
- 工具调用、确认请求、记忆更新和舞台动作都写入统一桥接事件，让网页端和桌面端能看到 QQ 触发的动作结果。

## 关键改动

### 1. QQ 工具权限与确认层

在 `xiaomiao` 增加 QQ Agent 工具权限网关：

- 新增 QQ 工具白名单配置，复用 `ROOT_User`、`Super_User`，并支持独立 `agent_tool_allowlist`。
- `qq-group` 默认保持 `low_risk`。
- 白名单用户触发工具型请求时传入 `tool_policy: "trusted_confirmed"` 或 `tool_policy: "trusted_pending"`。
- 高风险动作先返回确认码，例如：`确认执行 ABC123`。
- 确认码携带过期时间、用户 ID、群 ID、命令摘要和风险等级。
- 确认通过后才允许 `exec`、写文件、MCP stdio、插件动作或外部服务写操作。

风险分级：

- `low`：读文件、列目录、grep/glob、web_search、web_fetch、状态查询。
- `low` 补充：`markitdown_convert` Agent 工作区 / 项目根 `workspace/` 文件转 Markdown、`scrapling_get` 公网网页主内容抽取。
- `low` MCP 补充：Computer Use 只读桌面/浏览器/终端状态，Twitter `search/refresh-timeline/get-my-profile`，Minecraft `get_state/get_logs/get_last_prompt/get_llm_trace`。
- `medium`：写工作区文件、调用插件只读以外动作、启动受控 MCP。
- `high`：`exec`、系统进程、外部账号发帖/点赞、HomeAssistant 控制、Minecraft 执行动作、Claude Code hook 注入。

### 2. xiaomiaoAgent API 扩展

扩展 OpenAI 兼容 API 请求体：

```json
{
  "channel": "qq-group",
  "chat_id": "10001",
  "user_id": "3554978979",
  "session_id": "xiaomiao-unified",
  "tool_policy": "low_risk|trusted_pending|trusted_confirmed",
  "confirmation_id": "ABC123"
}
```

实现规则：

- `server.py` 不再只按 `channel == qq-group` 判断工具策略。
- `low_risk` 和 `trusted_pending` 只暴露低风险工具。
- `trusted_confirmed` 才暴露高风险工具。
- 即使模型从历史上下文伪造高风险工具调用，`ToolRegistry.prepare_call()` 仍必须二次拦截。
- API 响应中返回工具事件摘要，供 QQ 和桥接事件展示。

### 3. QQ 记忆命令

为 QQ 增加中文命令别名，并转发到 xiaomiaoAgent 内置命令：

- `记忆状态` -> `/status`
- `整理记忆` -> `/dream`
- `记忆日志` -> `/dream-log`
- `恢复记忆` -> `/dream-restore`
- `新会话` -> `/new`
- `停止任务` -> `/stop`

要求：

- 记忆整理、日志查看允许白名单用户使用。
- 记忆恢复属于高风险动作，需要确认。
- 所有记忆命令结果同步到桥接事件。

### 4. xiaomiaobot 能力适配为 Agent 工具

优先把 xiaomiaobot 能力收敛为 Agent 可调用工具/MCP，而不是让 QQ 直接操作前端内部状态。

第一批接入：

- 舞台控制：字幕、表情、背景、Live2D/VRM 模型切换、TTS 播报。
- 桌面状态：读取 stage-web/stage-tamagotchi 当前在线状态、最近消息、当前角色配置。
- Computer Use MCP：已完成显式启用安全配置档，本机窗口/终端/浏览器动作默认仅白名单 + 确认。
- Minecraft 服务：已完成显式启用安全配置档，查询状态/日志低风险开放，注入聊天/事件/REPL 高风险确认。
- Twitter 服务：已完成显式启用安全配置档，搜索/读取低风险开放，发帖/点赞/转发/登录/保存会话高风险确认。
- HomeAssistant 插件：读取状态低风险；控制设备高风险确认。

第二批接入：

- Bilibili 直播聊天插件。
- Chess 小游戏。
- Claude Code plugin hook。
- Browser Extension 页面上下文。
- stage-pocket 移动端桥接事件同步第一步已完成；后续补桥接绑定握手、动态地址配置和专门事件 UI。
- `memory-pgvector` 与 xiaomiaoAgent 记忆层是否合并评估。

### 5. 统一事件与可观测性

扩展桥接事件：

- 增加 `event_type`: `chat|tool_start|tool_finish|tool_error|confirmation_requested|memory_update|stage_action`
- 增加 `tool_name`、`risk_level`、`confirmation_id`、`result_summary`
- 保留现有 `client_message_id`、`schema_version`、`conversation_id`、`message_id`

展示要求：

- QQ 里返回简短结果。
- stage-web/stage-tamagotchi 里能看到完整工具事件。
- 高风险动作失败必须显式暴露，不能静默回退。

## 测试计划

Python 单测：

- QQ 白名单用户可请求高风险工具，但首次只生成确认码。
- 非白名单 QQ 用户调用 `exec` 被拒绝。
- 过期确认码、错用户确认、错群确认都失败。
- `tool_policy` 不能被用户文本伪造。
- `/dream`、`/dream-log`、`/dream-restore` 中文别名映射正确。
- 桥接事件写入工具事件和确认事件。

xiaomiaoAgent 单测：

- `trusted_confirmed` 暴露 `exec`，`low_risk` 不暴露。
- `trusted_pending` 不暴露高风险工具。
- 隐藏工具被模型直接调用时仍被 `ToolRegistry` 阻断。
- API 请求元数据正确传入 `AgentLoop.process_direct()`。
- MCP 工具按风险等级过滤，包含 Computer Use、Twitter、Minecraft 安全配置档。

前端/Vitest：

- stage 桥接事件能渲染工具开始、完成和失败。
- 确认事件不重复追加聊天消息。
- 舞台动作事件不破坏现有聊天同步。
- stage-pocket 能同步聊天、工具、确认、记忆和舞台桥接事件到移动端聊天历史。

联调验收：

- QQ 发送“整理记忆”，触发 Dream 并返回结果。
- QQ 白名单发送“帮我在本机执行 dir”，先收到确认码，确认后执行。
- QQ 普通用户请求本机执行命令，被明确拒绝。
- QQ 请求“让桌面小喵说一句话”，stage-tamagotchi 播放 TTS/字幕。
- QQ 请求 Minecraft 查询/动作，服务可用时返回结果，不可用时显式失败。
- `start-all.cmd --check` 通过。
- 现有最小矩阵继续通过：`test/xiaomiao`、`xiaomiaoAgent tests/test_openai_api.py tests/tools/test_tool_registry.py`、`xiaomiao-bridge-events.test.ts`。

## 实施批次

### 批次 1：API 与工具策略基础

- 在 xiaomiaoAgent API 支持 `tool_policy` 和 `confirmation_id`。
- 在 `ToolRegistry` 中把 `low_risk` / `trusted_pending` / `trusted_confirmed` 转为实际工具可见性。
- 增加 API 和 Registry 单测。

### 批次 2：QQ 权限网关

- 在 `xiaomiao` 增加 agent tool 白名单读取。
- 为高风险请求生成确认码。
- 确认码通过后向 xiaomiaoAgent API 发送 `trusted_confirmed`。

### 批次 3：QQ 记忆命令

- 增加中文命令别名。
- 记忆恢复走高风险确认。
- 结果写入桥接事件。

### 批次 4：xiaomiaobot 第一批能力工具化

- 先做 stage 状态和 TTS/字幕/表情控制。
- 已完成 Computer Use MCP、Minecraft、Twitter 的 Agent MCP 安全配置档。
- HomeAssistant 仍保留为 WIP，不通过 `xiaomiaobot_action` 伪执行。

### 批次 4A：tool 目录低风险工具化

- 已接入 `markitdown_convert`：Agent 工作区和项目根 `workspace/` 内本地文件转 Markdown，拒绝 URI 和其它本机路径。
- 已接入 QQ 文档资源链路：群文件上传和普通 file 消息段保存到 `workspace/downloads/qq/`，随后由 Agent 调用 `markitdown_convert` 转 Markdown 和总结。
- 已接入 `scrapling_get`：公网 `http/https` GET 主内容抽取，阻断内网、private、link-local、metadata，拒绝浏览器、会话和凭据类能力。
- 已把两个工具加入 `low_risk` 可见白名单。
- 后续高风险扩展包括 MarkItDown OCR/云服务、Scrapling 浏览器抓取、隐身抓取、会话和 Spider。

### 批次 4B：xiaomiaobot MCP 安全配置档

- 已新增 `tools.computer_use_mcp`：默认关闭，启用后只注册显式工具列表；`low_risk` 模式只开放观察/读取状态，`trusted_confirmed` 才开放终端、桌面点击、键盘、PTY、工作流等动作。
- 已新增 `tools.twitter_mcp`：默认连接本机 `http://127.0.0.1:8080/sse`，只读工具低风险可见，账号写操作需要确认。
- 已新增 `tools.minecraft_mcp`：默认连接本机 `http://127.0.0.1:3001/sse`，状态/日志读取低风险可见，注入和 REPL 需要确认。
- 已让 `xiaomiaobot_status` 披露 stage、Computer Use、Twitter、Minecraft、HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension 的真实 `capability_status`。
- `xiaomiaobot_action` 仍只执行 stage；MCP 安全配置档服务会提示使用对应 MCP 工具，避免假成功。

### 批次 4C：stage-pocket 只读桥接事件同步

- 已新增 stage-pocket 桥接事件同步模块。
- 已在移动端 `App.vue` 初始化聊天会话后启动 xiaomiao 桥接事件轮询，卸载时停止。
- 已把 `chat/tool_start/tool_finish/tool_error/confirmation_requested/memory_update/stage_action` 映射进移动端聊天历史。
- 已补 stage-pocket Vitest 配置和同步测试。
- 后续仍需桥接绑定握手、动态桥接 URL、owner 绑定和专门事件 UI。

### 批次 5：事件与前端展示

- 扩展桥接事件 schema。
- stage-web/stage-tamagotchi 渲染工具事件和确认事件。
- stage-pocket 同步并展示第一批桥接事件。
- 补 Vitest。

## 深度执行计划

本轮继续执行的深度目标是把第一条 xiaomiaobot 能力链路闭环：QQ/Agent 触发舞台动作后，桌面端不仅能看到事件，还能实际执行字幕和 TTS 播报；同时修正工具事件污染桌面 `/state` 的风险。

### 深度批次 A：舞台动作真实消费

- 为 `stage_action` 定义前端侧最小稳定语义：`say`、`tts`、`subtitle` 触发字幕和语音；其他动作先进入聊天事件流，不静默伪成功。
- 兼容两种事件来源：
  - `xiaomiao_stage`：`result_summary` 是动作名，`content` 是文本。
  - `xiaomiaobot_action`：`content` 是包含 `服务/动作/载荷` 的 JSON。
- 通过事件 ID 做去重，避免轮询重复导致重复播报。
- 保持现有 `/state` 普通聊天轮询逻辑可用。

### 深度批次 B：桥接状态安全过滤

- `/v1/xiaomiao/state` 只反映普通聊天助手回复。
- `confirmation_requested`、`tool_start`、`tool_finish`、`tool_error`、`memory_update`、`stage_action` 不写入最新桌面状态。
- 重新加载持久化事件时同样执行过滤，避免重启后桌面字幕被工具事件污染。

### 深度批次 C：验证矩阵

- Python：新增桥接状态过滤回归测试。
- Vitest：新增 stage action 提取、执行和去重测试。
- 联调检查：
  - `python -m pytest test/xiaomiao`
  - `python -m pytest xiaomiaoAgent/tests/test_openai_api.py xiaomiaoAgent/tests/tools/test_tool_registry.py`
  - `pnpm --filter @proj-airi/stage-ui test -- xiaomiao-bridge-events`
  - `pnpm --filter @proj-airi/stage-tamagotchi test -- xiaomiao-bridge`
  - `cmd /c call start-all.cmd --check`

## 前提假设

- 权限模型采用：主人/白名单可执行本机指令，普通群用户只能低风险工具。
- 高风险动作采用二次确认。
- 不把 xiaomiaobot 前端组件直接暴露给 QQ；统一通过桥接、server-runtime、MCP 或 Agent 工具适配器调用。
- 不删除现有 QQ 本地命令；新增 Agent 工具命令与现有 `runcommand` 分开，避免权限语义混乱。
- 后续实现按小批次推进，每批不修改超过 3 个业务文件。
