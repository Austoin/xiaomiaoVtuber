# CLI 参考

| 命令 | 说明 |
|---------|-------------|
| `nanobot onboard` | 在 `~/.nanobot/` 初始化配置和工作区 |
| `nanobot onboard --wizard` | 启动交互式初始化向导 |
| `nanobot onboard -c <config> -w <workspace>` | 初始化或刷新指定实例的配置和工作区 |
| `nanobot agent -m "..."` | 与 Agent 聊天 |
| `nanobot agent -w <workspace>` | 使用指定工作区聊天 |
| `nanobot agent -w <workspace> -c <config>` | 使用指定工作区和配置聊天 |
| `nanobot agent` | 交互式聊天模式 |
| `nanobot agent --no-markdown` | 显示纯文本回复 |
| `nanobot agent --logs` | 聊天时显示运行日志 |
| `nanobot serve` | 启动 OpenAI 兼容 API |
| `nanobot gateway` | 启动 gateway |
| `nanobot status` | 显示状态 |
| `nanobot provider login openai-codex` | 为 Provider 执行 OAuth 登录 |
| `nanobot channels login <channel>` | 以交互方式认证一个通道 |
| `nanobot channels status` | 显示通道状态 |

交互模式的退出方式：`exit`、`quit`、`/exit`、`/quit`、`:q` 或 `Ctrl+D`。
