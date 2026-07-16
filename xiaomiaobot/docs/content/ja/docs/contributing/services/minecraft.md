---
title: Minecraft
description: Minecraft ゲームコンパニオンの実行と開発
---

### Minecraft エージェント

Minecraft サービスは Mineflayer を使用し、移動、戦闘、採集、クラフト、
知覚、プレイヤーとの対話を提供します。自然言語の計画は共有の
`xiaomiaoAgent` のみが処理します。

先にポート `8900` の `xiaomiaoAgent` と接続可能な Minecraft サーバーを
起動します。`xiaomiaobot` ワークスペースで次の環境変数を設定します。

```shell
BOT_HOSTNAME=127.0.0.1
BOT_PORT=25565
BOT_USERNAME=xiaomiao
BOT_AUTH=offline
XIAOMIAO_AGENT_API_URL=http://127.0.0.1:8900/v1/chat/completions
XIAOMIAO_AGENT_SESSION_ID=minecraft-runtime
```

値は `services/minecraft/.env.local` に保存するか、シェルで設定できます。
その後、次を実行します。

```shell
pnpm --filter @proj-airi/minecraft-bot start
```

必要に応じて `ENABLE_MCP_SERVER=true`、`ENABLE_DEBUG_SERVER=true`、
`ENABLE_MINECRAFT_VIEWER=true` を設定します。Stage Web、Pocket、Desktop は
共有サーバーイベントを通じて状態を監視し、最新のゲーム情報を次の
エージェントターンへ渡します。
