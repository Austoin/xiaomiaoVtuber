# xiaomiaoAgent 文档

`nanobot` 代码包在本项目中以用户可见品牌 `xiaomiaoAgent` 运行。内部包名、Python import、配置目录和上游文档站仍保留 `nanobot` 命名。

上游最新文档请访问 [nanobot.wiki](https://nanobot.wiki/docs/latest/getting-started/nanobot-overview)。

本目录中的页面会跟随当前仓库更新，可能比已发布的网站文档更新更快。

## xiaomiaoVirtual 集成状态

当前仓库内的 xiaomiaoAgent 已作为 `xiaomiaoVirtual` 的统一能力层运行：

- QQ 群/私聊普通 AI 回复、stage-web 输入、desktop bridge 和 WebUI 共享 `xiaomiao-unified` 会话。
- QQ 请求会携带 `channel/chat_id/user_id/session_id/tool_policy/confirmation_id` 等元数据。
- 普通 QQ 用户默认 `low_risk`；ROOT/Super/`agent_tool_allowlist` 用户高风险动作需要确认后才会进入 `trusted_confirmed`。
- 已接入低风险工具 `markitdown_convert`、`scrapling_get`。
- 已提供 Computer Use、Twitter、Minecraft opt-in MCP 安全 profile，默认关闭，启用后按低风险/确认策略暴露。
- stage-web、stage-tamagotchi 和 stage-pocket 已能消费第一批 bridge events；stage-pocket 当前是只读同步。

相关项目文档：

- `../../docs/STARTUP.md`
- `../../docs/tool-directory-analysis.md`
- `../../docs/plans/2026-06-06-qq-agent-xiaomiaobot-capability-integration.md`
- `../../docs/plans/2026-06-06-project-deep-analysis-and-qq-agent-gap-audit.md`

## 核心文档

如果你要安装、日常使用或部署 xiaomiaoAgent，请从这里开始。

| 主题 | 仓库文档 | 内容说明 |
|---|---|---|
| 安装与快速开始 | [`quick-start.md`](./quick-start.md) | 安装、初始化和首次运行配置 |
| 聊天应用 | [`chat-apps.md`](./chat-apps.md) | 连接 Telegram、Discord、微信等平台 |
| Agent 社交网络 | [`agent-social-network.md`](./agent-social-network.md) | 从 xiaomiaoAgent 加入外部 Agent 社区 |
| 配置 | [`configuration.md`](./configuration.md) | Provider、工具、通道、MCP 和运行时设置 |
| 图像生成 | [`image-generation.md`](./image-generation.md) | 配置图像 Provider、WebUI 图像模式和生成产物 |
| 多实例 | [`multiple-instances.md`](./multiple-instances.md) | 使用独立配置和工作区运行多个 Bot |
| CLI 参考 | [`cli-reference.md`](./cli-reference.md) | 核心 CLI 命令和常用入口 |
| 聊天内命令 | [`chat-commands.md`](./chat-commands.md) | Slash 命令和周期任务行为 |
| OpenAI 兼容 API | [`openai-api.md`](./openai-api.md) | 本地 API 端点、请求格式、文件上传和 xiaomiaoVirtual 集成 |
| 部署 | [`deployment.md`](./deployment.md) | Docker、Linux service 和 macOS LaunchAgent 配置 |

## 高级文档

当你需要更深入的定制、集成或扩展时，请阅读这些文档。

| 主题 | 仓库文档 | 内容说明 |
|---|---|---|
| 记忆 | [`memory.md`](./memory.md) | xiaomiaoAgent 如何存储、整理和恢复记忆 |
| Python SDK | [`python-sdk.md`](./python-sdk.md) | 在 Python 中以编程方式使用 xiaomiaoAgent |
| 通道插件指南 | [`channel-plugin-guide.md`](./channel-plugin-guide.md) | 构建和测试自定义聊天通道插件 |
| WebSocket 通道 | [`websocket.md`](./websocket.md) | 实时 WebSocket 访问和协议细节 |
| 自定义工具 | [`my-tool.md`](./my-tool.md) | 使用 `my` 工具检查和调整运行时状态 |
