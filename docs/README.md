# xiaomiaoVirtual 文档入口

本文是 `docs/` 目录总导航。第一次阅读建议按“快速运行 -> 项目结构 -> 子系统文档 -> 验证维护”的顺序看。

## 快速入口

| 文档 | 用途 |
|------|------|
| [运行与配置.md](运行与配置.md) | 最短运行入口，包含 `setup-env.cmd` 和 `start-all.cmd` |
| [STARTUP.md](STARTUP.md) | 详细启动、端口、手动运行和常见问题 |
| [project-overview.md](project-overview.md) | 项目整体目录、子系统职责和运行边界 |
| [project-deep-classification.md](project-deep-classification.md) | 项目目录深度分类、清理清单和保留边界 |
| [verification.md](verification.md) | 单测、前端测试、启动检查和验收命令 |
| [testing-and-quality.md](testing-and-quality.md) | 测试目录职责和质量检查范围 |
| [QQ机器人指令速查.md](QQ机器人指令速查.md) | QQ 群聊/私聊可用指令 |
| [scripts-and-config.md](scripts-and-config.md) | 根目录脚本和本地配置说明 |
| [mcp-and-external-services.md](mcp-and-external-services.md) | MCP、Computer Use、Twitter、Minecraft 和外部服务权限 |
| [bridge-events.md](bridge-events.md) | bridge event 字段、接口和消费端 |
| [development-maintenance.md](development-maintenance.md) | 开发、维护、验证和文档规则 |

## 子系统文档

| 子系统 | 文档 |
|--------|------|
| `xiaomiao` QQ 机器人 | [xiaomiao/README.md](xiaomiao/README.md) |
| `xiaomiao` 部署打包 | [xiaomiao/deploy/README_DEPLOY.md](xiaomiao/deploy/README_DEPLOY.md) |
| `xiaomiaoAgent` 统一 Agent | [xiaomiaoAgent/README.md](xiaomiaoAgent/README.md) |
| `xiaomiaoAgent` 工具目录 | [xiaomiaoAgent/tools.md](xiaomiaoAgent/tools.md) |
| `xiaomiaobot` Web / 桌面表现层 | [xiaomiaobot/README.md](xiaomiaobot/README.md) |
| `xiaomiaobot` 操作文档 | [xiaomiaobot/操作文档.md](xiaomiaobot/操作文档.md) |
| `xiaomiaobot` 服务与插件 | [xiaomiaobot/services-and-plugins.md](xiaomiaobot/services-and-plugins.md) |
| `xiaomiaobot` 全结构索引 | [xiaomiaobot/struct.md](xiaomiaobot/struct.md) |
| `tool/markitdown` 与 `tool/Scrapling` | [tool/tool-directory-analysis.md](tool/tool-directory-analysis.md) |
| 文件和 workspace 规则 | [file-workspace-hygiene.md](file-workspace-hygiene.md) |

## 架构和计划

| 文档 | 用途 |
|------|------|
| [../README.md](../README.md) | 项目根入口和当前能力概览 |
| [../TECHNICAL.md](../TECHNICAL.md) | 技术结构、桥接协议、风险和演进路线 |
| [plans/README.md](plans/README.md) | 计划书索引、完成度和后续缺口 |
| [plans/2026-06-06-qq-agent-xiaomiaobot-capability-integration.md](plans/2026-06-06-qq-agent-xiaomiaobot-capability-integration.md) | QQ 直连 Agent / xiaomiaobot 能力计划 |
| [plans/2026-06-06-project-deep-analysis-and-qq-agent-gap-audit.md](plans/2026-06-06-project-deep-analysis-and-qq-agent-gap-audit.md) | 项目深度审计和缺口跟踪 |

## 当前覆盖状态

| 范围 | 状态 |
|------|------|
| 启动和环境配置 | 已覆盖 |
| QQ 指令和权限 | 已覆盖 |
| QQ 文件下载、Markdown 转换、workspace | 已覆盖 |
| xiaomiao QQ 机器人 | 已覆盖 |
| xiaomiaobot 表现层 | 已覆盖 |
| xiaomiaoAgent 统一 Agent 能力 | 已覆盖 |
| root 脚本、配置文件、健康检查 | 已覆盖 |
| 项目深度分类和清理边界 | 已覆盖 |
| MCP 和外部服务配置 | 已覆盖 |
| 测试和验收矩阵 | 已补本目录入口 |
| 测试目录和质量边界 | 已覆盖 |
| bridge event 协议 | 已覆盖 |
| xiaomiaobot 服务和插件简表 | 已覆盖 |
| docs/plans 计划索引 | 已覆盖 |
