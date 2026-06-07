# 测试与质量说明

本文说明项目内测试目录的职责。实际运行命令和当前预期结果见 [verification.md](verification.md)。

## 测试分区

| 范围 | 位置 | 主要覆盖 |
|------|------|----------|
| 项目根 Python 测试 | `test/xiaomiao/` | QQ 机器人权限、Agent 调用、桥接服务、文件工作区、人格配置和控制台输出 |
| xiaomiaoAgent Python 测试 | `xiaomiaoAgent/tests/` | Agent Loop、API、Channels、工具、记忆、会话、配置、Cron、Provider、MCP 和安全边界 |
| xiaomiaobot 前端/服务测试 | `xiaomiaobot/**/?(*.)test.ts` | stage UI、桥接事件、桌面端、移动端、插件 SDK、Computer Use、Minecraft、server-runtime 和共享包 |

## 根目录 `test/xiaomiao`

| 文件 | 重点 |
|------|------|
| `test_agent_backend.py` | QQ 普通 AI 回复调用 xiaomiaoAgent API、错误显式暴露 |
| `test_qq_permissions.py` | ROOT、Super、白名单、普通用户权限判断 |
| `test_qq_agent_tools.py` | 高风险确认码、过期、用户/群绑定和命令摘要 |
| `test_qq_agent_bridge.py` | QQ 请求元数据、工具事件和桥接事件写入 |
| `test_qq_workspace.py` | QQ 文件下载、扩展名、大小、URL 和 workspace 边界 |
| `test_desktop_bridge.py` | 本机 bridge HTTP 接口、聊天、状态和事件 |
| `test_desktop_bridge_persistence.py` | bridge event 持久化和历史读取 |
| `test_personas.py` | 人设模式和提示词配置 |
| `test_mossia_api.py` | 本地 API 分支和兼容逻辑 |
| `test_console_output.py` | 控制台输出格式 |

`__pycache__/` 属于运行缓存，不应提交。

## xiaomiaoAgent 测试目录

| 目录 | 重点 |
|------|------|
| `tests/agent/` | Agent 主循环、记忆、Dream、Session、Subagent、Hook、上下文压缩 |
| `tests/agent/tools/` | 自工具和 Subagent 工具 |
| `tests/channels/` | QQ、WebSocket、Telegram、Slack、飞书、企业微信、邮件等通道 |
| `tests/cli/` | 命令行交互、重启、历史文件和输入处理 |
| `tests/command/` | 内置命令和路由 |
| `tests/config/` | 配置路径、环境变量、统一根配置和迁移 |
| `tests/cron/` | 定时任务持久化、服务和工具 schema |
| `tests/heartbeat/` | 心跳投递和上下文桥接 |
| `tests/providers/` | OpenAI 兼容、Anthropic、Azure、Bedrock、Mistral、自定义 Provider 等 |
| `tests/security/` | 网络和安全边界 |
| `tests/session/` | 会话落盘一致性 |
| `tests/tools/` | 文件、编辑、Shell、Web、MCP、MarkItDown、Scrapling、stage 和服务工具 |

和 QQ 能力集成最相关的是 `tests/test_openai_api.py`、`tests/tools/test_tool_registry.py`、`tests/tools/test_tool_loader.py`、`tests/tools/test_markitdown_tool.py`、`tests/tools/test_scrapling_tool.py`、`tests/tools/test_xiaomiao_stage_tool.py` 和 `tests/tools/test_xiaomiaobot_services_tool.py`。

## xiaomiaobot 测试分布

`xiaomiaobot` 是 pnpm monorepo，测试分散在 `apps/`、`packages/`、`services/` 和 `plugins/` 下，统一由 Vitest 运行。

和小喵三端联动最相关的测试：

| 文件 | 重点 |
|------|------|
| `apps/stage-pocket/src/modules/xiaomiao-bridge-events.test.ts` | 移动端只读同步桥接事件 |
| `packages/stage-ui/src/xiaomiao-bridge-events.test.ts` | stage UI 渲染 chat/tool/confirmation/memory/stage 事件 |
| `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.test.ts` | 桌面端读取 bridge 状态和聊天 |
| `apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.test.ts` | 桌面端消费字幕、TTS、表情、背景和模型动作 |

其它测试覆盖：

- `packages/stage-ui/`：聊天、Provider、TTS、视觉、工具执行、场景组件。
- `apps/stage-tamagotchi/`：桌面窗口、HTTP server、插件挂载、桥接、字幕和窗口生命周期。
- `apps/stage-pocket/`：移动端桥接事件和平台适配。
- `services/computer-use-mcp/`：本机窗口、终端、浏览器、工作流和 MCP 工具注册。
- `services/minecraft/`：状态、动作、认知规划和 debug MCP。
- `services/twitter-services/`：命令解析和服务逻辑。
- `packages/plugin-sdk*`：插件宿主、权限、资源、依赖和 session。

## 质量检查规则

- 只改文档时，至少运行 `git diff --check`。
- 改启动脚本时，运行 `setup-env.cmd --check` 和 `start-all.cmd --check`。
- 改 QQ 权限、文件、桥接或 Agent 调用时，运行 `test/xiaomiao`。
- 改 xiaomiaoAgent API、工具或 MCP 时，运行相关 pytest。
- 改 stage bridge 或三端事件时，运行指定 Vitest bridge 测试。
- 跨子系统改动时，按 [verification.md](verification.md) 的最小完整矩阵验收。
