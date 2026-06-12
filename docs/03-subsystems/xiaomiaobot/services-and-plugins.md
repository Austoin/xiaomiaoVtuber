# xiaomiaobot 服务与插件清单

本文说明 `xiaomiaobot/` 中应用、服务、插件和关键包的用途，以及当前与 QQ / xiaomiaoAgent 的接入状态。

## 应用目录

| 路径 | 用途 | 当前接入 |
|------|------|----------|
| `apps/stage-web` | Web 舞台和网页聊天入口 | 已通过 xiaomiao bridge 进入统一 Agent |
| `apps/stage-tamagotchi` | Electron 桌面端、Live2D / VRM / TTS 表现层 | 已消费 bridge 状态和 bridge event |
| `apps/stage-pocket` | 移动端 / PWA | 已只读同步 bridge event |
| `apps/server` | server-runtime API、鉴权、计费、角色和聊天服务 | 项目内保留，暂不是 QQ 主链路 |
| `apps/component-calling` | 组件调用示例和插件化组件实验 | 暂不是 QQ 主链路 |
| `apps/ui-server-auth` | 服务端鉴权 UI | 暂不是 QQ 主链路 |

## 服务目录

| 路径 | 用途 | QQ / Agent 状态 |
|------|------|----------------|
| `services/computer-use-mcp` | 本机窗口、终端、浏览器操作 MCP | 可通过 Agent MCP 配置档启用，高风险动作需确认 |
| `services/minecraft` | Minecraft 机器人和认知/动作服务 | 可通过 Agent MCP 配置档启用，动作需确认 |
| `services/twitter-services` | Twitter / X 读取和账号动作服务 | 可通过 Agent MCP 配置档启用，发帖/点赞/转发需确认 |
| `services/satori-bot` | Satori bot 服务 | 当前不是 QQ 主链路 |
| `services/discord-bot` | Discord bot 服务 | 当前不是 QQ 主链路 |
| `services/telegram-bot` | Telegram bot 服务 | 当前不是 QQ 主链路 |

## 插件目录

| 路径 | 用途 | QQ / Agent 状态 |
|------|------|----------------|
| `plugins/airi-plugin-homeassistant` | HomeAssistant 插件 | 目录存在，QQ Agent 动作未接通 |
| `plugins/airi-plugin-bilibili-laplace` | Bilibili 直播/弹幕相关插件 | 目录存在，QQ Agent 动作未接通 |
| `plugins/airi-plugin-game-chess` | Chess 游戏插件 | 目录存在，QQ Agent 适配未接通 |
| `plugins/airi-plugin-claude-code` | Claude Code 插件 hook | 目录存在，高风险接入未完成 |
| `plugins/airi-plugin-web-extension` | 浏览器扩展上下文桥 | 目录存在，QQ Agent 上下文适配未接通 |

## 关键包

| 路径 | 用途 |
|------|------|
| `packages/stage-layouts` | stage-web / stage-tamagotchi 布局和 xiaomiao bridge 客户端 |
| `packages/stage-ui` | 舞台 UI、TTS、组件、状态管理 |
| `packages/stage-ui-live2d` | Live2D 渲染和状态 |
| `packages/stage-ui-three` | Three.js / VRM 相关能力 |
| `packages/model-driver-lipsync` | 口型同步 |
| `packages/plugin-sdk` | 插件 SDK |
| `packages/plugin-protocol` | 插件协议类型 |
| `packages/memory-pgvector` | pgvector 记忆包，当前未和 xiaomiaoAgent 记忆层合并 |
| `packages/server-runtime` | server runtime 能力 |
| `packages/pipelines-audio` | 音频处理管线 |

## 已打通的 Agent 工具

| 工具 | 说明 |
|------|------|
| `xiaomiao_stage` | 发布 `stage_action` 事件，驱动字幕、TTS、表情、背景、模型切换 |
| `xiaomiaobot_status` | 查询 bridge 和 xiaomiaobot 服务状态 |
| `xiaomiaobot_action` | 当前端到端支持 stage 动作，其它服务会显式返回未接通 |

## 当前边界

- QQ 不直接操作 `xiaomiaobot` 前端内部状态，而是通过 xiaomiao bridge event 或 Agent 工具适配。
- stage 动作已经可以端到端触发；Computer Use、Minecraft、Twitter 走显式启用 MCP 配置档，配置与风险边界见 [../mcp-and-external-services.md](../mcp-and-external-services.md)。
- HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension 当前仍是待接通能力。
- `stage-pocket` 当前是只读同步，不执行舞台动作。
- `memory-pgvector` 暂未合并到 xiaomiaoAgent 记忆层。

## 验证

桥接事件测试：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot
pnpm exec vitest run apps/stage-pocket/src/modules/xiaomiao-bridge-events.test.ts packages/stage-ui/src/xiaomiao-bridge-events.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.test.ts
```

完整启动检查：

```powershell
cd F:\xiaomiaoVirtual
cmd /c call start-all.cmd --check
```
