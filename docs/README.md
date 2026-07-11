# xiaomiaoVirtual 文档中心

本文档目录只保留当前有效文档；历史计划、报告和一次性任务记录统一放在 `docs/archive/`。

## 快速入口

- [getting-started/README.md](getting-started/README.md): 3 分钟快速上手
- [00-quick-start/SETUP.md](00-quick-start/SETUP.md): 首次环境配置
- [00-quick-start/run-and-config.md](00-quick-start/run-and-config.md): 完整启动与配置说明
- [user-guide/qq-bot/README.md](user-guide/qq-bot/README.md): QQ Bot 使用指南
- [user-guide/monitoring.md](user-guide/monitoring.md): 服务监控面板说明

## 当前结构

### 启动与配置

- [00-quick-start/](00-quick-start/): 原始快速启动材料与指令速查
- [getting-started/](getting-started/): 当前推荐的新手入口

### 用户文档

- [user-guide/qq-bot/](user-guide/qq-bot/): QQ Bot 使用与场景
- [user-guide/agent/examples.md](user-guide/agent/examples.md): Agent API 示例
- [user-guide/examples/](user-guide/examples/): 配置与使用示例
- [user-guide/live2d/](user-guide/live2d/): Live2D 切换与模型位置
- [user-guide/monitoring.md](user-guide/monitoring.md): 本地监控面板

### 架构与子系统

- [subsystems/xiaomiao/README.md](subsystems/xiaomiao/README.md): QQ Bot 子系统
- [subsystems/xiaomiaoAgent/README.md](subsystems/xiaomiaoAgent/README.md): Agent 子系统
- [subsystems/xiaomiaobot/README.md](subsystems/xiaomiaobot/README.md): 前端表现层
- [subsystems/xiaomiaobot/services-and-plugins.md](subsystems/xiaomiaobot/services-and-plugins.md): 服务与插件
- [subsystems/xiaomiaobot/struct.md](subsystems/xiaomiaobot/struct.md): 前端完整结构索引

### 历史归档

- [archive/plans/](archive/plans/): 历史开发计划
- [archive/refactor/](archive/refactor/): 已归档的重构计划、设计和交付记录
- [archive/reports/](archive/reports/): 历史报告与阶段总结
- [archive/tasks/](archive/tasks/): 已完成/历史任务记录
- [archive/changelogs/](archive/changelogs/): 历史变更日志

## 说明

- `guide/` 和 `live2d/` 目录已经不再作为主入口，优先使用 `getting-started/` 与 `user-guide/`
- `docs/changelog/`、`docs/report/`、`docs/task/` 的重复副本已移除，统一保留归档版本
- 监控相关静态页面和脚本会统一收拢到仓库根级 `web/monitoring/`
