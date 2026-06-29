# xiaomiaoVirtual 项目结构说明

## 顶层目录

```text
xiaomiaoVirtual/
├── xiaomiao/         # Python QQ Bot 主项目
├── xiaomiaoAgent/    # Agent 后端与工具系统
├── xiaomiaobot/      # Web/桌面/移动端表现层 monorepo
├── characters/       # 角色人设
├── docs/             # 项目文档
├── scripts/          # 仓库级辅助脚本
├── test/             # 仓库级测试
├── tool/             # 统一工具层与第三方接入
└── web/              # 仓库级可视化/监控页面
```

## 文档结构

当前 `docs/` 只保留有效入口，历史内容统一归档：

```text
docs/
├── README.md
├── 00-quick-start/
├── getting-started/
├── user-guide/
├── subsystems/
├── refactor/
└── archive/
```

说明：

- `user-guide/` 是当前用户侧主入口
- `archive/` 存放历史 plans/reports/tasks/changelogs
- `guide/`、`live2d/` 等旧分组不再作为主入口，后续可继续收敛

## xiaomiao

```text
xiaomiao/
├── main.py                   # 主入口，当前仍负责事件注册与主流程编排
├── commands/                 # 命令模块
├── handlers/                 # 命令/消息处理器
├── services/                 # 服务层
├── routing/                  # 路由
├── models/                   # 数据模型
├── core/                     # 核心应用对象
├── utils/                    # 公共工具
├── assets/                   # 资源文件
├── archive/                  # 历史代码
├── deprecated/               # 废弃兼容代码
└── docs/                     # 子项目局部文档
```

## 监控与可视化

仓库级监控页面、生成脚本和启动脚本统一放在：

```text
web/
└── monitoring/
```

这里存放：

- `web/monitoring/monitor-api.py`
- `monitor-dashboard*.html`
- `generate-*monitor.py`
- `start-monitor*.cmd`

## 整理原则

- 根目录只放仓库级入口、配置、脚本和说明文档
- 子项目内部结构尽量保持各自生态约定，不强行上提
- 仓库级重复文档、重复面板和一次性报告优先归档或删除
