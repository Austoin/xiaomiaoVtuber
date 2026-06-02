---
mode: plan
cwd: F:\xiaomiaoVirtual
task: 打通 xiaomiao 到 AuBot stage-web 并融合 nanobot Agent 能力
complexity: complex
tool: local-code-inspection
total_thoughts: 8
created_at: 2026-06-02T15:49:30+08:00
status: implemented-runtime-verified
---

# Plan: xiaomiao web nanobot fusion

## 任务概述

目标是把当前已经打通到 `AuBot/apps/stage-tamagotchi` 的小喵本地桥接能力，
扩展到 `AuBot/apps/stage-web`，并让 `xiaomiao` 能使用 `nanobot` 的 Agent 能力。

当前仓库已经存在三块基础能力：

1. `xiaomiao` 通过 `desktop_bridge.py` 暴露本地 OpenAI 兼容接口。
2. `stage-tamagotchi` 已能消费小喵桥接，驱动字幕、聊天历史、TTS 和口型同步。
3. `nanobot` 已有 `AgentLoop`、工具系统、记忆、API server 和 OpenAI 兼容入口。

## 当前证据

- `README.md:3`：项目定位为 QQ 机器人、Vtuber 桌面角色与轻量 Agent 框架融合项目。
- `README.md:11`：当前已打通 `xiaomiao` 与 `AuBot` Electron 桌面端本地 HTTP 桥接。
- `xiaomiao/main.py:226`：启动 `127.0.0.1:5519` 桌面桥接服务。
- `xiaomiao/desktop_bridge.py:67`：创建本地 HTTP bridge，提供模型、状态和聊天接口。
- `AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.ts:52`：读取小喵桥接状态。
- `AuBot/apps/stage-tamagotchi/src/renderer/stores/chat-sync.ts:285`：桌面聊天输入优先走小喵 bridge。
- `AuBot/apps/stage-web/src/App.vue:84`：web 端初始化全局 stores。
- `AuBot/apps/stage-web/src/pages/index.vue:45`：web 端已有舞台、音频、VAD 和聊天输入流水线。
- `nanobot/nanobot/api/server.py:194`：OpenAI 兼容 API 处理 `/v1/chat/completions`。
- `nanobot/nanobot/agent/loop.py:1669`：`process_direct()` 是 nanobot Agent 的直接处理入口。

## 分阶段实施计划

### Phase 1: 让 AuBot stage-web 消费小喵 bridge

范围控制在最多 3 个文件：

1. 在 `stage-web` 增加小喵 bridge client 或复用 Electron 端桥接逻辑。
2. 在 `stage-web/src/pages/index.vue` 中把语音/文本 ingest 优先转到 `xiaomiao` bridge。
3. 保持 bridge 不可用时显式失败或走现有 provider 路径，具体行为实现前再按当前代码测试决定。

验收标准：

- `stage-web` 能向 `http://127.0.0.1:5519/v1/chat/completions` 发送用户文本。
- 成功后 user/assistant 消息进入当前 chat session。
- 页面舞台仍能正常渲染，音频/VAD 初始化不被破坏。
- 运行 `pnpm -C AuBot --filter @proj-airi/stage-web typecheck`。

### Phase 2: 让 xiaomiao bridge 可选接入 nanobot Agent

范围控制在最多 3 个文件：

1. 在 `xiaomiao` 增加可配置的 Agent backend。
2. 默认保持现有回复逻辑，启用配置后转发到 `nanobot` OpenAI 兼容 API。
3. 为桥接转发写测试，覆盖成功、HTTP 错误和响应缺失。

推荐优先使用 HTTP 转发到 `nanobot serve`，而不是直接导入 `AgentLoop`。
原因是边界清晰、依赖隔离，且 `nanobot` 已有 `/v1/chat/completions` API。

验收标准：

- `xiaomiao` bridge 可以调用 `nanobot` API 获得 Agent 回复。
- 默认配置下原有 QQ Bot 回复不被破坏。
- 运行 `conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_*.py"`。

### Phase 3: 联调闭环

启动顺序：

1. 启动 `nanobot serve`，默认端口按文档为 `127.0.0.1:8900`。
2. 启动 `xiaomiao`，确认 bridge 状态接口 `127.0.0.1:5519/v1/xiaomiao/status`。
3. 启动 `stage-web`，在网页端发送文本或语音。

验收标准：

- `stage-web` 输入文本后，链路经过 `xiaomiao` bridge。
- 配置启用时，`xiaomiao` bridge 回复来自 `nanobot Agent`。
- 回复进入 web 聊天历史，并驱动 Vtuber 表现层。

## 预期任务拆分

本任务会拆成小步执行，每步不超过 3 个业务文件：

1. `stage-web` bridge 接入与类型检查。
2. `xiaomiao` bridge Agent backend 与单元测试。
3. 联调脚本或启动验证说明，仅在必要时追加。

## 测试计划

- Python bridge 单测：`test/xiaomiao/test_desktop_bridge.py`。
- nanobot API 测试参考：`nanobot/tests/test_openai_api.py`。
- AuBot web 静态验证：`pnpm -C AuBot --filter @proj-airi/stage-web typecheck`。
- 必要时补充前端纯函数测试；当前 `stage-web` package 暂无 test script。

## 风险与注意事项

- `stage-web` 目前没有像 Electron 端一样的小喵桥接集成。
- Electron 端桥接用户 ID 仍有硬编码，多用户映射后续需要单独解决。
- `nanobot` 工具能力不能直接暴露给任意 QQ 用户或公网入口。
- `xiaomiao` 和 `nanobot` 同时维护上下文时，可能出现 session 状态分裂。
- 网络、API Key、模型 provider 失败必须显式暴露，不做静默假成功。

## 确认点

已确认进入实现。当前执行小批次：

1. 第一批：计划状态、stage-web bridge helper、桌面 ChatArea 文本入口。已完成并通过 typecheck。
2. 第二批：移动端文本入口与页面级录音入口。已完成并通过 typecheck。
3. 第三批：xiaomiao Agent backend 与单元测试。已完成并通过 unittest。
4. 第四批：desktop bridge HTTP 502 显式错误、QQ 群/私聊自然语言回复统一到 Agent backend。已完成并通过 unittest 与 py_compile。

已完成验证：

- `pnpm -C AuBot --filter @proj-airi/stage-web build`
- `pnpm -C AuBot --filter @proj-airi/stage-web typecheck`
- `conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_*.py"`
- `conda run -n xiaomiao python -m py_compile xiaomiao/main.py xiaomiao/agent_backend.py xiaomiao/desktop_bridge.py`
- 运行时闭环：`xiaomiao bridge -> nanobot Agent -> bridge state` 返回 200，回复内容为 `小喵网页接入测试成功`。
- 浏览器闭环：Chrome 打开 `stage-web`，真实输入文本并按 Enter 后，请求 `127.0.0.1:5519/v1/chat/completions` 返回 200，页面出现 `小喵网页浏览器接入成功`。

日志：

- `log/2026-06-02-nanobot-agent-fusion.md`

运行时验证结论：

- `nanobot /health` 返回 200。
- `nanobot /v1/models` 返回 `deepseek-chat`。
- `xiaomiao bridge /v1/xiaomiao/status` 返回 200。
- `xiaomiao bridge /v1/chat/completions` 调用 nanobot Agent 成功。
- `xiaomiao bridge /v1/xiaomiao/state` 写入同一回复状态。
- `stage-web` 浏览器输入链路真实触发 `xiaomiao bridge`，并把 nanobot 回复写入页面聊天历史。
