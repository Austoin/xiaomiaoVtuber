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

### Phase 6：真实启动与端到端验收

状态：已完成。

完成内容：

1. 启动前执行 `cmd /c call start-all.cmd --check`，确认目标端口空闲。
2. 执行 `cmd /c call start-all.cmd`，真实打开必要服务终端。
3. 启动后再次执行 `cmd /c call start-all.cmd --check`，所有服务健康检查通过。
4. 确认 NapCat/QQ OneBot `5004` 在线，进程为 NapCat shell 下的 `QQ.exe`。
5. 确认 xiaomiaoAgent API `8900`、gateway `8765`、`main.py`/桌面桥接 `5519` 在线。
6. 确认 stage-web `5175` 与 xiaomiaoAgent WebUI `5174` 页面均返回 HTTP 200。
7. Agent API 直连统一 session `xiaomiao-unified`，返回 `OK ✅`。
8. 桌面桥接 `/v1/chat/completions` 发送 `Phase6-bridge-health-check`，返回 `OK ✅`。
9. Agent WebUI WebSocket 通过 `/webui/bootstrap` token 连接，attach `xiaomiao-unified` 后返回 `PHASE6_WEBUI_WS_OK`。
10. bridge events 已确认记录本轮 `web:stage-web` 与 `agent-webui:xiaomiao-unified` 的 user/assistant 事件。
11. gateway session API 已确认 `api:xiaomiao-unified` 含 `Phase6-Agent-API-health-check`、`Phase6-bridge-health-check`、`Phase6-Agent-WebUI-WS-health-check` 与对应回复。

验证：

- `cmd /c call start-all.cmd --check`：启动前通过，启动后通过。
- `POST http://127.0.0.1:8900/v1/chat/completions`：返回 `OK ✅`。
- `POST http://127.0.0.1:5519/v1/chat/completions`：返回 `OK ✅`。
- `GET http://127.0.0.1:5519/v1/xiaomiao/events`：确认事件 `43/44` 为 Agent WebUI user/assistant 同步。
- `GET http://127.0.0.1:8765/api/sessions/api%3Axiaomiao-unified/messages`：带 bootstrap token 后可读，确认统一会话同步。
- `ws://127.0.0.1:8765/?client_id=phase6-ws&token=<bootstrap-token>`：收到 `ready`、`attached`、`delta`、`stream_end`。

### Phase 7：残留风险 hardening

状态：已完成。

完成内容：

1. `start-all.cmd` preflight 增加 `config-safe` 检查。
2. `scripts/start-all-health.ps1` 新增 `config-safe` 命令，解析 `xiaomiaoAgent/.nanobot/config.json`。
3. 如果 `channels.qq.enabled=true`，启动前明确失败，避免 Agent 原生 QQ channel 与 `xiaomiao/main.py + NapCat` 同时回复。
4. `start-all.cmd --check` 分支改为子过程调用，避免标签跳转异常。
5. `start-all.cmd` 转回 CRLF，修复 Windows `cmd` 对 LF batch 标签扫描不稳定的问题。
6. `test_websocket_xiaomiao_bridge.py` 新增非统一 WebSocket/WebUI 会话不镜像到 bridge 的边界测试。
7. `xiaomiao/desktop_bridge.py` 新增 loopback 客户端边界，非本机地址访问 `5519` 会得到显式 `403 bridge_loopback_only`。
8. `test_desktop_bridge.py` 新增 `is_loopback_client()` 边界测试。
9. 复核 Agent API 停止、HTTP 错误、空回复、超时路径，当前均有显式失败测试覆盖。
10. `config-safe` 增加 `agents.defaults.unifiedSession=true` 拦截，避免所有 channel、cron、heartbeat 混入同一上下文。
11. stage-web 主页面轮询 bridge events 时启用 `includeWeb: true`，刷新后可从 bridge 回放 web 自己的确认事件。
12. `xiaomiao-bridge-events.test.ts` 新增空本地历史下回放 web bridge 事件的测试。

验证：

- `F:\Anaconda3\envs\xiaomiao\python.exe -m pytest tests\channels\test_websocket_xiaomiao_bridge.py -q`
- 结果：`4 passed`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-all-health.ps1 config-safe -ConfigPath xiaomiaoAgent\.nanobot\config.json`
- 结果：通过
- `cmd /c call start-all.cmd --check`
- 结果：通过，全部服务健康
- 限定本次修改文件的 `git diff --check`
- 结果：无 whitespace 错误，仅有 LF/CRLF 提示
- `F:\Anaconda3\envs\xiaomiao\python.exe -m pytest test\xiaomiao\test_desktop_bridge.py test\xiaomiao\test_agent_backend.py -q`
- 结果：`23 passed`
- `F:\Anaconda3\envs\xiaomiao\python.exe -m py_compile xiaomiao\desktop_bridge.py xiaomiao\agent_backend.py`
- 结果：通过
- 临时风险配置 `agents.defaults.unifiedSession=true`
- 结果：`config-safe` 明确失败并提示使用显式 `xiaomiao-unified` 路由
- `pnpm exec vitest run packages/stage-ui/src/xiaomiao-bridge-events.test.ts`
- 结果：`7 passed`

### 2026-06-05 维护补丁：QQ 命令误触发、启动终端最小化与操作文档同步

状态：已完成。

触发原因：

用户在 QQ 中发送 `- 在桌面agent.txt里面写入一些关于agent的知识` 后，机器人返回了 “Build Information / Powered by NapCat.OneBot” 信息，而不是进入 xiaomiaoAgent。根因是 `xiaomiao/main.py` 使用了 `"关于" in order`、`"帮助" in order`、`"读图" in order` 这类包含匹配；当 `reminder` 为 `-` 时，自然语言里包含 `关于` 会被误判为本地“关于”命令。

完成内容：

1. `xiaomiao/qq_agent_bridge.py` 新增 `is_qq_exact_command()`，用于收口 QQ 本地命令精确匹配。
2. `test/xiaomiao/test_qq_agent_bridge.py` 新增复现测试，覆盖：
   - `关于` 可以触发本地关于命令。
   - `帮助` 可以触发本地帮助命令。
   - `在桌面agent.txt里面写入一些关于agent的知识` 不会误触发关于命令。
   - `帮助我写文件` 不会误触发帮助命令。
   - `读图总结这张图片` 不会误触发读图命令。
3. `xiaomiao/main.py` 群聊和私聊的 `帮助`、`关于`、`读图` 改为精确匹配。
4. `xiaomiao/main.py` 中与帮助、权限、关于、系统感知相关的用户可见英文提示改为中文。
5. `start-all.cmd` 所有新启动终端加 `/min`，保持一个服务一个独立终端，但默认最小化。
6. `start-all.cmd` 成功提示改为 minimized terminals，避免脚本文案与行为不一致。
7. 更新操作文档，统一说明：
   - `start-all.cmd` 串行健康检查启动。
   - 前一步失败不会打开后续服务。
   - 每个服务仍是独立终端，新启动终端默认最小化。
   - `start-all.cmd --check` 只检查，不启动窗口。
   - QQ 本地命令 `帮助`、`关于`、`读图` 使用精确匹配。
   - QQ / Web / xiaomiaoAgent WebUI 共享 `xiaomiao-unified` 和 bridge events。

已更新文档：

- `README.md`
- `docs/STARTUP.md`
- `docs/xiaomiao/README.md`
- `docs/AuBot/README.md`
- `docs/AuBot/操作文档.md`
- `xiaomiaoAgent/docs/openai-api.md`
- `plan/2026-06-04_20-51-53-xiaomiao-agent-bot-deep-plan.md`
- `log/log-docs/2026-06-04_21-22-12-phase-progress-checkpoint.md`

验证：

- `F:\Anaconda3\envs\xiaomiao\python.exe -m pytest test\xiaomiao\test_qq_agent_bridge.py -q`
- 结果：`8 passed`
- `F:\Anaconda3\envs\xiaomiao\python.exe -m py_compile xiaomiao\main.py xiaomiao\qq_agent_bridge.py`
- 结果：通过
- `cmd /c call start-all.cmd --check`
- 结果：所有服务健康检查通过
- 文档关键词扫描：
  - Batch 1 文档包含 `默认最小化`、`独立终端`、`精确匹配`。
  - Batch 2 文档包含 `start-all.cmd`、`bridge events`、`5004`、`三端同步`、`静默回退` 边界说明。

边界说明：

1. `- 关于`、`- 帮助`、`- 读图` 仍触发本地命令。
2. `- 在桌面agent.txt里面写入一些关于agent的知识` 进入普通 AI 回复链路。
3. `- 读图总结这张图片` 不再误切换 Pixmap 模式；如果要启用读图模式，应单独发送 `- 读图`。
4. `start-all.cmd` 不会合并终端；它仍保持每个服务一个终端，只是默认最小化。

## 正在进行

暂无。Phase 1 到 Phase 7 已完成。

## 下一步建议

当前计划书内已识别风险均已完成 hardening 与验证。下一步进入最终整体验收或等待用户指定新目标。
