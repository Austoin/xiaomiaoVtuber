# xiaomiaoVirtual

xiaomiaoVirtual 使用一个统一智能体：`xiaomiaoAgent`。QQ、Web、Pocket 和 Electron 都只负责输入输出、媒体处理和界面交互，不在端侧运行第二套 LLM Agent。

## 架构

```text
QQ / NapCat ──> xiaomiao/main.py ───────┐
Stage Web / Pocket / Electron ──────────┤
Minecraft Mineflayer ───────────────────┼──> xiaomiaoAgent
Discord / Telegram / embedded WebUI ────┘       ├── HTTP API :8900
                                                ├── Gateway :18790
                                                ├── WebUI/WebSocket :8765
                                                └── Twitter/Minecraft MCP tools
```

- [`xiaomiaoAgent/`](xiaomiaoAgent/README.md)：唯一推理、记忆、会话和工具执行层。
- [`xiaomiao/`](xiaomiao/README.md)：QQ/NapCat 通道适配器，调用 Agent HTTP API。
- [`xiaomiaobot/`](xiaomiaobot/README.md)：Web、Pocket、Electron 客户端，以及 Minecraft、Twitter 外部服务。
- `test/xiaomiao/`：QQ 适配器测试。
- `scripts/`：统一启动与环境检查脚本。

## 端口

| 端口 | 服务 |
| --- | --- |
| `5004` | NapCat OneBot WebSocket |
| `8900` | xiaomiaoAgent HTTP API、事件和配置 |
| `18790` | xiaomiaoAgent Gateway 健康检查 |
| `8765` | 内嵌 WebUI 与 WebSocket 通道 |
| `5175` | Stage Web 开发服务器 |
| `8080` | Twitter MCP，启用服务后使用 |
| `3001` | Minecraft 调试 MCP，显式启用后使用 |

## 启动

```powershell
pnpm start
```

也可以分开启动：

```powershell
menu.cmd agent-api
menu.cmd agent-webui
menu.cmd agent-gateway
menu.cmd qq
menu.cmd bot-web
menu.cmd bot-minecraft
menu.cmd bot-twitter
```

检查服务状态但不启动窗口：

```powershell
menu.cmd check
```

## 配置

根目录 `config.json` 是统一配置入口：

- `xiaomiaoAgent`：模型与 Provider。
- `xiaomiao_agent`：QQ 适配器访问 Agent API 的地址、会话和超时。
- `xiaomiaoAgent.channels`：WebSocket、Discord、Telegram 等 Agent 原生通道。
- `xiaomiaoAgent.tools`：Twitter、Minecraft 等 MCP 工具配置。

运行时缓存统一存放在 `.cache/`，密钥不会通过 `/v1/xiaomiao/config` 返回给前端。

## 验证

```powershell
python -m pytest test/xiaomiao -q
cd xiaomiaoAgent
uv run pytest -q
uv run ruff check nanobot tests
cd ..\xiaomiaobot
pnpm --filter @proj-airi/core-agent typecheck
pnpm --filter @proj-airi/stage-ui typecheck
pnpm --filter @proj-airi/stage-web typecheck
pnpm --filter @proj-airi/stage-pocket typecheck
pnpm --filter @proj-airi/stage-tamagotchi typecheck
```

详细启动与配置见 [文档中心](docs/README.md)、[快速开始](docs/guide/QUICK_START.md)、[集成指南](docs/guide/INTEGRATIONS.md)和 [Agent API](xiaomiaoAgent/docs/openai-api.md)。每个子项目的目录职责、常用命令、缓存边界和扩展建议统一维护在其 README 中，不再另设“项目文件目录说明”。
