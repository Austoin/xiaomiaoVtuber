时间：2026-06-04
任务：完整跑通 QQ、Web、Agent 三端互通与消息同步
状态：已完成运行态验收

目标：

1. 理解 `xiaomiao`、`xiaomiaobot`、`xiaomiaoAgent` 三个子系统的协作关系。
2. 确认 QQ 机器人登录一次后，本地保留 NapCat 账号配置与缓存。
3. 跑通 Web 端、QQ 端、Agent WebUI 端三端互通。
4. 确认三端消息进入同一 bridge events 与 xiaomiaoAgent 统一会话。

本次关键实现：

1. `xiaomiao/bridge_event_store.py`
   - 新增 bridge events JSONL 持久化。
   - 默认写入 `xiaomiao/runtime/bridge_events.jsonl`。
   - 支持 `XIAOMIAO_BRIDGE_EVENT_STORE` 覆盖，便于测试隔离。

2. `xiaomiao/desktop_bridge.py`
   - 启动时加载本地 bridge events。
   - 新增 `POST /v1/xiaomiao/events`，允许 Agent WebUI 写事件而不触发模型回复。
   - 保留 `/v1/xiaomiao/events` 查询能力，用于 Web 端轮询同步。

3. `xiaomiaoAgent/nanobot/channels/websocket.py`
   - 将 `chat_id=xiaomiao-unified` 映射到 `api:xiaomiao-unified`。
   - 允许 Agent WebUI 读取统一 API 会话。
   - 将 Agent WebUI 的 user/assistant 消息镜像到 xiaomiao bridge events。
   - 流式 assistant 回复在 `stream_end` 时只镜像一次完整内容。

4. `start-all.cmd`
   - 启动流程扩展为 6 步：NapCat、xiaomiaoAgent API、xiaomiaoAgent gateway、xiaomiao bridge、xiaomiaobot Web、Agent WebUI。
   - 使用 `conda run --no-capture-output -n xiaomiao`，避免 `conda activate` 未初始化。
   - xiaomiaobot Web 固定到 `5175`，避免与 Understand Anything dashboard 的 `5173` 冲突。

本次测试：

1. `conda run --no-capture-output -n xiaomiao python -m pytest test\xiaomiao\test_desktop_bridge.py test\xiaomiao\test_agent_backend.py test\xiaomiao\test_desktop_bridge_persistence.py`
   - 结果：22 passed。

2. `conda run --no-capture-output -n xiaomiao python -m pytest xiaomiaoAgent\tests\channels\test_websocket_http_routes.py xiaomiaoAgent\tests\channels\test_websocket_xiaomiao_bridge.py`
   - 结果：27 passed。

3. `.\start-all.cmd --check`
   - 结果：通过。
   - 端口输出包含：
     - QQ OneBot WebSocket：`127.0.0.1:5004`
     - xiaomiao bridge：`127.0.0.1:5519`
     - xiaomiaoAgent API：`127.0.0.1:8900`
     - xiaomiaoAgent gateway：`127.0.0.1:8765`
     - Agent WebUI：`http://127.0.0.1:5174`
     - xiaomiaobot Web：`http://127.0.0.1:5175`

最终运行态验收：

1. 端口全部在线：
   - `5004`
   - `5519`
   - `8900`
   - `8765`
   - `5174`
   - `5175`

2. OneBot 登录态：
   - `get_login_info` 返回 `status=ok`。
   - 账号：`3994383071`。
   - 昵称：`小喵`。

3. Web 端同步：
   - bridge events 出现 `source=web`。
   - 测试消息：`Web三端同步测试，请只回复 ok`。
   - assistant 回复：`ok`。

4. Agent WebUI 同步：
   - bridge events 出现 `source=agent-webui`。
   - 测试消息：`Agent WebUI三端同步测试，请只回复 ok`。
   - assistant 回复：`ok`。

5. QQ 端真实入站同步：
   - bridge events 出现 `source=qq-private`。
   - QQ 入站消息：`你好小喵`。
   - assistant 回复：`你好呀！🐱 有什么需要我帮忙的吗？`。

6. xiaomiaoAgent 统一会话：
   - `xiaomiaoAgent/.nanobot/workspace/sessions/api_xiaomiao-unified.jsonl` 已记录 Web、Agent WebUI、QQ 三端消息。

需要保留：

1. 本次源码和测试变更。
2. `start-all.cmd`。
3. `xiaomiaoAgent/.nanobot/workspace/sessions/api_xiaomiao-unified.jsonl`，这是统一会话证据和运行缓存。
4. NapCat 账号配置和缓存，包含账号 `3994383071` 的本地登录相关配置。
5. `.understand-anything/knowledge-graph.json`，用于 Understand Anything dashboard。

可清理候选：

1. `xiaomiao/runtime/bridge_events.jsonl`
   - 这是本次运行态事件样本，已在本文档记录关键证据。
   - 删除后下次运行会重新生成。

2. `log/tmp/*`
   - 主要是 2026-06-02 的临时验证脚本、Playwright/Chrome 探针、stdout/stderr 日志和截图。
   - 当前不参与项目运行。

3. `log/*.log`
   - 主要是临时 xiaomiaoAgent serve/gateway/webui 运行日志。
   - 当前不参与项目运行。

清理注意：

1. 删除运行样本前，应保留本日志作为验收记录。
2. 不删除 NapCat 缓存，否则会破坏“登录一次本地带缓存”的目标。
3. 不删除 xiaomiaoAgent session，否则会丢失三端统一会话历史。
