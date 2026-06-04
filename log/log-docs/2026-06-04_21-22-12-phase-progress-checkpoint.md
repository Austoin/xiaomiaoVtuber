# 2026-06-04 Phase Progress Checkpoint

## 当前主目标

按 `plan/2026-06-04_20-51-53-xiaomiao-agent-bot-deep-plan.md` 推进：

1. 深度阅读 `xiaomiaoAgent` 和 `xiaomiaobot`。
2. 梳理未打通、重复、未使用能力。
3. 按 Phase 逐步实现。
4. 每完成一个 Phase 更新计划文档并询问是否继续。

## 已完成

### 规划文档

已创建并持续更新：

- `plan/2026-06-04_20-51-53-xiaomiao-agent-bot-deep-plan.md`

### Phase 1：固化现有闭环

状态：已完成。

完成内容：

1. 后端 bridge event 支持 `client_message_id`。
2. `/v1/chat/completions` 和 `POST /v1/xiaomiao/events` 都可写入该字段。
3. 持久化重载会保留 `client_message_id`。
4. stage-web bridge client 支持 `clientMessageId`。
5. stage-web 常规输入、移动端输入、页面级语音转写会生成并传入 `clientMessageId`。
6. 本地乐观消息与 bridge 回放事件使用 `clientMessageId + role` 去重。
7. 坏 bridge event 行会隔离到 `bridge_events.invalid.jsonl`。
8. `start-all.cmd --check` 增加统一 session 可读性检查。

验证：

- `conda run --no-capture-output -n xiaomiao python -m pytest test/xiaomiao/test_desktop_bridge.py test/xiaomiao/test_desktop_bridge_persistence.py -q`
- 结果：`17 passed`
- `pnpm exec vitest run packages/stage-ui/src/xiaomiao-bridge-events.test.ts`
- 结果：`6 passed`
- PowerShell 解析 `scripts/start-all-health.ps1`：通过
- `start-all.cmd --check`：通过

### Phase 2：统一消息模型

状态：已完成。

完成内容：

1. bridge event 统一补齐 `schema_version`、`conversation_id`、`message_id`。
2. 新事件写入和旧事件重载都走统一字段归一化。
3. `message_id` 规则：
   - 有 `client_message_id`：`client:<client_message_id>:<role>`
   - 无 `client_message_id`：`bridge:<id>`
4. `conversation_id` 规则：`<channel>:<chat_id>`。
5. stage-web bridge event 类型与归一化逻辑已同步。
6. QQ、Web、Agent WebUI mirror 路径都复用统一 bridge event 完成逻辑。

验证：

- Python bridge tests：`17 passed`
- Vitest bridge event tests：`6 passed`

### Phase 3：多模态打通

状态：已完成。

完成内容：

1. `xiaomiao/agent_backend.py` 会把 `XiaomiaoAgentRequest.media` 写入 Agent API 请求体。
2. media 使用 OpenAI-compatible content parts：文本 + `image_url`。
3. data URL 原样传递，本地图片文件会转 data URL。
4. QQ 群 Pixmap 图片/表情包会压缩为 `data:image/jpeg;base64,...` 后传入 Agent media。
5. QQ 私聊 Pixmap 图片/表情包同样接入 Agent media。
6. stage-web 当前 active 输入面没有图片/文件上传控件；语音路径仍是转写成文本后发送。

验证：

- Python tests：`26 passed`
- `xiaomiao/main.py` py_compile：通过
- Vitest bridge event tests：`6 passed`

### Phase 4：权限与工具分层

状态：已完成。

完成内容：

1. `xiaomiao/agent_backend.py` 请求体携带 `channel`、`chat_id`、`user_id`。
2. Agent API 支持从 JSON 与 multipart 请求解析来源字段。
3. Agent API 将来源字段传给 `AgentLoop.process_direct()`，不再统一硬编码为 `api/default/user`。
4. `process_direct()` 支持 `sender_id` 与 `metadata`，并写入 `InboundMessage`。
5. Agent API 按来源生成 `channel_policy`：`qq-group` 为 `low_risk`，其他 API 来源默认为 `trusted`。
6. `ToolRegistry` 支持请求上下文，`low_risk` 只暴露 `read_file`、`list_dir`、`grep`、`glob`、`web_search`、`web_fetch`。
7. 隐藏工具被直接调用时，`prepare_call()` 会显式返回 blocked by channel policy 错误。

验证：

- Python main bridge tests：`26 passed`
- Agent API + ToolRegistry tests：`27 passed`
- Python py_compile：通过
- Vitest bridge event tests：`6 passed`

### Phase 5：模块边界治理

状态：已完成。

完成内容：

1. 新增 `xiaomiao/qq_agent_bridge.py`，收口 QQ Agent turn、Agent reply、bridge payload。
2. 群聊/私聊普通 AI 分支改用 `build_qq_agent_reply()` 与 `publish_qq_agent_reply()`。
3. 保留原行为顺序：先发送 QQ 回复，再发布 bridge 同步事件。
4. QQ 图片 URL 解析、商城表情包 URL、Agent media URL 转换规则已进入 `qq_agent_bridge.py`。
5. 新增 `xiaomiao/qq_permissions.py`，封装 `has_manage_permission()` 与 `has_super_permission()`。
6. 重启、runcommand、禁言、解禁、踢出入口已改用权限纯函数。
7. 新增 `test/xiaomiao/test_qq_agent_bridge.py` 与 `test/xiaomiao/test_qq_permissions.py`。

验证：

- Python main bridge + QQ boundary tests：`36 passed`
- Agent API + ToolRegistry tests：`27 passed`
- `xiaomiao/main.py`、`qq_agent_bridge.py`、`qq_permissions.py` py_compile：通过
- Vitest bridge event tests：`6 passed`
- 限定本次修改文件的 `git diff --check`：通过

## 正在进行

暂无。下一步应进入 Phase 6。

## 下一步建议

进入 Phase 6：建议聚焦三端真实启动与端到端验收，验证 QQ、stage-web、Agent WebUI 在统一 session 下的消息同步与工具边界表现。
