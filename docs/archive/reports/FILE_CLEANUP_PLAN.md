# 项目文件整理方案

## 📋 当前问题

1. **docs/ 根目录混乱** - 12 个历史报告文件散落在根目录
2. **重复文档** - changelog、report、task 目录有大量历史文档
3. **文档分类不清** - 缺少清晰的目录结构
4. **过时文档** - 大量历史优化报告已过时

## 🎯 整理目标

### 新的 docs 结构

```
docs/
├── README.md                    # 文档总入口
│
├── getting-started/             # 快速开始 (合并 00-quick-start + guide)
│   ├── README.md
│   ├── installation.md         # 安装指南
│   ├── configuration.md        # 配置指南
│   └── first-run.md            # 首次运行
│
├── user-guide/                  # 用户指南
│   ├── qq-bot/                 # QQ 机器人
│   │   ├── README.md
│   │   ├── commands.md         # 命令列表
│   │   ├── permissions.md      # 权限管理
│   │   └── troubleshooting.md  # 故障排除
│   │
│   ├── agent/                  # Agent 使用
│   │   ├── README.md
│   │   ├── api-usage.md
│   │   └── examples.md
│   │
│   └── live2d/                 # Live2D 角色
│       ├── README.md
│       ├── character-switch.md
│       └── models-location.md
│
├── developer/                   # 开发者文档
│   ├── README.md
│   ├── architecture.md         # 架构说明
│   ├── command-system.md       # 命令系统
│   ├── contributing.md         # 贡献指南
│   └── testing.md              # 测试指南
│
├── subsystems/                  # 子系统文档 (保留)
│   ├── xiaomiao/
│   ├── xiaomiaoAgent/
│   └── xiaomiaobot/
│
└── archive/                     # 历史文档归档
    ├── reports/                # 项目报告
    │   ├── 2026-06-24-docs-improvement.md
    │   ├── 2026-06-25-optimization-plan.md
    │   └── refactoring-phases/
    │       ├── phase1.md
    │       ├── phase2.md
    │       └── progress.md
    │
    ├── changelogs/             # 变更日志
    │   └── webui-removal/
    │
    └── tasks/                  # 历史任务
        ├── live2d-issues.md
        └── electron-esm.md
```

## 📦 文件移动计划

### 1. 需要删除的文件 (过时/重复)

```
docs/
├── CODE_CONSOLIDATION_ANALYSIS.md          → 删除 (已过时)
├── DOCS_IMPROVEMENT_REPORT_2026-06-24.md   → archive/reports/
├── PROJECT_DOCS_HEALTH_CHECK.md            → 删除 (已完成)
├── PROJECT_DOCS_OPTIMIZATION_COMPLETE.md   → archive/reports/
├── PROJECT_OPTIMIZATION_PLAN_2026-06-25.md → archive/reports/
├── REFACTORING_PHASE1_COMPLETE.md          → archive/reports/refactoring-phases/
├── REFACTORING_PHASE2_COMPLETE.md          → archive/reports/refactoring-phases/
├── REFACTORING_PROGRESS.md                 → archive/reports/refactoring-phases/
├── TASK_SUMMARY_PRIORITY_1.md              → 删除 (已完成)
├── TASK_SUMMARY_PRIORITY_2.md              → 删除 (已完成)
└── MONITOR_DASHBOARD_GUIDE.md              → user-guide/monitoring.md
```

### 2. 需要合并的目录

**合并 00-quick-start + guide → getting-started**
```
docs/00-quick-start/
├── SETUP.md              → getting-started/installation.md
└── run-and-config.md     → getting-started/configuration.md

docs/guide/
├── QUICK_START.md        → getting-started/README.md
├── CONFIGURATION.md      → 合并到 getting-started/configuration.md
└── QQ_BOT_GUIDE.md       → user-guide/qq-bot/README.md
```

**整理 06-examples → user-guide/examples**
```
docs/06-examples/
├── README.md             → user-guide/examples/README.md
├── agent-api-examples.md → user-guide/agent/examples.md
├── config-examples.md    → getting-started/configuration.md (合并)
└── qq-bot-scenarios.md   → user-guide/qq-bot/scenarios.md
```

**整理 live2d**
```
docs/live2d/
├── LIVE2D_CHARACTER_SWITCH.md → user-guide/live2d/character-switch.md
├── LIVE2D_MODELS_LOCATION.md  → user-guide/live2d/models-location.md
└── QQ_CHARACTER_SWITCH.md     → user-guide/live2d/ (合并)
```

**归档历史文档**
```
docs/changelog/ → docs/archive/changelogs/
docs/report/    → docs/archive/reports/
docs/task/      → docs/archive/tasks/
```

### 3. refactor 目录保留但简化

```
docs/refactor/
├── README.md                   # 保留 - 重构总入口
├── COMPLETION_REPORT.md        # 保留 - 完成报告
└── archive/                    # 其他文档归档
    ├── plans/
    │   ├── master-plan.md
    │   ├── xiaomiao-plan.md
    │   └── agent-tools-plan.md
    └── guides/
        ├── integration-guide.md
        └── checklist.md
```

## 🗑️ 立即删除的文件

以下文件已过时,可以安全删除:
1. `docs/CODE_CONSOLIDATION_ANALYSIS.md` - 临时分析文件
2. `docs/PROJECT_DOCS_HEALTH_CHECK.md` - 一次性检查报告
3. `docs/TASK_SUMMARY_PRIORITY_1.md` - 已完成任务
4. `docs/TASK_SUMMARY_PRIORITY_2.md` - 已完成任务

## 📝 新增必要文档

1. `docs/README.md` - 更新为清晰的导航页
2. `docs/getting-started/README.md` - 快速开始总览
3. `docs/user-guide/README.md` - 用户指南总览
4. `docs/developer/README.md` - 开发者文档总览
5. `docs/developer/command-system.md` - 命令系统文档 (基于 refactor/)

## ✅ 执行步骤

1. 创建新目录结构
2. 移动和合并文档
3. 删除过时文件
4. 更新所有文档内的链接
5. 创建新的 README 导航
6. Git 提交

---

**预计整理后**:
- 文档数量: 46 → ~25 (减少 45%)
- 目录层级: 清晰的 3 层结构
- 查找效率: 提升 10 倍
