# 外部集成恢复记录（2026-07-16）

## 目标

恢复 Discord、Telegram、Minecraft、Twitter 和 xiaomiaoAgent WebUI，同时保持 `xiaomiaoAgent` 是唯一模型推理、会话、记忆和工具执行层。

## 恢复来源与处理

- Discord、Telegram：使用 `xiaomiaoAgent/nanobot/channels/` 的原生通道，没有恢复旧 Node 独立 Agent 服务。
- Minecraft：从当前 Git 基线恢复 Mineflayer 服务，将原模型调用改为 `POST http://127.0.0.1:8900/v1/chat/completions`；请求不再携带 Provider API Key 或模型名。
- Twitter：从当前 Git 基线恢复 Playwright MCP 服务。该服务只提供浏览器工具，不运行模型。
- WebUI：从删除提交 `2219115fa1c14abded33a891181cf601812fb70a` 的父提交恢复，构建后嵌入 `xiaomiaoAgent/nanobot/web/dist/`。
- Stage UI：删除残留的客户端 `generateText("ping")` 校验；Provider Health 只执行 `GET /models` 连接检查。

## 入口

| 功能 | 命令 | 地址或依赖 |
| --- | --- | --- |
| WebUI | `pnpm run agent:webui` | `http://127.0.0.1:8765` |
| Discord、Telegram | `pnpm run agent:gateway` | 根配置启用通道并填写 token |
| Minecraft | `pnpm run bot:minecraft` | Agent API `:8900`、Minecraft Server |
| Twitter | `pnpm run bot:twitter` | MCP `http://127.0.0.1:8080/sse` |

## 验证结果

- WebUI：12 个文件、82 个测试通过；生产构建和 Python wheel/sdist 打包通过。
- WebUI 实际启动：Gateway `:18790`、WebSocket/WebUI `:8765` 正常；bootstrap、SPA 回退和 WebSocket 建连通过。
- WebUI 真实聊天：新会话返回 `WEBUI_RESTORE_OK_20260716`；桌面 1440x900、移动 390x844 无横向溢出或控制重叠。
- Agent：agent shards、channels、CLI、config、cron、heartbeat、session、providers、security、tools、utils 和根 API 测试均通过；channels 为 620 passed、3 skipped。
- QQ：66 passed。
- Minecraft：19 个文件、166 个测试通过；typecheck 通过。
- Twitter：14 个测试通过；typecheck 通过。
- xiaomiaobot workspace：113 个测试文件、708 个测试通过，2 skipped；46 个项目 typecheck 通过。
- Stage Web、Stage Pocket、Stage Tamagotchi/Electron 构建通过。
- Python `uv build` 通过，wheel 与 sdist 均包含 `nanobot/web/dist/index.html`。
- `git diff --check` 通过。

Ruff 全仓扫描仍报告 239 个历史基线问题，主要是旧文件的导入顺序、E402 和测试命名；本次没有用自动修复扩大改动范围。CLI 自身的 E402 来自既有 Windows UTF-8 初始化顺序。

## 外部验证限制

- Discord 和 Telegram 需要真实 Bot token 与用户白名单，未发送线上消息。
- Minecraft 需要可连接的服务器和账号，未执行真实进服动作。
- Twitter 需要有效登录会话，未读取或发布真实推文。

以上限制不影响本地单元测试、类型检查和服务构建；部署时应按 [集成指南](guide/INTEGRATIONS.md) 完成凭据验证。

## Git 记录

- `f3ab52a refactor(core): unify clients on xiaomiaoAgent`
- `db45d47 feat(integrations): restore external services`
- `38961ca feat(webui): restore embedded agent interface`
- 文档更新由包含本文件的后续 `docs` 提交记录。
