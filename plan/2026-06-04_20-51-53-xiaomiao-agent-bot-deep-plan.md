---
mode: plan
cwd: f:\xiaomiaoVirtual
task: 深度阅读 xiaomiaoAgent 和 xiaomiaobot，梳理未打通、重复、未使用功能并给出完整规划
complexity: complex
created_at: 2026-06-04 20:51:53 +08:00
---

# xiaomiaoAgent 与 xiaomiaobot 深度联通规划

## 0. 实施进度

### 2026-06-04 Target 1：bridge event 支持 client_message_id

状态：已完成。

完成内容：

1. `xiaomiao/desktop_bridge.py` 的 `publish_bridge_event()` 和 `publish_bridge_exchange()` 已支持可选 `client_message_id`。
2. `/v1/chat/completions` 和 `POST /v1/xiaomiao/events` 都可以接收并写入 `client_message_id`。
3. `xiaomiao/bridge_event_store.py` 重载持久化事件时会保留 `client_message_id`。
4. `test/xiaomiao/test_desktop_bridge_persistence.py` 已新增重载后保留 `client_message_id` 的测试。

验证结果：

- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest test/xiaomiao/test_desktop_bridge_persistence.py -q`
- 结果：`3 passed`
- 发现既有问题：`test/xiaomiao/test_desktop_bridge.py` 仍导入旧的 `NanobotAgentConfig` / `reply_with_nanobot_agent` 名称，当前代码已改为 `XiaomiaoAgentConfig` / `reply_with_xiaomiao_agent`，导致该文件收集失败。该问题已在 Target 2 修复。

### 2026-06-04 Target 2：修复 bridge 主测试并补 HTTP client_message_id 验证

状态：已完成。

完成内容：

1. `test/xiaomiao/test_desktop_bridge.py` 已从旧 `NanobotAgent*` 命名更新为当前 `XiaomiaoAgent*` 命名。
2. 同一测试文件中的根配置段从旧 `nanobot` 更新为当前 `xiaomiaoAgent`。
3. 新增 `/v1/chat/completions` 路由级测试，确认请求体携带 `client_message_id` 后，`/v1/xiaomiao/events` 返回的 user/assistant 事件都保留该字段。

验证结果：

- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest test/xiaomiao/test_desktop_bridge.py -q`
- 结果：`13 passed`
- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest test/xiaomiao/test_desktop_bridge_persistence.py -q`
- 结果：`3 passed`

### 2026-06-04 Phase 1：固化现有闭环

状态：已完成。

完成内容：

1. 后端 bridge event 协议支持 `client_message_id`，包括 `/v1/chat/completions`、`POST /v1/xiaomiao/events`、内存事件和持久化重载。
2. stage-web bridge client 支持 `clientMessageId` 参数，请求时转换为后端字段 `client_message_id`。
3. stage-web 常规文本入口、移动端入口、页面级语音转写入口都会生成并传入 `clientMessageId`。
4. 本地乐观消息和 bridge 回放事件统一使用 `clientMessageId + role` 生成 chat item id；同一消息被事件流确认时不会重复追加。
5. bridge event store 遇到坏 JSON 或缺字段行时，会把坏行写入 `bridge_events.invalid.jsonl`，继续加载其他有效事件。
6. `start-all.cmd --check` 的 gateway 检查会在 `api:xiaomiao-unified` session 已存在时验证其 messages API 可读；首次启动尚无该 session 时不误报失败。

修改范围：

- `xiaomiao/desktop_bridge.py`
- `xiaomiao/bridge_event_store.py`
- `scripts/start-all-health.ps1`
- `xiaomiaobot/packages/stage-layouts/src/xiaomiao-bridge.ts`
- `xiaomiaobot/packages/stage-layouts/src/components/Widgets/ChatArea.vue`
- `xiaomiaobot/packages/stage-layouts/src/components/Layouts/MobileInteractiveArea.vue`
- `xiaomiaobot/apps/stage-web/src/pages/index.vue`
- `test/xiaomiao/test_desktop_bridge.py`
- `test/xiaomiao/test_desktop_bridge_persistence.py`
- `xiaomiaobot/packages/stage-ui/src/xiaomiao-bridge-events.test.ts`

验证结果：

- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest test/xiaomiao/test_desktop_bridge.py test/xiaomiao/test_desktop_bridge_persistence.py -q`
- 结果：`17 passed`
- 通过：`pnpm exec vitest run packages/stage-ui/src/xiaomiao-bridge-events.test.ts`
- 结果：`1 passed / 6 passed`
- 通过：PowerShell 解析 `scripts/start-all-health.ps1`
- 结果：`start-all-health.ps1 syntax OK`
- 通过：`start-all.cmd --check`
- 结果：检查通过；当前端口均空闲，会在正式启动时打开对应独立终端。

### 2026-06-04 Phase 2：统一消息模型

状态：已完成。

完成内容：

1. bridge event 统一补齐 `schema_version`、`conversation_id`、`message_id`。
2. 新事件写入时由 `complete_bridge_event()` 生成统一字段。
3. 旧持久化事件读取时也会自动归一化为统一消息模型。
4. `message_id` 规则：
   - 有 `client_message_id` 时：`client:<client_message_id>:<role>`
   - 无 `client_message_id` 时：`bridge:<id>`
5. `conversation_id` 规则：`<channel>:<chat_id>`。
6. stage-web bridge event 类型增加统一字段。
7. stage-web 事件响应在字段缺失时会按同样规则补齐，兼容旧 bridge event。
8. QQ 路径、Web 路径、Agent WebUI mirror 路径都复用同一 bridge event 完成逻辑。

修改范围：

- `xiaomiao/bridge_event_store.py`
- `xiaomiao/desktop_bridge.py`
- `test/xiaomiao/test_desktop_bridge.py`
- `test/xiaomiao/test_desktop_bridge_persistence.py`
- `xiaomiaobot/packages/stage-layouts/src/xiaomiao-bridge.ts`
- `xiaomiaobot/packages/stage-ui/src/xiaomiao-bridge-events.test.ts`

验证结果：

- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest test/xiaomiao/test_desktop_bridge.py test/xiaomiao/test_desktop_bridge_persistence.py -q`
- 结果：`17 passed`
- 通过：`pnpm exec vitest run packages/stage-ui/src/xiaomiao-bridge-events.test.ts`
- 结果：`1 passed / 6 passed`

### 2026-06-04 Phase 3：多模态打通

状态：已完成。

完成内容：

1. `xiaomiao/agent_backend.py` 中已存在的 `XiaomiaoAgentRequest.media` 现在会进入 OpenAI-compatible 请求体。
2. media 请求体使用 Agent API 已支持的 `content: [{ type: "text" }, { type: "image_url" }]` 格式。
3. data URL 会原样传递；本地图片文件会转成 data URL；不存在文件或非图片类型会显式报错。
4. `xiaomiao/main.py` 的 QQ 群 Pixmap 图片/表情包分支会把图片 URL 压缩成 `data:image/jpeg;base64,...` 并传入 Agent media。
5. `xiaomiao/main.py` 的 QQ 私聊 Pixmap 图片/表情包分支同样接入 Agent media。
6. stage-web 当前 active 输入面没有图片/文件上传控件；现有语音路径是转写为文本后发送，因此本 Phase 不新增空上传 UI。

修改范围：

- `xiaomiao/agent_backend.py`
- `xiaomiao/main.py`
- `test/xiaomiao/test_agent_backend.py`

验证结果：

- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest test/xiaomiao/test_agent_backend.py test/xiaomiao/test_desktop_bridge.py test/xiaomiao/test_desktop_bridge_persistence.py -q`
- 结果：`26 passed`
- 通过：`conda run --no-capture-output -n xiaomiao python -m py_compile xiaomiao/main.py`
- 结果：通过
- 通过：`pnpm exec vitest run packages/stage-ui/src/xiaomiao-bridge-events.test.ts`
- 结果：`1 passed / 6 passed`

### 2026-06-04 Phase 4：权限与工具分层

状态：已完成。

完成内容：

1. `xiaomiao/agent_backend.py` 发往 Agent API 的请求体已携带 `channel`、`chat_id`、`user_id`。
2. `xiaomiaoAgent/nanobot/api/server.py` 会解析 JSON 与 multipart 请求中的来源字段。
3. Agent API 会把来源字段透传到 `AgentLoop.process_direct()`，不再把所有 API 请求硬编码为 `api/default/user`。
4. `AgentLoop.process_direct()` 支持 `sender_id` 与 `metadata`，并把 metadata 写入 `InboundMessage`。
5. Agent API 会生成 `channel_policy`：`qq-group` 为 `low_risk`，其他 API 来源默认为 `trusted`。
6. `ToolRegistry` 支持请求上下文，`low_risk` 策略只暴露 `read_file`、`list_dir`、`grep`、`glob`、`web_search`、`web_fetch`。
7. 即使隐藏工具被历史上下文或模型直接调用，`ToolRegistry.prepare_call()` 也会显式返回 blocked by channel policy 错误。

修改范围：

- `xiaomiao/agent_backend.py`
- `xiaomiaoAgent/nanobot/api/server.py`
- `xiaomiaoAgent/nanobot/agent/loop.py`
- `xiaomiaoAgent/nanobot/agent/tools/registry.py`
- `test/xiaomiao/test_agent_backend.py`
- `xiaomiaoAgent/tests/test_openai_api.py`
- `xiaomiaoAgent/tests/tools/test_tool_registry.py`

验证结果：

- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest test/xiaomiao/test_agent_backend.py test/xiaomiao/test_desktop_bridge.py test/xiaomiao/test_desktop_bridge_persistence.py -q`
- 结果：`26 passed`
- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest tests/test_openai_api.py tests/tools/test_tool_registry.py -q`（工作目录：`xiaomiaoAgent`）
- 结果：`27 passed`
- 通过：`conda run --no-capture-output -n xiaomiao python -m py_compile xiaomiao/agent_backend.py xiaomiao/main.py xiaomiaoAgent/nanobot/api/server.py xiaomiaoAgent/nanobot/agent/loop.py xiaomiaoAgent/nanobot/agent/tools/registry.py`
- 结果：通过
- 通过：`pnpm exec vitest run packages/stage-ui/src/xiaomiao-bridge-events.test.ts`
- 结果：`1 passed / 6 passed`

### 2026-06-05 Phase 5：模块边界治理

状态：已完成。

完成内容：

1. 新增 `xiaomiao/qq_agent_bridge.py`，把 QQ Agent turn、Agent reply、bridge payload 组装收口到独立边界。
2. `xiaomiao/main.py` 群聊和私聊普通 AI 分支改为调用 `build_qq_agent_reply()` 与 `publish_qq_agent_reply()`。
3. 保留原有顺序：先发送 QQ 回复，再发布 bridge 同步事件。
4. `qq_agent_bridge.py` 收口 QQ 图片 URL 解析、商城表情包 URL 生成和 Agent media URL 转换纯函数。
5. 新增 `xiaomiao/qq_permissions.py`，封装 `has_manage_permission()` 与 `has_super_permission()`。
6. `xiaomiao/main.py` 中重启、runcommand、禁言、解禁、踢出等高风险入口已改用权限纯函数。
7. 新增 `test/xiaomiao/test_qq_agent_bridge.py` 与 `test/xiaomiao/test_qq_permissions.py`，为 QQ 普通消息、图片/media 规则、bridge payload、权限判断提供独立测试入口。

修改范围：

- `xiaomiao/main.py`
- `xiaomiao/qq_agent_bridge.py`
- `xiaomiao/qq_permissions.py`
- `test/xiaomiao/test_qq_agent_bridge.py`
- `test/xiaomiao/test_qq_permissions.py`

验证结果：

- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest test/xiaomiao/test_qq_agent_bridge.py test/xiaomiao/test_qq_permissions.py test/xiaomiao/test_agent_backend.py test/xiaomiao/test_desktop_bridge.py test/xiaomiao/test_desktop_bridge_persistence.py -q`
- 结果：`36 passed`
- 通过：`conda run --no-capture-output -n xiaomiao python -m pytest tests/test_openai_api.py tests/tools/test_tool_registry.py -q`（工作目录：`xiaomiaoAgent`）
- 结果：`27 passed`
- 通过：`conda run --no-capture-output -n xiaomiao python -m py_compile xiaomiao/main.py xiaomiao/qq_agent_bridge.py xiaomiao/qq_permissions.py`
- 结果：通过
- 通过：`pnpm exec vitest run packages/stage-ui/src/xiaomiao-bridge-events.test.ts`
- 结果：`1 passed / 6 passed`
- 通过：限定本次修改文件的 `git diff --check`
- 结果：无空白错误；完整 `git diff --check` 会扫到既有 `.pytest-tmp-*` 权限噪声。

## 1. 目标

本计划只回答一个问题：当前 `xiaomiaoAgent` 与 `xiaomiaobot` 哪些已经打通，哪些只是半打通，哪些重复或暂未使用，以及后续应该怎样收敛成稳定的三端互通系统。

三端在本文中指：

1. Web 端：`xiaomiaobot/apps/stage-web`
2. QQ 端：`xiaomiao/main.py + NapCat/OneBot`
3. Agent 端：`xiaomiaoAgent` API、gateway、WebUI、tools、session

当前结论：普通文本对话已经通过 `xiaomiaoAgent API :8900` 收敛到同一个 Agent 能力层；三端消息同步已经有事件通道雏形，但还没有形成唯一消息源。重复最大的是 QQ 接入、聊天 UI、会话历史、语音/多模态和配置面。未用最大的是 `xiaomiaoAgent` 多平台 channel、`xiaomiaobot` 多数 app/service，以及 Agent 原生工具对 QQ/Web 的权限化暴露。

## 2. 当前已打通链路

### 2.1 Web 到 Agent

`stage-web` 文本输入会走本地 bridge：

```text
stage-web
  -> http://127.0.0.1:5519/v1/chat/completions
  -> xiaomiao/desktop_bridge.py
  -> xiaomiao/main.py generate_desktop_reply()
  -> xiaomiao/agent_backend.py
  -> http://127.0.0.1:8900/v1/chat/completions
  -> xiaomiaoAgent AgentLoop
```

证据：

- `xiaomiaobot/packages/stage-layouts/src/xiaomiao-bridge.ts:74` 定义 `requestXiaomiaoBridgeReply()`。
- `xiaomiaobot/packages/stage-layouts/src/xiaomiao-bridge.ts:80` 固定请求 `http://127.0.0.1:5519/v1/chat/completions`。
- `xiaomiao/desktop_bridge.py:322` 处理 `/v1/chat/completions`。
- `xiaomiao/main.py:192` 的 `generate_desktop_reply()` 进入 `generate_agent_reply()`。
- `xiaomiao/agent_backend.py:10` 默认 Agent API 是 `http://127.0.0.1:8900/v1/chat/completions`。
- `xiaomiao/agent_backend.py:75` 请求体带 `session_id`。
- `xiaomiaoAgent/nanobot/api/server.py:228` 将 `session_id` 映射成 `api:<session_id>`。

### 2.2 QQ 到 Agent

QQ 普通 AI 回复由 `xiaomiao/main.py` 接入，而不是直接启用 Agent 自带 QQ channel：

```text
NapCat / OneBot :5004
  -> xiaomiao/main.py
  -> generate_agent_reply()
  -> xiaomiaoAgent API :8900
  -> publish_bridge_exchange()
  -> bridge_events.jsonl
  -> stage-web 轮询展示
```

证据：

- `xiaomiao/main.py:42` 引入 Hyper `Listener, Events, Logger, Manager, Segments`。
- `xiaomiao/main.py:2203` 群聊普通 AI 分支调用 `generate_agent_reply()`。
- `xiaomiao/main.py:2224` 群聊回复后调用 `publish_bridge_exchange()`。
- `xiaomiao/main.py:2782` 私聊普通 AI 分支调用 `generate_agent_reply()`。
- `xiaomiao/main.py:2801` 私聊回复后调用 `publish_bridge_exchange()`。

### 2.3 Agent WebUI 到 bridge 事件

Agent WebUI/gateway 只有在 `chat_id == "xiaomiao-unified"` 时加入统一链路：

- `xiaomiaoAgent/nanobot/channels/websocket.py:68` 定义 `XIAOMIAO_UNIFIED_CHAT_ID = "xiaomiao-unified"`。
- `xiaomiaoAgent/nanobot/channels/websocket.py:69` 映射到 `api:xiaomiao-unified`。
- `xiaomiaoAgent/nanobot/channels/websocket.py:964` 对该 chat_id 返回统一 session key。
- `xiaomiaoAgent/nanobot/channels/websocket.py:972` 非统一 chat_id 不镜像到 bridge。
- `xiaomiaoAgent/nanobot/channels/websocket.py:1451` 用户输入时镜像 user 事件。
- `xiaomiaoAgent/nanobot/channels/websocket.py:1545` 非工具/进度类 assistant 消息镜像 assistant 事件。

### 2.4 stage-web 事件同步

`stage-web` 会轮询 bridge 事件，把 QQ 或 Agent WebUI 的消息补进当前聊天历史：

- `xiaomiaobot/apps/stage-web/src/pages/index.vue:67` 保存 bridge event cursor。
- `xiaomiaobot/apps/stage-web/src/pages/index.vue:96` 请求 bridge events。
- `xiaomiaobot/apps/stage-web/src/pages/index.vue:100` 调用 `appendXiaomiaoBridgeEvents()`。
- `xiaomiaobot/packages/stage-layouts/src/xiaomiao-bridge.ts:145` 定义 `requestXiaomiaoBridgeEvents()`。
- `xiaomiaobot/packages/stage-layouts/src/xiaomiao-bridge.ts:200` 定义 `appendXiaomiaoBridgeEvents()`。
- `xiaomiaobot/packages/stage-layouts/src/xiaomiao-bridge.ts:209` 默认跳过 `source === "web"`，避免本端重复显示。

## 3. 没完全打通的功能

### 3.1 三端 session 不是全局统一

当前统一依赖一个特例 session：`xiaomiao-unified`。

- 根目录 `config.json:6` 配置 `xiaomiao_agent.session_id = "xiaomiao-unified"`。
- `xiaomiaoAgent/.nanobot/config.json:20` 的 `unifiedSession` 仍是 `false`。
- `xiaomiaoAgent/nanobot/agent/loop.py:542` 只有启用 unified session 时才使用全局 `UNIFIED_SESSION_KEY`。
- `xiaomiaoAgent/nanobot/channels/websocket.py:955` 普通 WebUI session 仍是 `websocket:<id>`。

影响：

1. QQ 和 stage-web 主路径进入 `api:xiaomiao-unified`。
2. Agent WebUI 只有选择或附着 `xiaomiao-unified` 才进入同一上下文。
3. 普通 WebUI 新聊天仍会产生独立 `websocket:<uuid>` 上下文。

规划：不要直接把 `unifiedSession` 改成 true。先设计 `UnifiedConversationId` 映射层，让 `web`、`qq-private`、`qq-group`、`agent-webui` 都显式声明要进入哪个会话。

### 3.2 消息同步不是唯一消息源

当前有三套历史：

1. `xiaomiaoAgent` session 文件：Agent 真正上下文。
2. `xiaomiaobot` IndexedDB/Pinia chat session：Web UI 本地历史。
3. `xiaomiao/runtime/bridge_events.jsonl`：跨端展示事件。

证据：

- `xiaomiaobot/packages/stage-ui/src/stores/chat/session-store.ts:240` 保存 stage-web session。
- `xiaomiaobot/packages/stage-ui/src/database/repos/chat-sessions.repo.ts:21` 保存单个聊天会话。
- `xiaomiao/bridge_event_store.py:7` bridge 事件落到 `runtime/bridge_events.jsonl`。
- `xiaomiaoAgent/nanobot/api/server.py:228` Agent API 侧生成 `api:<session_id>`。

影响：stage-web 展示的消息不等于 Agent 的完整 session；Agent WebUI 展示的是 Agent session；bridge 事件只是镜像，不是权威存储。

规划：后续应把 `bridge_events` 升级成“消息事件总线 API”，并明确权威来源。推荐权威来源为 Agent session，bridge event 只作为跨端投递日志。

### 3.3 stage-web 主动发送不会从事件流回放

Web 主动发送时直接追加本地历史：

- `xiaomiaobot/packages/stage-layouts/src/components/Widgets/ChatArea.vue:63` `sendChatText()`。
- `xiaomiaobot/packages/stage-layouts/src/components/Widgets/ChatArea.vue:69` 直接 `setSessionMessages()`。
- `xiaomiaobot/apps/stage-web/src/pages/index.vue:82` 语音文本发送到 bridge。
- `xiaomiaobot/apps/stage-web/src/pages/index.vue:84` 直接追加本地 exchange。

同时 `appendXiaomiaoBridgeEvents()` 默认跳过 web 事件。因此 Web 端“自己发的消息”和“从事件流来的消息”不是同一路径。

规划：增加 `client_message_id` 和 `event_id`，Web 端发送后也由事件流确认落库；本地可以乐观显示，但最终以事件确认去重。

### 3.4 多模态没有贯穿

Agent API 支持 multipart、base64 图片和 media path：

- `xiaomiaoAgent/nanobot/api/server.py:195` 说明 `/v1/chat/completions` 支持 JSON 和 multipart。
- `xiaomiaoAgent/nanobot/api/server.py:206` 解析 multipart。
- `xiaomiaoAgent/nanobot/api/server.py:215` 从 JSON 解析 media。

但 `xiaomiao/agent_backend.py` 的 `XiaomiaoAgentRequest.media` 还没有写进请求体：

- `xiaomiao/agent_backend.py:30` 声明 `media`。
- `xiaomiao/agent_backend.py:73` 到 `:79` 只发送文本、session_id、model。

影响：QQ 图片、表情包、Web 上传、语音附件暂时不能稳定进入 Agent 多模态上下文。

规划：先补文本 + 图片单通路，再补语音。不要让 QQ 图片分支继续散落在 `main.py` 巨型函数内。

## 4. 重复能力

### 4.1 QQ 接入重复

当前实际运行 QQ：

- `xiaomiao/main.py + NapCat/OneBot + Hyper`

Agent 自带 QQ channel：

- `xiaomiaoAgent/nanobot/channels/qq.py`
- `xiaomiaoAgent/.nanobot/config.json:150` 存在 `qq` channel 配置。
- `xiaomiaoAgent/.nanobot/config.json:151` 当前 `enabled = false`。

规划：短期保留 `xiaomiao/main.py` 作为 QQ 权威入口；中期抽象出 `QqIngressAdapter`；长期再评估迁移到 `xiaomiaoAgent` 原生 channel，而不是两边同时处理同一个 QQ 账号。

### 4.2 聊天 UI 重复

当前至少两个聊天界面：

1. `xiaomiaobot stage-web`：角色表现、语音、字幕、聊天历史。
2. `xiaomiaoAgent WebUI`：Agent session、工具进度、文件/图片/多会话管理。

规划：不要强行合并 UI。应定义职责：

- stage-web：用户陪伴入口、语音/表情/角色表现。
- Agent WebUI：调试、工具、session 管理、权限配置。
- 两者共享同一个 session/event API。

### 4.3 语音与转写重复

`stage-web` 有浏览器端录音、VAD、转写流程：

- `xiaomiaobot/apps/stage-web/src/pages/index.vue:49` 使用 `transcribeForRecording()`。
- `xiaomiaobot/packages/stage-layouts/src/components/Widgets/ChatArea.vue:87` 使用 streaming transcription。

Agent channel 基类也有转写 provider 支持：

- `xiaomiaoAgent/nanobot/channels/base.py:51` 引入 OpenAI transcription。
- `xiaomiaoAgent/nanobot/channels/base.py:58` 引入 Groq transcription。

规划：Web 端继续负责麦克风采集和前端体验；Agent 端负责统一多模态消息结构和转写服务能力。不要在两端各自维护不可互通的音频语义。

### 4.4 配置面重复

配置来源包括：

- 根目录 `config.json`
- `xiaomiao/config.json`
- `xiaomiaoAgent/.nanobot/config.json`
- stage-web 启动时读取 bridge config

证据：

- `xiaomiao/unified_config.py:13` 默认统一配置路径是根目录 `config.json`。
- `xiaomiao/unified_config.py:53` 支持保存小喵 Agent 自定义配置。
- `xiaomiaobot/apps/stage-web/src/App.vue:127` 读取 bridge config。
- `xiaomiaobot/apps/stage-web/src/App.vue:138` 保存 bridge config。

规划：根目录 `config.json` 只放跨子系统共享配置；各子系统本地配置只放运行时细节。配置 UI 写根配置时必须明确“需重启哪些服务”。

## 5. 暂未使用或低使用模块

### 5.1 xiaomiaoAgent 低使用模块

当前 `.nanobot/config.json` 只启用 websocket channel：

- `xiaomiaoAgent/.nanobot/config.json:196` websocket channel。
- `xiaomiaoAgent/.nanobot/config.json:197` `enabled = true`。
- `xiaomiaoAgent/.nanobot/config.json:150` QQ channel 存在但未启用。
- `xiaomiaoAgent/.nanobot/config.json:40`、`:48`、`:182`、`:223`、`:233` 等多平台 channel 均未启用。

低使用能力：

- 原生 QQ、Telegram、Discord、Slack、Feishu、WeChat、WhatsApp 等 channel。
- Cron、Heartbeat、Dream 等 gateway 后台能力，当前不是三端消息闭环核心。
- 文件系统、Shell、Web、MCP、Subagent 等工具还没有按 QQ/Web 权限分层暴露。

### 5.2 xiaomiaobot 低使用模块

当前启动脚本只启动 `apps/stage-web`：

- `start-all.cmd:206` 启动 xiaomiaobot web。
- `start-all.cmd:211` 进入 `xiaomiaobot/apps/stage-web`。

未纳入当前三端闭环的 app：

- `apps/component-calling`
- `apps/server`
- `apps/stage-pocket`
- `apps/stage-tamagotchi`
- `apps/ui-server-auth`

未纳入当前三端闭环的 service：

- `services/discord-bot`
- `services/telegram-bot`
- `services/satori-bot`
- `services/minecraft`
- `services/twitter-services`
- `services/computer-use-mcp`

规划：先不要删除这些上游 monorepo 能力。对当前小喵目标，只把 `stage-web`、`stage-layouts`、`stage-ui`、音频相关 package 标记为 active surface，其余归为 upstream reserved。

## 6. 推荐目标架构

目标不是把所有代码塞进一个进程，而是统一协议和状态：

```text
QQ / Web / Agent WebUI
  -> Ingress Adapter
  -> Unified Conversation API
  -> xiaomiaoAgent Session + Tools + Memory
  -> Message Event Bus
  -> QQ / stage-web / Agent WebUI 同步展示
```

核心规则：

1. `xiaomiaoAgent` 是 Agent 能力权威。
2. `xiaomiao` 是 QQ 命令和 NapCat 登录缓存权威。
3. `xiaomiaobot` 是角色表现和 Web 交互权威。
4. session/event 协议必须独立于 UI。
5. 所有跨端消息都必须有稳定 `conversation_id`、`message_id`、`source`、`channel`、`role`、`content`、`media`、`timestamp`。

## 7. 分阶段路线

### Phase 1：固化现有闭环

目标：把当前可跑链路变成可验证、可定位、可恢复。

任务：

1. 为 `5519 /events` 增加 `client_message_id` 字段。
2. stage-web 主动发送也写入/读取同一事件确认链。
3. Agent WebUI 默认提供“加入小喵统一会话”入口，而不是靠用户猜 `xiaomiao-unified`。
4. `start-all.cmd --check` 增加统一 session 可读性检查。
5. 给 `bridge_events.jsonl` 增加损坏行隔离和保留策略。

验收：

- QQ 发消息后，stage-web 和 Agent WebUI 都能看到。
- stage-web 发消息后，QQ 事件流不重复，Agent WebUI 能看到。
- Agent WebUI 在统一会话发消息后，stage-web 能看到。

### Phase 2：统一消息模型

目标：从“事件镜像”升级为“统一消息总线”。

任务：

1. 定义 `UnifiedMessage` schema。
2. bridge event store 改为 schema 校验。
3. stage-web chat item 与 `UnifiedMessage` 建立纯转换层。
4. Agent WebUI session message 与 `UnifiedMessage` 建立转换层。
5. QQ message segment 转成文本/media 的规范结构。

验收：

- 同一条消息跨端 ID 一致。
- Web 乐观消息能被服务端确认消息替换。
- 重启 stage-web 后能从 bridge/Agent session 恢复统一会话。

### Phase 3：多模态打通

目标：图片、表情包、语音都能进入 Agent，而不是只在某一端本地处理。

任务：

1. `xiaomiao/agent_backend.py` 把 `media` 转成 Agent API 可识别内容。
2. QQ 图片/表情包下载逻辑从 `main.py` 抽到 media service。
3. stage-web 上传/录音结果转成统一 media。
4. Agent API 返回 media/artifact 时，stage-web 和 QQ 都有展示策略。

验收：

- QQ 图片提问能进入 Agent 多模态。
- stage-web 上传图片能进入同一 session。
- Agent 生成图片或文件时，WebUI 可见，stage-web 可展示链接或缩略信息。

### Phase 4：权限与工具分层

状态：已完成。当前已完成来源透传、`channel_policy` 生成、QQ 群低风险工具过滤和隐藏工具拦截。

目标：Agent tools 可以服务三端，但不会直接把高危能力暴露给 QQ 或网页。

任务：

1. 定义 `channel_policy`：web、qq-private、qq-group、agent-webui。
2. 工具分级：只读、网络、文件、Shell、MCP、系统操作。
3. QQ 群默认只允许低风险工具。
4. Agent WebUI 可显示工具轨迹，stage-web 只显示适合用户的摘要。

验收：

- QQ 群不能触发 Shell/文件写入。
- Web 端工具错误不静默吞掉。
- Agent WebUI 能看到工具进度，stage-web 不被调试噪声污染。

### Phase 5：模块边界治理

状态：已完成。当前已拆出 QQ Agent reply/bridge payload、QQ media URL 规则、QQ permissions 纯函数边界；`xiaomiao/main.py` 仍保留为唯一 QQ 权威入口。

目标：减少重复实现和巨型文件风险。

任务：

1. `xiaomiao/main.py` 拆出 QQ ingress、commands、agent reply、bridge publish、media、permissions。
2. `xiaomiaobot` 标注 active packages 与 upstream reserved packages。
3. `xiaomiaoAgent` 明确 API/gateway/channel/tool 的小喵使用边界。
4. 决策是否迁移到 Agent 原生 QQ channel；迁移前保留 `xiaomiao/main.py` 为唯一 QQ 权威入口。

验收：

- QQ 普通消息、命令消息、图片消息各有独立测试入口。
- stage-web 只依赖一个小喵 bridge client。
- Agent WebUI 和 stage-web 不再各自猜 session 规则。

### Phase 6：真实启动与端到端验收

状态：已完成。当前真实启动链路已通过 `start-all.cmd` 拉起，NapCat、`main.py`、Agent API、gateway、stage-web、Agent WebUI 均在线；Agent API、桌面桥接、Agent WebUI WebSocket 都已写入同一统一会话并同步到 bridge event。

目标：确认本地 QQ 登录缓存、独立终端启动工作流、Web 端、QQ 端、Agent 端的真实运行状态可用。

完成内容：

1. `start-all.cmd --check` 启动前通过，确认目标端口空闲。
2. `start-all.cmd` 真实启动后再次 `--check` 通过，确认所有必要终端与服务在线。
3. NapCat/QQ OneBot `5004`、Agent API `8900`、Agent gateway `8765`、`main.py`/桌面桥接 `5519`、stage-web `5175`、Agent WebUI `5174` 均健康。
4. Agent API 直连 `session_id=xiaomiao-unified` 返回 `OK ✅`。
5. 桌面桥接 `/v1/chat/completions` 返回 `OK ✅`，并写入 `web:stage-web` bridge event。
6. Agent WebUI WebSocket 通过 bootstrap token 连接、attach `xiaomiao-unified`，流式返回 `PHASE6_WEBUI_WS_OK`。
7. bridge events 已确认存在 `agent-webui:xiaomiao-unified` 的 user/assistant 同步事件。
8. gateway session API 已确认 `api:xiaomiao-unified` 含本轮 Agent API、bridge、Agent WebUI 消息与回复。

验收：

- `cmd /c call start-all.cmd --check`：通过。
- `8900/v1/chat/completions`：统一 session 直连通过。
- `5519/v1/chat/completions` 与 `/v1/xiaomiao/events`：桥接请求和事件同步通过。
- `8765/webui/bootstrap` 与 WebSocket：token、attach、流式回复通过。
- `5175` stage-web 和 `5174` Agent WebUI 页面：HTTP 200。

### Phase 7：残留风险 hardening

状态：已完成。已完成 QQ 双入口阻断、全局 `unifiedSession=true` 阻断、非统一 WebUI session 不同步回归测试、`5519` bridge loopback 访问边界、stage-web bridge 确认事件权威回放。

目标：围绕真实运行后仍可能造成重复回复、误同步、边界暴露的问题做小步 hardening，不迁移 QQ channel。

已完成内容：

1. `start-all.cmd` 的 preflight 调用 `start-all-health.ps1 config-safe`。
2. `config-safe` 会解析 `xiaomiaoAgent/.nanobot/config.json`，当 `channels.qq.enabled=true` 时明确失败。
3. 错误信息声明当前 QQ 权威入口是 `xiaomiao/main.py + NapCat`，避免同时启用 Agent 原生 QQ channel。
4. `start-all.cmd --check` 分支改为 `call :check_services` 后退出，避免 Windows batch 标签跳转异常。
5. `start-all.cmd` 已转回 CRLF，修复 LF 下 `cmd` 标签扫描报 `cannot find the batch label` 的问题。
6. 新增 WebSocket bridge 边界测试：非 `xiaomiao-unified` 的 WebUI/WebSocket 会话不会镜像到 bridge。
7. `5519` desktop bridge 增加 loopback 客户端检查，非本机地址会得到显式 `403 bridge_loopback_only`。
8. 复核 Agent API 停止、HTTP 错误、空回复、超时路径，当前均有显式失败测试覆盖。
9. `config-safe` 增加 `agents.defaults.unifiedSession=true` 拦截，要求使用显式 `xiaomiao-unified` 路由。
10. stage-web 主页面轮询 bridge events 时启用 `includeWeb: true`，刷新后可从 bridge 回放 web 自己的确认事件。
11. QQ 本地命令 `帮助`、`关于`、`读图` 改为精确匹配，避免自然语言中出现 `关于`、`帮助`、`读图` 时误触发本地命令。
12. `start-all.cmd` 新启动终端默认最小化，仍保持一个服务一个独立终端和串行健康检查。

验证：

- `F:\Anaconda3\envs\xiaomiao\python.exe -m pytest tests\channels\test_websocket_xiaomiao_bridge.py -q`：`4 passed`。
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-all-health.ps1 config-safe -ConfigPath xiaomiaoAgent\.nanobot\config.json`：通过。
- `cmd /c call start-all.cmd --check`：通过。
- `F:\Anaconda3\envs\xiaomiao\python.exe -m pytest test\xiaomiao\test_desktop_bridge.py test\xiaomiao\test_agent_backend.py -q`：`23 passed`。
- `F:\Anaconda3\envs\xiaomiao\python.exe -m pytest test\xiaomiao\test_qq_agent_bridge.py -q`：`8 passed`。
- `F:\Anaconda3\envs\xiaomiao\python.exe -m py_compile xiaomiao\desktop_bridge.py xiaomiao\agent_backend.py`：通过。
- `F:\Anaconda3\envs\xiaomiao\python.exe -m py_compile xiaomiao\main.py xiaomiao\qq_agent_bridge.py`：通过。
- 临时风险配置 `agents.defaults.unifiedSession=true`：`config-safe` 明确失败。
- `pnpm exec vitest run packages/stage-ui/src/xiaomiao-bridge-events.test.ts`：`7 passed`。
- `git diff --check` 限定本次修改文件：无 whitespace 错误，仅有 LF/CRLF 提示。

## 8. 风险

1. 直接开启 `unifiedSession=true` 可能把所有 channel、cron、heartbeat 都混进同一上下文；Phase 7 已在启动前阻断该组合。
2. 同时启用 `xiaomiao/main.py` QQ 和 `xiaomiaoAgent` 原生 QQ channel 会造成重复回复；Phase 7 已在启动前阻断该组合。
3. stage-web 本地历史与 Agent session 长期并存，会继续制造“看得到但上下文不一致”的问题；Phase 7 已让主页面回放 web 确认事件，降低刷新后依赖 IndexedDB 的风险。
4. Agent tools 暴露到 QQ 群前必须做权限隔离。
5. `5519` bridge 当前是本机信任接口，不应直接暴露到公网；Phase 7 已增加 loopback 客户端边界。
6. QQ 自然语言提示中可能包含本地命令词；当前 `帮助`、`关于`、`读图` 已改为精确匹配。

## 9. 最小测试矩阵

### 回归测试

1. `start-all.cmd --check` 全部通过。
2. `5519/v1/xiaomiao/status` 返回 bridge 可用。
3. `8900/v1/chat/completions` 携带 `session_id=xiaomiao-unified` 可回复。
4. `8765` WebUI token、session list、WS 握手可用。

### 三端同步测试

1. QQ 私聊发送 `确认同步-qq-private`，stage-web 出现 user/assistant。
2. QQ 群发送 `确认同步-qq-group`，stage-web 出现群来源。
3. stage-web 发送 `确认同步-web`，Agent session `api:xiaomiao-unified` 可读到。
4. Agent WebUI 在 `xiaomiao-unified` 发送 `确认同步-agent-webui`，stage-web 出现 agent-webui 来源。

### 边界测试

1. Agent API 停止时，QQ 普通 AI 回复显式失败，不让 bridge 假成功。
2. NapCat 停止时，`main.py` 退出并暴露 OneBot 连接错误。
3. bridge event store 有坏行时，错误可定位，不污染后续事件。
4. stage-web 刷新后不会重复追加历史消息。
5. 非统一 WebUI session 不应同步到 stage-web；Phase 7 已补回归测试。

## 10. 下一步执行顺序

推荐优先级：

1. 已完成事件协议、stage-web 消息确认与去重、Agent WebUI 统一会话入口。
2. 已完成多模态 media 的基础接入、权限与工具分层、QQ 模块边界治理。
3. 已完成真实启动与三端端到端验收。
4. 已完成残留风险 hardening，未迁移 QQ channel。
5. 评估 Agent 原生 QQ channel 前，必须先保证不会与 `xiaomiao/main.py` 产生重复回复。

这条路线能保留当前已经跑通的本地 QQ 登录缓存、NapCat 入口和 `start-all.cmd` 独立终端工作流，同时逐步消除“看起来同步但不是同一状态源”的核心问题。
