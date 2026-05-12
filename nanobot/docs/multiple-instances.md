# 多实例

你可以同时运行多个 nanobot 实例，并为它们使用独立配置和运行时数据。主要入口是 `--config`。如果你想为某个实例初始化或更新已保存的工作区，也可以在 `onboard` 时传入 `--workspace`。

## 快速开始

如果你希望每个实例从一开始就拥有自己的专用工作区，请在初始化时同时传入 `--config` 和 `--workspace`。

**初始化实例：**

```bash
# 创建独立实例配置和工作区
nanobot onboard --config ~/.nanobot-telegram/config.json --workspace ~/.nanobot-telegram/workspace
nanobot onboard --config ~/.nanobot-discord/config.json --workspace ~/.nanobot-discord/workspace
nanobot onboard --config ~/.nanobot-feishu/config.json --workspace ~/.nanobot-feishu/workspace
```

**配置每个实例：**

编辑 `~/.nanobot-telegram/config.json`、`~/.nanobot-discord/config.json` 等文件，为它们设置不同的通道配置。你在 `onboard` 时传入的工作区会保存到每个配置中，作为该实例的默认工作区。

**运行实例：**

```bash
# 实例 A - Telegram bot
nanobot gateway --config ~/.nanobot-telegram/config.json

# 实例 B - Discord bot
nanobot gateway --config ~/.nanobot-discord/config.json

# 实例 C - 使用自定义端口的飞书 bot
nanobot gateway --config ~/.nanobot-feishu/config.json --port 18792
```

## 路径解析

使用 `--config` 时，nanobot 会根据配置文件位置推导运行时数据目录。工作区仍来自 `agents.defaults.workspace`，除非你用 `--workspace` 覆盖它。

如果要在本地打开指向某个实例的 CLI 会话：

```bash
nanobot agent -c ~/.nanobot-telegram/config.json -m "Hello from Telegram instance"
nanobot agent -c ~/.nanobot-discord/config.json -m "Hello from Discord instance"

# 可选的一次性工作区覆盖
nanobot agent -c ~/.nanobot-telegram/config.json -w /tmp/nanobot-telegram-test
```

> `nanobot agent` 会使用所选工作区和配置启动本地 CLI agent。它不会附加到已经运行的 `nanobot gateway` 进程，也不会通过该进程代理。

| 组件 | 解析来源 | 示例 |
|-----------|---------------|---------|
| **Config** | `--config` 路径 | `~/.nanobot-A/config.json` |
| **Workspace** | `--workspace` 或配置 | `~/.nanobot-A/workspace/` |
| **Cron Jobs** | 配置目录 | `~/.nanobot-A/cron/` |
| **Media / runtime state** | 配置目录 | `~/.nanobot-A/media/` |

## 工作原理

- `--config` 选择要加载的配置文件。
- 默认情况下，工作区来自该配置中的 `agents.defaults.workspace`。
- 如果传入 `--workspace`，它会覆盖配置文件中的工作区。

## 最小配置

1. 将基础配置复制到新的实例目录。
2. 为该实例设置不同的 `agents.defaults.workspace`。
3. 使用 `--config` 启动该实例。

配置示例：

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.nanobot-telegram/workspace",
      "model": "anthropic/claude-sonnet-4-6"
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_TELEGRAM_BOT_TOKEN"
    }
  },
  "gateway": {
    "host": "127.0.0.1",
    "port": 18790
  }
}
```

启动独立实例：

```bash
nanobot gateway --config ~/.nanobot-telegram/config.json
nanobot gateway --config ~/.nanobot-discord/config.json
```

每个 gateway 实例还会在 `gateway.host:gateway.port` 暴露一个轻量 HTTP 健康检查端点。默认情况下，gateway 绑定到 `127.0.0.1`，所以端点会保持本地访问，除非你显式将 `gateway.host` 设置为公网或局域网地址。

- `GET /health` 返回 `{"status":"ok"}`。
- 其他路径返回 `404`。

需要时，可以为一次性运行覆盖工作区：

```bash
nanobot gateway --config ~/.nanobot-telegram/config.json --workspace /tmp/nanobot-telegram-test
```

## 常见使用场景

- 为 Telegram、Discord、飞书和其他平台运行独立 Bot。
- 隔离测试实例和生产实例。
- 为不同团队使用不同模型或 Provider。
- 使用独立配置和运行时数据服务多个租户。

## 注意事项

- 如果多个实例同时运行，每个实例都必须使用不同端口。
- 如果你希望记忆、会话和技能彼此隔离，请为每个实例使用不同工作区。
- `--workspace` 会覆盖配置文件中定义的工作区。
- Cron 任务和运行时媒体/状态由配置目录推导。
