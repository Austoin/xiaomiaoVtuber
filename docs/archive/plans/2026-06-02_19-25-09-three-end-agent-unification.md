---
mode: execution-plan
cwd: <项目根目录>
task: 三端对话同步、统一 config、QQ 接入 nanobot 全工具
complexity: complex
created_at: 2026-06-02_19-25-09
status: complete
---

# 计划：三端统一接入 nanobot Agent

## 目标

把 `AuBot stage-web`、`stage-tamagotchi` 桌面端、`xiaomiao` QQ 入口统一到
同一个 nanobot Agent 能力层，并把对话事件同步到可订阅的桥接事件流。

## 当前事实

1. QQ 普通聊天已调用 `generate_agent_reply(...)`，入口在 `xiaomiao/main.py`。
2. `generate_agent_reply(...)` 通过 `agent_backend.py` 调用 nanobot OpenAI-compatible API。
3. 现有桥接服务只保存每个用户最后一条 assistant 回复：`publish_desktop_state(...)`。
4. `stage-web` 只会发消息到桥接服务，不会轮询 QQ/桌面产生的消息。
5. nanobot API 使用 `session_id` 组成 `api:<session_id>`，默认统一会话是 `xiaomiao-unified`。
6. nanobot 具备 shell、文件、web 等工具配置，但 QQ 远程执行这些工具必须有显式权限边界。
7. 根目录 `.gitignore` 当前未忽略 `/config.json`，创建密钥配置前必须先补忽略规则。

## 分批执行

### 批次 1：桥接事件历史同步

业务文件不超过 3 个：

1. `xiaomiao/desktop_bridge.py`
   - 增加事件历史存储。
   - 新增 `GET /v1/xiaomiao/events?after=<id>&user_id=<id>`。
   - 保留 `/v1/xiaomiao/state` 兼容桌面端。
2. `test/xiaomiao/test_desktop_bridge.py`
   - 先写复现测试：QQ 发布后 `/events` 可读。
   - 覆盖 `after` 游标和 user/assistant 成对事件。
3. `xiaomiao/main.py`
   - QQ 群/私聊自然语言分支发布 user + assistant 事件。

函数级设计：

1. `desktop_bridge.py`
   - 新增 `BRIDGE_EVENTS` 与自增事件 ID。
   - 新增 `publish_bridge_event(...)`，参数包含 source/channel/chat_id/user_id/role/content。
   - 新增 `publish_bridge_exchange(...)`，一次写 user 与 assistant 两条事件。
   - 新增 `query_bridge_events(...)`，支持 `after` 与可选 `user_id`。
   - `publish_desktop_state(...)` 保留，继续兼容桌面端 `/state`。
   - `POST /v1/chat/completions` 成功后写入 web user+assistant exchange。
   - 新增 `GET /v1/xiaomiao/events`，返回 `events` 与 `last_id`。
2. `test_desktop_bridge.py`
   - 先加测试证明当前缺陷：QQ-style publish 后 `/events` 应该能读取。
   - 测试 web POST 写入两条事件。
   - 测试 `after` 游标只返回新事件。
3. `main.py`
   - `generate_desktop_reply(...)` 不再重复发布 state，避免 web POST 双写。
   - QQ 群和私聊成功发送后调用 `publish_bridge_exchange(...)`。
   - QQ 的 source 分别为 `qq-group`、`qq-private`，chat_id 分别为群号和用户号。

### 批次 2：stage-web 订阅桥接事件

业务文件不超过 3 个：

1. `AuBot/packages/stage-layouts/src/xiaomiao-bridge.ts`
   - 增加事件类型、事件拉取、去重合并 helper。
2. `AuBot/apps/stage-web/src/pages/index.vue`
   - 周期拉取 `/events`，把 QQ/桌面消息合并到当前聊天会话。
3. 必要时只改一个输入组件处理去重元数据。

### 批次 3：根目录统一配置

业务文件不超过 3 个：

1. `.gitignore`
   - 增加 `/config.json`，避免密钥入库。
2. `config.example.json`
   - 放安全占位结构，不放真实密钥。
3. `xiaomiao/unified_config.py` 或现有配置入口
   - 从根目录 `config.json` 读取 nanobot 与提供方覆盖项。

本批会创建本地 `config.json`，内容只用占位或空值，真实密钥由用户自行填入。

### 批次 4：QQ 使用 nanobot 全工具

业务文件不超过 3 个：

1. `xiaomiao/agent_backend.py`
   - 把 `user_id`、`channel`、`chat_id` 明确传入 Agent 请求上下文。
2. `xiaomiao/main.py`
   - 只允许 ROOT/owner/allowlist 用户从 QQ 触发高风险工具请求。
3. nanobot 配置文件或示例
   - 明确 shell、文件、web 工具启用方式。

权限边界默认建议：只有 `ROOT_User`/owner 可从 QQ 使用 shell、写文件、联网搜索等高风险工具。

### 批次 5：验证与日志

1. Python 单测，60 秒超时。
2. stage-web typecheck。
3. nanobot API 手动请求验证。
4. 桥接 `/events` 验证 web、QQ、桌面事件同步。
5. 安全验证：非 owner QQ 用户不能触发 shell/文件工具。
6. 写入 `log\tmp` 过程日志与 `log-docs` 总结日志。

## 待确认

1. QQ 高风险工具权限：用户确认普通 QQ 用户也可以使用。
2. 根目录 `config.json`：用户确认按本地 ignored secret config 处理。
3. 网页端事件范围：用户确认显示统一事件。

## 执行记录

### 2026-06-02 批次 1

状态：已完成。

改动：

1. `desktop_bridge.py` 新增桥接事件历史、`/v1/xiaomiao/events`、事件发布与查询辅助函数。
2. `main.py` 的 QQ 群/私聊自然语言回复成功后发布 user+assistant 事件。
3. `test_desktop_bridge.py` 新增事件同步测试，并抽出测试 helper 保持文件 300 行以内。

验证：

1. `conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_desktop_bridge.py"`：8 个测试通过。
2. `conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_*.py"`：22 个测试通过。

### 2026-06-02 批次 2

状态：已完成。

改动：

1. `xiaomiao-bridge.ts` 新增 `/v1/xiaomiao/events` 拉取、事件校验、事件转聊天消息和去重合并。
2. `index.vue` 启动桥接事件轮询，将 QQ/桌面事件合并进当前 stage-web 聊天会话。
3. `xiaomiao-bridge-events.test.ts` 覆盖事件拉取和非 web 事件去重合并。

验证：

1. `pnpm -C AuBot --filter @proj-airi/stage-ui test:run -- src/xiaomiao-bridge-events.test.ts`：2 个测试通过。
2. `pnpm -C AuBot --filter @proj-airi/stage-web typecheck`：通过。

### 2026-06-02 批次 3

状态：已完成。

改动：

1. `.gitignore` 增加 `/config.json`，根目录真实密钥配置不会进入 git。
2. `config.example.json` 提供统一配置示例。
3. 本地 `config.json` 已创建，内容为空占位，不包含真实密钥。
4. `unified_config.py` 新增根配置读取与非空覆盖合并。
5. `agent_backend.py` 的 `nanobot_agent` 配置支持由根目录 `config.json` 覆盖。

验证：

1. `git check-ignore -v config.json`：确认 `/config.json` 被忽略。
2. `conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_agent_backend.py"`：8 个测试通过。
3. `conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_*.py"`：24 个测试通过。

### 2026-06-02 批次 4

状态：代码侧已完成，运行联调待最终验证。

改动：

1. QQ 群普通聊天的 `Normal`、`Net` 分支改为调用 `generate_agent_reply(...)`。
2. QQ 私聊普通聊天的 `Normal`、`Net` 分支改为调用 `generate_agent_reply(...)`。
3. `main.py` 删除旧 `SearchOnline` 导入，避免普通聊天静默回退到旧提供方。
4. 按用户确认，不增加 ROOT/owner 限制；普通 QQ 用户也可通过 nanobot Agent 触发工具。

验证：

1. `conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_*.py"`：24 个测试通过。
2. `rg -n "SearchOnline" xiaomiao\main.py -S`：无结果。
3. `rg -n "generate_agent_reply\(" xiaomiao\main.py -S`：web、QQ 群 Pixmap/Normal/Net、QQ 私聊 Pixmap/Normal/Net 均存在 Agent 调用点。

### 2026-06-02 最终验证

状态：已完成。

验证：

1. Python：`test/xiaomiao` 24 个测试通过。
2. 前端：`stage-ui` 定向 Vitest 2 个测试通过。
3. 前端：`stage-web` typecheck 通过。
4. nanobot API：临时启动 `python -m nanobot serve --config ...` 后 `/v1/models` 返回 200。
5. nanobot exec：本地 API 请求返回 `XIAOMIAO_TOOL_OK`。
6. nanobot 文件工具：成功创建 `log\tmp\nanobot-created-20260602-195345.txt`，内容为 `XIAOMIAO_FILE_TOOL_OK`。
7. nanobot web：联网搜索工具请求返回 200，响应为 `WEB_DONE`。
8. 进程检查：临时 nanobot 进程均已停止。

### 2026-06-02 批次 5

状态：已完成。

改动：

1. `stage-tamagotchi` 主页面新增桥接 `/events` 轮询。
2. 桌面端聊天记录通过 `appendXiaomiaoBridgeEvents(..., { includeWeb: true })` 合并 web/QQ 事件。
3. 原 `/state` 轮询继续负责桌面表情、字幕和语音反应，不再重复写聊天记录。

验证：

1. `pnpm -C AuBot --filter @proj-airi/stage-tamagotchi typecheck`：通过。
2. 最终验证矩阵：Python 24 个测试通过，stage-ui 2 个测试通过，stage-web typecheck 通过，stage-tamagotchi typecheck 通过。
