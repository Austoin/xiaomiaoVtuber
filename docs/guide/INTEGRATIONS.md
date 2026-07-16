# 外部通道与服务

所有集成都以 `xiaomiaoAgent` 为唯一推理、记忆和工具层。Discord、Telegram、Minecraft、Twitter 和 WebUI 不保存独立模型配置，也不直接调用聊天 Provider。

## WebUI

```powershell
pnpm run agent:webui
```

浏览器地址为 `http://127.0.0.1:8765`，Gateway 健康检查为 `http://127.0.0.1:18790/health`。命令会在运行时启用 WebSocket 通道，并保留 `config.json` 中已有的 token 与 `allowFrom` 设置。

## Discord

1. 安装可选依赖：`cd xiaomiaoAgent; uv sync --extra discord`。
2. 在根 `config.json` 的 `xiaomiaoAgent.channels.discord` 中填写 Bot token，将 `enabled` 设为 `true`。
3. 运行 `pnpm run agent:gateway`。

`allowFrom` 为空时不接受用户消息；填写允许访问的 Discord 用户 ID，或按私有部署策略使用 `"*"`。

## Telegram

在 `xiaomiaoAgent.channels.telegram` 中填写 BotFather token、启用通道并配置 `allowFrom`，然后运行：

```powershell
pnpm run agent:gateway
```

Discord 与 Telegram 可以同时启用，共享同一 Agent。是否共享同一会话由 `xiaomiaoAgent.agents.defaults.unifiedSession` 控制。

## Minecraft

Minecraft 服务使用 Mineflayer 连接游戏服务器，所有自然语言规划请求发送到 `XIAOMIAO_AGENT_API_URL`。

```powershell
pnpm run agent:api
$env:BOT_HOSTNAME="127.0.0.1"
$env:BOT_PORT="25565"
$env:BOT_USERNAME="xiaomiao"
$env:BOT_AUTH="offline"
$env:XIAOMIAO_AGENT_API_URL="http://127.0.0.1:8900/v1/chat/completions"
$env:XIAOMIAO_AGENT_SESSION_ID="minecraft-runtime"
pnpm run bot:minecraft
```

服务上线后，可在 Web、Pocket 或 Desktop 的“设置 -> 模块 -> Minecraft”查看连接状态、最新 Bot 上下文和最近 50 条服务事件。Minecraft 上下文会作为旁路状态注入下一轮对话，实际推理仍只经过 `xiaomiaoAgent`。

需要 Minecraft 调试 MCP 时设置 `$env:ENABLE_MCP_SERVER="true"`。服务地址为 `http://127.0.0.1:3001/sse`，根配置中的 `tools.minecraftMcp` 可按 `config.example.json` 启用。真实验证需要可连接的 Minecraft Server 和对应账号。

## Twitter

Twitter 服务通过 Playwright 操作 X/Twitter，并以 MCP 暴露时间线、搜索、发帖和用户资料工具。它本身不调用模型。

```powershell
$env:BROWSER_HEADLESS="false"
$env:MCP_PORT="8080"
pnpm run bot:twitter
```

首次运行需要在浏览器中完成登录，登录状态写入服务本地 `data/twitter-session.json`。MCP SSE 地址为 `http://127.0.0.1:8080/sse`；在 `xiaomiaoAgent.tools.twitterMcp` 启用后重启 Agent Gateway/API。真实发帖和读取验证需要有效 Twitter 登录状态。

## 安全边界

- 不要提交 Bot token、Twitter 会话文件、Minecraft 密码或 Provider API Key。
- 只在可信网络暴露 WebUI、MCP 和 Gateway 端口。
- 外部服务连接失败时会显式报错，不会切换到另一套模型或伪造成功。
