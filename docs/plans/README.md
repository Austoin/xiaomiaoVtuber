# 计划书索引

本文是 `docs/plans/` 的中文索引，用于区分历史计划、已完成实施记录和仍需继续推进的能力缺口。当前运行方式、配置和验收命令以 `docs/运行与配置.md`、`docs/STARTUP.md`、`docs/verification.md` 为准。

## 当前主计划

| 文档 | 状态 | 说明 |
|------|------|------|
| [2026-06-06-project-deep-analysis-and-qq-agent-gap-audit.md](2026-06-06-project-deep-analysis-and-qq-agent-gap-audit.md) | 当前审计基线 | 说明上一计划完成度、当前已闭环链路和后续缺口 |
| [2026-06-06-qq-agent-xiaomiaobot-capability-integration.md](2026-06-06-qq-agent-xiaomiaobot-capability-integration.md) | 部分完成，继续推进 | QQ 权限、确认、记忆、工具事件、舞台动作和第一批工具已完成；部分 xiaomiaobot 服务仍待产品化 |

## 已完成或基本完成的历史计划

| 文档 | 状态 | 说明 |
|------|------|------|
| [2026-06-04_20-51-53-xiaomiao-agent-bot-deep-plan.md](2026-06-04_20-51-53-xiaomiao-agent-bot-deep-plan.md) | 已完成主要阶段 | 三端联动、消息模型、权限分层、真实启动和残留风险加固已完成 |
| [2026-06-02_19-25-09-three-end-agent-unification.md](2026-06-02_19-25-09-three-end-agent-unification.md) | 已完成主体 | QQ、Web、Agent WebUI 统一会话和桥接事件的早期执行记录 |
| [2026-06-02_15-49-30-xiaomiao-web-nanobot-fusion.md](2026-06-02_15-49-30-xiaomiao-web-nanobot-fusion.md) | 已完成主体 | stage-web、桌面桥接和 QQ 普通 AI 回复接入 Agent 的早期计划 |

## 历史背景

| 文档 | 状态 | 说明 |
|------|------|------|
| [2026-05-12-xiaomiao-console-fusion.md](2026-05-12-xiaomiao-console-fusion.md) | 历史参考 | 早期“小喵 QQ Bot 控制台”方案，当前已被三端 Agent 联动路线覆盖 |

## 未完成重点

| 范围 | 当前状态 |
|------|----------|
| HomeAssistant / Bilibili / Chess | 有插件或服务痕迹，但尚未形成 QQ 可直接稳定调用的 Agent 工具闭环 |
| Claude Code / Browser Extension | 有通道或上下文能力，仍缺受控 QQ 工具面 |
| Computer Use / Minecraft / Twitter | 已有安全配置档，真实外部服务仍需按需启动和联调 |
| stage-pocket | 已完成第一批只读事件同步，仍缺绑定握手、动态地址配置和专门事件 UI |
| `memory-pgvector` | 尚未和 xiaomiaoAgent 记忆层合并 |

## 使用规则

- 新计划优先放在本目录，并在本索引登记。
- 已完成计划保留执行记录，不直接删除。
- 计划状态改变后，同步更新本索引和 `docs/README.md`。
- 面向用户的运行说明不要只写在计划书里，要同步到正式文档。
