---
title: Minecraft
description: 启动和开发 Minecraft 游戏陪伴服务
---

### Minecraft 智能体

Minecraft 服务通过 Mineflayer 提供移动、战斗、采集、合成、感知和玩家互动。
所有自然语言规划只由共享的 `xiaomiaoAgent` 处理。

先启动监听 `8900` 端口的 `xiaomiaoAgent` 和可连接的 Minecraft 服务器，然后在
`xiaomiaobot` 工作区配置以下环境变量：

```shell
BOT_HOSTNAME=127.0.0.1
BOT_PORT=25565
BOT_USERNAME=xiaomiao
BOT_AUTH=offline
XIAOMIAO_AGENT_API_URL=http://127.0.0.1:8900/v1/chat/completions
XIAOMIAO_AGENT_SESSION_ID=minecraft-runtime
```

这些值可以写入 `services/minecraft/.env.local`，也可以在当前终端设置。随后运行：

```shell
pnpm --filter @proj-airi/minecraft-bot start
```

需要调试时可分别设置 `ENABLE_MCP_SERVER=true`、`ENABLE_DEBUG_SERVER=true` 或
`ENABLE_MINECRAFT_VIEWER=true`。Stage Web、Pocket 和 Desktop 通过共享服务事件
观察 Minecraft 状态，并将最新游戏上下文注入下一轮智能体对话。
