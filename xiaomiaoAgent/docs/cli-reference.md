# 命令行参考

| 命令 | 说明 |
|---------|-------------|
| `xiaomiao onboard` | 在 `~/.nanobot/` 初始化配置和工作区 |
| `xiaomiao onboard --wizard` | 启动交互式初始化向导 |
| `xiaomiao onboard -c <config> -w <workspace>` | 初始化或刷新指定实例的配置和工作区 |
| `xiaomiao agent -m "..."` | 与 Agent 聊天 |
| `xiaomiao agent -w <workspace>` | 使用指定工作区聊天 |
| `xiaomiao agent -w <workspace> -c <config>` | 使用指定工作区和配置聊天 |
| `xiaomiao agent` | 交互式聊天模式 |
| `xiaomiao agent --no-markdown` | 显示纯文本回复 |
| `xiaomiao agent --logs` | 聊天时显示运行日志 |
| `xiaomiao serve` | 启动 OpenAI 兼容 API |
| `xiaomiao gateway` | 启动网关 |
| `xiaomiao status` | 显示状态 |
| `xiaomiao provider login openai-codex` | 为提供方执行 OAuth 登录 |
| `xiaomiao channels login <channel>` | 以交互方式认证一个通道 |
| `xiaomiao channels status` | 显示通道状态 |

交互模式的退出方式：`exit`、`quit`、`/exit`、`/quit`、`:q` 或 `Ctrl+D`。

旧 `nanobot` 命令入口仍保留兼容；用户文档统一展示 `xiaomiao`。
