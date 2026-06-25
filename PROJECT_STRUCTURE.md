# xiaomiaoVirtual 项目结构说明

## 📁 顶层目录结构

```
xiaomiaoVirtual/
├── xiaomiao/              # QQ 机器人核心
├── xiaomiaoAgent/         # Agent 后端框架
├── xiaomiaobot/           # Web 前端 (已移除)
├── characters/            # 角色人设配置
├── tool/                  # 统一工具层
├── test/                  # 测试文件
├── docs/                  # 📚 项目文档 (主要)
└── scripts/               # 辅助脚本
```

---

## 📚 docs/ 文档目录 (已整理)

### 核心文档

```
docs/
├── README.md                          # 📖 文档入口 (从这里开始)
├── MONITOR_DASHBOARD_GUIDE.md        # 监控面板指南
│
├── 00-quick-start/                   # 🚀 快速开始
│   ├── SETUP.md                      # 安装配置
│   ├── run-and-config.md             # 运行指南
│   └── QQ机器人指令速查.md
│
├── 01-configuration/                 # ⚙️ 配置
│   ├── configuration.md              # 配置说明
│   ├── troubleshooting.md            # 故障排查
│   └── scripts-and-config.md
│
├── 02-architecture/                  # 🏗️ 架构
│   ├── project-overview.md
│   ├── project-deep-classification.md
│   ├── bridge-events.md
│   └── mcp-and-external-services.md
│
├── 03-subsystems/                    # 📦 子系统
│   ├── xiaomiao/
│   ├── xiaomiaoAgent/
│   └── xiaomiaobot/
│
├── 04-development/                   # 👨‍💻 开发
│   ├── development-maintenance.md
│   ├── testing-and-quality.md
│   ├── verification.md
│   └── file-workspace-hygiene.md
│
├── 05-tools/                         # 🛠️ 工具
│   └── tool-directory-analysis.md
│
├── 06-examples/                      # 📋 示例
│   ├── README.md
│   ├── agent-api-examples.md
│   ├── config-examples.md
│   └── qq-bot-scenarios.md
│
├── guide/                            # 📖 指南
│   ├── QUICK_START.md
│   ├── CONFIGURATION.md
│   └── QQ_BOT_GUIDE.md
│
├── live2d/                           # 🎨 Live2D
│   ├── LIVE2D_CHARACTER_SWITCH.md
│   ├── LIVE2D_MODELS_LOCATION.md
│   └── QQ_CHARACTER_SWITCH.md
│
├── refactor/                         # 🔧 重构文档
│   ├── README.md                     # 重构总览
│   ├── COMPLETION_REPORT.md          # ⭐ 完成报告
│   ├── index.md
│   ├── QUICK_START.md
│   ├── CHECKLIST.md
│   ├── DELIVERY_SUMMARY.md
│   ├── master-refactor-plan.md
│   ├── xiaomiao-refactor-plan.md
│   ├── xiaomiao-command-system-design.md
│   ├── xiaomiaoAgent-tools-reorganization.md
│   └── command-system-integration-guide.md
│
├── changelog/                        # 📝 变更日志
│   ├── WEBUI_REMOVAL_CHANGELOG.md
│   ├── WEBUI_REMOVAL_COMPLETE.md
│   └── WEBUI_REMOVED.md
│
├── report/                           # 📊 报告
│   ├── FUNCTIONAL_TEST_REPORT_2026-06-13.md
│   ├── PROJECT_FINAL_SUMMARY.md
│   └── TEST_REPORT_2026-06-13.md
│
├── task/                             # 📋 任务
│   ├── ATRI_NATSUME_MANUAL_UPLOAD.md
│   ├── ELECTRON_ESM_ISSUE.md
│   ├── LIVE2D_CHARACTER_VERIFICATION.md
│   └── WEB_LIVE2D_MODELS_ISSUE.md
│
└── archive/                          # 📦 历史归档 (新增)
    └── reports/                      # 已完成的报告
        ├── CODE_CONSOLIDATION_ANALYSIS.md
        ├── PROJECT_DOCS_HEALTH_CHECK.md
        ├── TASK_SUMMARY_PRIORITY_1.md
        ├── TASK_SUMMARY_PRIORITY_2.md
        ├── REFACTORING_PHASE1_COMPLETE.md
        ├── REFACTORING_PHASE2_COMPLETE.md
        ├── REFACTORING_PROGRESS.md
        ├── DOCS_IMPROVEMENT_REPORT_2026-06-24.md
        ├── PROJECT_DOCS_OPTIMIZATION_COMPLETE.md
        ├── PROJECT_OPTIMIZATION_PLAN_2026-06-25.md
        └── FILE_CLEANUP_PLAN.md
```

---

## 🗂️ xiaomiao/ 目录 (已整理)

```
xiaomiao/
├── main.py                           # ⭐ 主程序 (已集成命令系统)
├── config.json                       # 配置文件
├── requirements.txt                  # Python 依赖
│
├── commands/                         # 🎯 命令模块 (新)
│   ├── __init__.py
│   ├── base.py                       # 命令基类
│   ├── registry.py                   # 注册表
│   ├── basic.py                      # 基础命令 (3)
│   ├── image.py                      # 图片命令 (3)
│   ├── agent.py                      # Agent 命令 (6)
│   └── persona.py                    # 角色命令 (4)
│
├── handlers/                         # 🔀 处理器
│   ├── __init__.py
│   ├── command_dispatcher.py         # 命令分发器 (新)
│   ├── text_handler.py
│   └── command_handler.py
│
├── services/                         # 🛠️ 服务层 (新)
│   ├── image_service.py              # 图片服务
│   └── persona_service.py            # 人设服务
│
├── core/                             # 核心模块
├── models/                           # 数据模型
├── routing/                          # 路由系统
├── runtime/                          # 运行时数据
│
└── archive/                          # 📦 归档 (新增)
    ├── main_new.py                   # 旧的示例文件
    └── character_commands.py         # 已迁移的命令
```

---

## 🧪 test/ 目录

```
test/
├── xiaomiao/
│   └── test_commands.py              # 命令系统测试 (9/12 通过)
│
├── xiaomiaoAgent/
│   └── (Agent 测试)
│
└── xiaomiaobot/
    └── (前端测试)
```

---

## 🎭 characters/ 角色配置

```
characters/
├── xiaomiao/                         # 小喵角色
│   ├── IDENTITY.md
│   └── SOUL.md
│
├── atri/                             # ATRI 角色
│   ├── IDENTITY.md
│   └── SOUL.md
│
└── natsume/                          # 夏目角色
    ├── IDENTITY.md
    └── SOUL.md
```

---

## 🛠️ tool/ 统一工具层

```
tool/
├── adapters/                         # 适配器
│   └── qq_adapter.py
│
└── vendor/                           # 第三方工具
    ├── markitdown/
    └── Scrapling/
```

---

## 📊 整理成果

### 清理的文件

- ✅ 归档 11 个历史报告到 `docs/archive/reports/`
- ✅ 归档 2 个过时文件到 `xiaomiao/archive/`
- ✅ 清理所有 Python 缓存文件 (`__pycache__`, `*.pyc`)

### 目录优化

- ✅ **保留原有编号结构** (00-quick-start, 01-configuration, ...)
- ✅ **新增 archive/** - 历史文档归档
- ✅ **新增 commands/** - 命令模块
- ✅ **新增 services/** - 服务层
- ✅ **新增 handlers/** - 处理器

### 文档优化

- ✅ 所有活跃文档保留在原位置
- ✅ 历史报告归档,不影响查找
- ✅ 目录结构清晰,层级分明

---

## 🎯 快速导航

### 新用户
1. [docs/README.md](../docs/README.md) - 文档入口
2. [docs/00-quick-start/SETUP.md](../docs/00-quick-start/SETUP.md) - 安装指南
3. [docs/00-quick-start/run-and-config.md](../docs/00-quick-start/run-and-config.md) - 运行指南

### 开发者
1. [docs/refactor/COMPLETION_REPORT.md](../docs/refactor/COMPLETION_REPORT.md) - 重构报告
2. [docs/04-development/development-maintenance.md](../docs/04-development/development-maintenance.md) - 开发规范
3. [xiaomiao/commands/](../xiaomiao/commands/) - 命令系统代码

### 用户
1. [docs/guide/QQ_BOT_GUIDE.md](../docs/guide/QQ_BOT_GUIDE.md) - QQ 机器人指南
2. [docs/06-examples/](../docs/06-examples/) - 使用示例
3. [docs/live2d/](../docs/live2d/) - Live2D 角色

---

**最后更新**: 2025-06-25  
**整理人**: Claude Opus 4.8 (1M context)
