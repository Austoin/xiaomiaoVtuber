# xiaomiaoVirtual 文档分类树

> **生成日期**: 2026-06-13  
> **文档总数**: 2336+ 个 Markdown 文件  
> **组织方式**: 按子系统 + 文档类型分类

---

## 📊 文档统计总览

| 位置 | 文件数 | 说明 |
|------|--------|------|
| **主文档** (docs/) | 31 | xiaomiaoVirtual 集成层文档 |
| **xiaomiaoAgent** | 16 | nanobot 上游完整文档 |
| **xiaomiaobot** | 2289+ | AIRI 上游文档站 + README |
| **总计** | **2336+** | 完整文档体系 |

---

## 🌳 完整文档树

### 主文档 (docs/) - 31 个文件

```
docs/
├── README.md                                   # 文档入口
├── DOCUMENTATION_INDEX.md                      # 📚 文档总索引（新增）
├── PROJECT_CHECK_REPORT_2026-06-13.md         # 项目检查报告
├── PROJECT_ARCHITECTURE_2026-06-13.md         # 架构总览（待生成）
├── DOCUMENTATION_TREE.md                       # 📄 本文档
├── TEST_COVERAGE_MATRIX.md                     # 测试矩阵（待生成）
│
├── 00-quick-start/                            # 快速开始 (3)
│   ├── run-and-config.md                      # ⭐ 最快启动
│   ├── STARTUP.md                             # 详细启动指南
│   └── QQ机器人指令速查.md                    # QQ 命令参考
│
├── 01-configuration/                          # 配置 (3)
│   ├── configuration.md                       # 统一配置
│   ├── troubleshooting.md                     # 🚨 故障排查 (701行)
│   └── scripts-and-config.md                  # 脚本和配置
│
├── 02-architecture/                           # 架构 (4)
│   ├── project-overview.md                    # 📐 项目覆盖图 + 架构图
│   ├── project-deep-classification.md         # 技术深度分类
│   ├── bridge-events.md                       # 桥接事件协议
│   └── mcp-and-external-services.md           # MCP 集成
│
├── 03-subsystems/                             # 子系统文档 (8)
│   ├── xiaomiao/                              # QQ 桥接 (2)
│   │   ├── README.md                          # 集成说明
│   │   └── deploy/
│   │       └── README_DEPLOY.md               # 部署指南
│   │
│   ├── xiaomiaoAgent/                         # Agent 能力层 (2)
│   │   ├── README.md                          # 集成说明
│   │   └── tools.md                           # 工具注册表
│   │
│   └── xiaomiaobot/                           # 表现层 (4)
│       ├── README.md                          # 集成说明
│       ├── operation-guide.md                 # 操作指南
│       ├── services-and-plugins.md            # 服务清单
│       └── struct.md                          # 目录结构
│
├── 04-development/                            # 开发维护 (4)
│   ├── development-maintenance.md             # 开发指南
│   ├── testing-and-quality.md                 # 测试质量
│   ├── verification.md                        # 验证矩阵
│   └── file-workspace-hygiene.md              # 文件规范
│
├── 05-tools/                                  # 工具 (1)
│   └── tool-directory-analysis.md             # tool/ 目录分析
│
└── plans/                                      # 规划 (7)
    ├── README.md                              # 规划索引
    ├── 2026-05-12-xiaomiao-console-fusion.md
    ├── 2026-06-02_15-49-30-xiaomiao-web-nanobot-fusion.md
    ├── 2026-06-02_19-25-09-three-end-agent-unification.md
    ├── 2026-06-04_20-51-53-xiaomiao-agent-bot-deep-plan.md
    └── ...
```

---

### xiaomiaoAgent 文档 (16 个文件)

**位置**: `xiaomiaoAgent/docs/`

```
xiaomiaoAgent/docs/
├── README.md                          # 📚 文档索引
├── quick-start.md                     # 快速开始
├── configuration.md                   # ⚙️ 配置详解
├── cli-reference.md                   # 🖥️ CLI 参考
├── chat-commands.md                   # 💬 聊天命令
├── openai-api.md                      # 🌐 OpenAI API
├── memory.md                          # 🧠 记忆系统
├── python-sdk.md                      # 🐍 Python SDK
├── deployment.md                      # 🚀 部署指南
├── image-generation.md                # 🎨 图像生成
├── channel-plugin-guide.md            # 🔌 通道插件开发
├── websocket.md                       # 🔌 WebSocket
├── my-tool.md                         # 🔧 MyTool
├── agent-social-network.md            # 🤖 Agent 社交
├── chat-apps.md                       # 📱 聊天应用集成
└── multiple-instances.md              # 🔄 多实例
```

**文档类型分类**:

| 类型 | 文件数 | 文件 |
|------|--------|------|
| **使用文档** | 8 | quick-start, configuration, cli-reference, chat-commands, openai-api, memory, image-generation, multiple-instances |
| **开发文档** | 5 | python-sdk, channel-plugin-guide, websocket, my-tool, agent-social-network |
| **部署文档** | 3 | deployment, chat-apps, multiple-instances |

---

### xiaomiaobot 文档 (2289+ 个文件)

**位置**: `xiaomiaobot/`

#### 根文档 (2)
```
xiaomiaobot/
├── AGENTS.md                          # 🤖 Agent 开发指南
└── CLAUDE.md                          # Claude 项目引用
```

#### VitePress 文档站 (多语言)
```
xiaomiaobot/docs/
├── .vitepress/                        # VitePress 配置
├── content/
│   ├── en/docs/                      # 英文文档
│   ├── zh-Hans/docs/                 # 简体中文文档
│   └── ja/docs/                      # 日文文档
├── ai/
│   └── context/
│       └── ui-components.md          # 🎨 UI 组件 API
└── scripts/                           # 文档构建脚本
```

#### App 专项文档
```
xiaomiaobot/apps/server/
├── CLAUDE.md                          # 服务器 Agent 指南
└── docs/
    └── ai-context/                   # 8 个详细架构文档
        ├── architecture-overview.md
        ├── transport-and-routes.md
        ├── data-model-and-state.md
        ├── billing-architecture.md
        ├── redis-boundaries-and-pubsub.md
        ├── auth-and-oidc.md
        ├── config-and-naming-conventions.md
        └── workers-and-runtime.md
```

#### Package README (2200+)
```
xiaomiaobot/packages/*/
└── README.md                          # 每个包的使用说明
```

**每个 package 的 README 包含**:
- 功能说明
- 使用方法
- 何时使用
- 何时不使用

**代表性包**:
- `packages/stage-ui/README.md` - 核心舞台组件
- `packages/core-agent/README.md` - Agent 运行时
- `packages/core-character/README.md` - 角色系统
- `packages/server-runtime/README.md` - 服务器运行时
- `packages/ui/README.md` - 基础组件库

---

## 📑 文档类型分类

### 按功能分类

| 功能类型 | 文档数量 | 主要位置 |
|---------|---------|---------|
| **快速开始** | 5 | docs/00-quick-start/, xiaomiaoAgent/docs/ |
| **配置说明** | 6 | docs/01-configuration/, xiaomiaoAgent/docs/ |
| **架构设计** | 12 | docs/02-architecture/, xiaomiaobot/apps/server/docs/ |
| **API 参考** | 4 | xiaomiaoAgent/docs/, xiaomiaobot/docs/ai/context/ |
| **开发指南** | 15+ | docs/04-development/, xiaomiaobot/AGENTS.md, 各 package/ |
| **部署运维** | 5 | xiaomiaoAgent/docs/, docs/03-subsystems/ |
| **工具文档** | 4 | docs/05-tools/, xiaomiaoAgent/docs/my-tool.md |
| **规划文档** | 7 | docs/plans/ |
| **Package 说明** | 2200+ | xiaomiaobot/packages/*/README.md |

### 按语言分类

| 语言 | 文档数量 | 位置 |
|------|---------|------|
| **简体中文** | 50+ | docs/, xiaomiaobot/docs/content/zh-Hans/ |
| **英文** | 2280+ | xiaomiaoAgent/docs/, xiaomiaobot/docs/content/en/, packages/ |
| **日文** | 6+ | xiaomiaobot/docs/content/ja/ |

### 按维护者分类

| 维护者 | 文档数量 | 说明 |
|--------|---------|------|
| **xiaomiaoVirtual** | 31 | 主 docs/ + 子系统集成文档 |
| **nanobot 上游** | 16 | xiaomiaoAgent/docs/ |
| **AIRI 上游** | 2289+ | xiaomiaobot/ 全部文档 |

---

## 🔍 文档查找指南

### 我想了解...

**如何启动项目？**
→ [运行与配置](00-quick-start/run-and-config.md)

**如何配置 Agent？**
→ [xiaomiaoAgent 配置详解](../xiaomiaoAgent/docs/configuration.md)

**如何开发插件？**
→ [通道插件开发](../xiaomiaoAgent/docs/channel-plugin-guide.md)

**如何使用 API？**
→ [OpenAI 兼容 API](../xiaomiaoAgent/docs/openai-api.md)

**如何开发前端组件？**
→ [AGENTS 开发指南](../xiaomiaobot/AGENTS.md)

**如何部署到生产环境？**
→ [xiaomiaoAgent 部署指南](../xiaomiaoAgent/docs/deployment.md)

**遇到问题怎么排查？**
→ [故障排查指南](01-configuration/troubleshooting.md)

**如何理解系统架构？**
→ [项目覆盖图](02-architecture/project-overview.md) (包含 Mermaid 架构图)

**如何开发服务器端？**
→ [服务器架构文档](../xiaomiaobot/apps/server/docs/ai-context/)

**UI 组件如何使用？**
→ [UI 组件 API 参考](../xiaomiaobot/docs/ai/context/ui-components.md)

---

## 📈 文档质量评估

### 优点
- ✅ **组织清晰**: 数字前缀分类 (00-05)
- ✅ **覆盖全面**: 从快速开始到深入架构
- ✅ **多语言支持**: 中英日三语
- ✅ **上游完整**: 子系统文档独立维护
- ✅ **实用性强**: 大量可执行命令和示例

### 待改进
- ⚠️ **长文档**: troubleshooting.md (701行) 建议拆分
- ⚠️ **缺少 API 文档**: xiaomiaoAgent OpenAI API 端点详细说明
- ⚠️ **缺少元文件**: CHANGELOG.md, CONTRIBUTING.md

---

## 🔗 相关文档

- [文档总索引](DOCUMENTATION_INDEX.md) - 快速导航
- [项目检查报告](PROJECT_CHECK_REPORT_2026-06-13.md) - 质量评估
- [测试覆盖矩阵](TEST_COVERAGE_MATRIX.md) - 测试统计

---

**文档维护**: 保持主文档聚焦集成说明，通过链接引用子系统详细文档
