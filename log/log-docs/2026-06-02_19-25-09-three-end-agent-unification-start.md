时间：2026-06-02_19-25-09
任务：三端对话同步、统一 config、QQ 接入 nanobot 全工具
状态：已完成只读核对，等待用户批准实施计划

已核对事实：

1. `xiaomiao/main.py` 的 QQ 群/私聊自然语言分支已调用 nanobot Agent backend。
2. `xiaomiao/desktop_bridge.py` 当前只保存最新 assistant state，不保存完整对话历史。
3. `AuBot stage-web` 当前只发送消息到 bridge，不订阅 QQ 产生的事件。
4. `stage-tamagotchi` 已轮询 `/v1/xiaomiao/state`，但该接口也只有最后一条回复。
5. nanobot API 支持 `session_id`，默认可形成统一 Agent session。
6. 根目录 `.gitignore` 未忽略 `/config.json`，写入密钥配置前需要先补规则。

下一步：

等待用户确认计划和权限边界后，从 Batch 1 开始实施。

基线验证：

1. 当前 HEAD：`6a8abaeda1a427f1884de80c03a9d4b0b7927c3c`。
2. `python -m unittest discover -s test/xiaomiao -p "test_*.py"`：20 个测试通过。
3. `pnpm -C AuBot --filter @proj-airi/stage-web typecheck`：通过。
4. 当前未跟踪文件：新计划文件与根目录 `log-docs` 总结日志目录。

Batch 1 函数级设计：

1. `desktop_bridge.py` 增加事件历史、事件发布、事件查询 helper。
2. 保留 `/v1/xiaomiao/state`，新增 `/v1/xiaomiao/events`。
3. web POST 成功写入 user+assistant 事件。
4. QQ 群/私聊自然语言分支成功发送后写入 user+assistant 事件。
5. `generate_desktop_reply(...)` 不直接发布 state，避免与 bridge POST 路由重复发布。

用户确认：

1. QQ 普通用户也可以使用 Agent 全部工具。
2. 根目录 `config.json` 按 ignored 本地密钥文件处理。
3. 网页端显示统一事件。

Batch 1 结果：

1. 已实现 bridge 事件历史与 `/v1/xiaomiao/events`。
2. 已让 web POST 与 QQ 群/私聊回复写入 user+assistant 事件。
3. `test_desktop_bridge.py` 行数为 267，低于 300 行限制。
4. bridge 专项测试：8 个通过。
5. xiaomiao 全量单测：22 个通过。

Batch 2 结果：

1. `xiaomiao-bridge.ts` 增加事件拉取、校验、去重合并。
2. `stage-web/src/pages/index.vue` 增加 bridge 事件轮询。
3. web 自己产生的 bridge 事件推进游标但不重复显示。
4. QQ 群/私聊事件以来源前缀显示到聊天记录。
5. stage-ui 定向 Vitest：2 个通过。
6. stage-web typecheck：通过。

Batch 3 结果：

1. `.gitignore` 已加入 `/config.json`。
2. 根目录 `config.example.json` 已创建。
3. 根目录本地 `config.json` 已创建且被 git 忽略。
4. `unified_config.py` 支持读取根配置并用非空值覆盖本地配置。
5. `agent_backend.py` 已接入根目录 `nanobot_agent` 配置。
6. agent backend 单测：8 个通过。
7. xiaomiao 全量单测：24 个通过。

Batch 4 结果：

1. QQ 群普通聊天 `Normal`、`Net` 分支改走 nanobot Agent。
2. QQ 私聊普通聊天 `Normal`、`Net` 分支改走 nanobot Agent。
3. `main.py` 已删除旧 `SearchOnline` 导入。
4. 用户确认普通 QQ 用户可使用 Agent 全部工具，因此未增加 owner-only guard。
5. xiaomiao 全量单测：24 个通过。

最终验证：

1. Python 全量单测：24 个通过。
2. stage-ui 定向 Vitest：2 个通过。
3. stage-web typecheck：通过。
4. nanobot serve 临时启动成功，`/v1/models` 返回 200。
5. exec 工具请求返回 `XIAOMIAO_TOOL_OK`。
6. 文件工具创建 `log\tmp\nanobot-created-20260602-195345.txt`，内容为 `XIAOMIAO_FILE_TOOL_OK`。
7. web_search 请求返回 200，响应为 `WEB_DONE`。
8. 临时 nanobot 进程已停止，无残留。

Batch 5 结果：

1. stage-tamagotchi 新增 `/v1/xiaomiao/events` 轮询。
2. 桌面端聊天记录现在合并 web/QQ bridge events。
3. `/state` 轮询继续用于字幕/语音反应，避免重复写聊天记录。
4. stage-tamagotchi typecheck：通过。
5. 最终验证矩阵全部通过。
