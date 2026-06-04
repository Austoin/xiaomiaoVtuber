# 三端统一互通实施日志

## 当前状态

已生成实施计划，尚未修改业务代码。

## 基线验证

1. Python 单测：`test/xiaomiao` 现有 20 个测试通过。
2. stage-web typecheck：通过。
3. 当前业务代码尚未修改，后续每批修改都以该基线对照。

## 核心结论

QQ 目前已经能把普通聊天请求送进 nanobot Agent，但同步只停留在“最后一条回复状态”。
网页端没有订阅 QQ 消息事件，所以 QQ 聊天不会显示到网页端。

要做到完全互通，需要先把 bridge 从 `latest state` 升级为 `event history`，
再让 web/desktop/QQ 都读写同一条事件流，并继续使用同一个 nanobot `session_id`。

## Batch 1 准备

已收敛到 3 个业务文件：

1. `desktop_bridge.py`：事件历史与 `/events` endpoint。
2. `test_desktop_bridge.py`：先测缺陷，再测事件写入与游标。
3. `main.py`：QQ 群/私聊发布 user+assistant 事件。

## Batch 1 结果

已完成 bridge 事件历史同步：

1. web POST 成功后写入 web user+assistant 事件。
2. QQ 群/私聊自然语言回复成功后写入 QQ user+assistant 事件。
3. `/v1/xiaomiao/state` 保持兼容，`/v1/xiaomiao/events` 用于后续网页端同步。
4. Python 单测 22 个通过。

## Batch 2 结果

已完成 stage-web 事件订阅：

1. stage-web 启动后轮询 bridge `/v1/xiaomiao/events`。
2. QQ 群/私聊事件会合并进当前网页聊天记录。
3. web 本地发送的消息继续即时显示，同时不会因轮询重复显示。
4. 前端新增事件 helper 测试 2 个通过，stage-web typecheck 通过。

## Batch 3 结果

已完成根目录统一配置基础：

1. 根目录 `config.json` 已创建为本地 ignored 文件。
2. `config.example.json` 提供可提交的安全占位结构。
3. xiaomiao 的 nanobot agent backend 会读取根目录 `nanobot_agent` 配置。
4. 空字符串和 null 占位不会覆盖已有有效本地配置。
5. xiaomiao 单测 24 个通过。

## Batch 4 结果

已完成 QQ 普通聊天统一到 nanobot Agent：

1. QQ 群聊和私聊的普通自然语言回复不再回退旧 `SearchOnline`。
2. 三种模式名 `Pixmap`、`Normal`、`Net` 都进入 `generate_agent_reply()`。
3. 普通 QQ 用户可通过 nanobot Agent 使用已启用的工具能力。
4. 代码侧验证通过，真实工具执行还需要最终联调验证。

## 最终验证

已完成验证：

1. xiaomiao Python 单测 24 个通过。
2. stage-ui 事件 helper 测试 2 个通过。
3. stage-web typecheck 通过。
4. nanobot API 临时启动成功，`/v1/models` 返回 200。
5. nanobot exec 工具验证返回 `XIAOMIAO_TOOL_OK`。
6. nanobot 文件工具创建了验证文件，内容正确。
7. nanobot web_search 请求返回 200。
8. 临时 nanobot 进程均已停止。
9. stage-tamagotchi typecheck 通过。

## 当前结论

三端统一链路已落地：

1. web 输入进入 xiaomiao bridge，再进入 nanobot Agent。
2. QQ 群/私聊普通聊天进入同一个 nanobot Agent session。
3. bridge 维护完整事件流，stage-web 轮询事件流同步 QQ 消息。
4. stage-tamagotchi 轮询同一事件流，将 web/QQ 事件合并进桌面聊天记录。
5. 根目录 `config.json` 已作为本地 ignored 配置源接入 xiaomiao nanobot backend。

## 待用户确认

1. QQ 高风险工具权限边界。
2. 根目录 `config.json` 本地 ignored 方案。
3. 网页端 QQ 消息展示范围。
