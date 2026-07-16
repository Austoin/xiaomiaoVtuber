---
title: Minecraft
description: Run and contribute to the Minecraft game companion
---

### Minecraft agent

The Minecraft service uses Mineflayer for movement, combat, collection, crafting,
perception, and player interaction. Natural-language planning is handled only by
the shared `xiaomiaoAgent` runtime.

Start `xiaomiaoAgent` on port `8900` and a reachable Minecraft server first. From
the `xiaomiaobot` workspace, configure the service environment:

```shell
BOT_HOSTNAME=127.0.0.1
BOT_PORT=25565
BOT_USERNAME=xiaomiao
BOT_AUTH=offline
XIAOMIAO_AGENT_API_URL=http://127.0.0.1:8900/v1/chat/completions
XIAOMIAO_AGENT_SESSION_ID=minecraft-runtime
```

You may place these values in `services/minecraft/.env.local`, or export them in
your shell. Then run:

```shell
pnpm --filter @proj-airi/minecraft-bot start
```

Set `ENABLE_MCP_SERVER=true`, `ENABLE_DEBUG_SERVER=true`, or
`ENABLE_MINECRAFT_VIEWER=true` when the corresponding debugging surface is
needed. Stage Web, Pocket, and Desktop observe this service through the shared
server event channel and inject fresh game context into the next agent turn.
