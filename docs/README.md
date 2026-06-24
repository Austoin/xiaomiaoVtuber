# xiaomiaoVirtual 文档中心

欢迎来到 xiaomiaoVirtual 项目文档。本文档按使用场景分类，帮助您快速找到所需信息。

---

## 📂 文档分类

### 🚀 [00-quick-start/](00-quick-start/) - 快速开始

**新用户从这里开始**，包含最快速的启动和使用指南。

| 文档 | 用途 |
|------|------|
| [run-and-config.md](00-quick-start/run-and-config.md) | **⭐ 主快速启动文档**，一键启动、手动启动、配置说明、常见问题 |
| [SETUP.md](00-quick-start/SETUP.md) | **⭐ 克隆后必读**，依赖安装、模型下载、环境配置 |
| [QQ机器人指令速查.md](00-quick-start/QQ机器人指令速查.md) | QQ 群聊/私聊可用的所有指令 |

---

### ⚙️ [01-configuration/](01-configuration/) - 配置与故障排查

**配置文件说明和问题解决**，遇到问题时优先查看。

| 文档 | 用途 |
|------|------|
| [configuration.md](01-configuration/configuration.md) | **⭐ 配置文件完整说明**（主配置、子系统配置、优先级、环境变量） |
| [troubleshooting.md](01-configuration/troubleshooting.md) | **⭐ 故障排查指南**（启动失败、端口占用、连接问题、模型调用） |
| [scripts-and-config.md](01-configuration/scripts-and-config.md) | 根目录脚本和本地配置文件说明 |

---

### 🏗️ [02-architecture/](02-architecture/) - 架构与设计

**项目结构和技术架构**，深入理解项目设计。

| 文档 | 用途 |
|------|------|
| [project-overview.md](02-architecture/project-overview.md) | 项目整体目录、子系统职责和运行边界 |
| [project-deep-classification.md](02-architecture/project-deep-classification.md) | 项目目录深度分类、清理清单和保留边界 |
| [bridge-events.md](02-architecture/bridge-events.md) | bridge event 字段、接口和消费端协议 |
| [mcp-and-external-services.md](02-architecture/mcp-and-external-services.md) | MCP、Computer Use、Twitter、Minecraft 和外部服务权限 |

---

### 🔧 [03-subsystems/](03-subsystems/) - 子系统文档

**三大子系统的详细文档**，深入了解各模块。

#### xiaomiao - QQ 机器人

| 文档 | 用途 |
|------|------|
| [xiaomiao/README.md](03-subsystems/xiaomiao/README.md) | QQ 机器人架构、功能和实现 |
| [xiaomiao/deploy/README_DEPLOY.md](03-subsystems/xiaomiao/deploy/README_DEPLOY.md) | QQ 机器人部署打包文档 |

#### xiaomiaoAgent - 统一 Agent 框架

| 文档 | 用途 |
|------|------|
| [xiaomiaoAgent/README.md](03-subsystems/xiaomiaoAgent/README.md) | Agent 框架架构、API 和使用方式 |
| [xiaomiaoAgent/tools.md](03-subsystems/xiaomiaoAgent/tools.md) | Agent 工具目录、注册和风险分级 |

#### xiaomiaobot - Vtuber 表现层

| 文档 | 用途 |
|------|------|
| [xiaomiaobot/README.md](03-subsystems/xiaomiaobot/README.md) | 前端架构、技术栈和功能 |
| [xiaomiaobot/operation-guide.md](03-subsystems/xiaomiaobot/operation-guide.md) | 前端操作手册和使用说明 |
| [xiaomiaobot/services-and-plugins.md](03-subsystems/xiaomiaobot/services-and-plugins.md) | 服务和插件简表 |
| [xiaomiaobot/struct.md](03-subsystems/xiaomiaobot/struct.md) | 前端完整目录结构索引 |

---

### 👨‍💻 [04-development/](04-development/) - 开发与维护

**开发规范和测试验证**，贡献代码时必读。

| 文档 | 用途 |
|------|------|
| [development-maintenance.md](04-development/development-maintenance.md) | 开发、维护、验证和文档规则 |
| [testing-and-quality.md](04-development/testing-and-quality.md) | 测试目录职责和质量检查范围 |
| [verification.md](04-development/verification.md) | **⭐ 验证矩阵**（单测、前端测试、启动检查命令） |
| [file-workspace-hygiene.md](04-development/file-workspace-hygiene.md) | 文件和 workspace 管理规则 |

---

### 🛠️ [05-tools/](05-tools/) - 工具文档

**第三方工具和源码说明**。

| 文档 | 用途 |
|------|------|
| [tool-directory-analysis.md](05-tools/tool-directory-analysis.md) | tool/ 目录分析（markitdown 和 Scrapling） |

---

### 📋 [archive/](archive/) - 归档文档

**历史规划和报告**，项目演进记录。

| 目录 | 用途 |
|------|------|
| [archive/plans/](archive/plans/) | 历史开发计划和架构设计（6 个计划书） |
| [archive/reports/](archive/reports/) | 历史报告和分析文档（4 个报告） |

---

### 📖 [guide/](guide/) - 使用指南

**新手入门和配置指南**。

| 文档 | 用途 |
|------|------|
| [QUICK_START.md](guide/QUICK_START.md) | 快速开始指南 |
| [QQ_BOT_GUIDE.md](guide/QQ_BOT_GUIDE.md) | QQ Bot 使用指南 |
| [CONFIGURATION.md](guide/CONFIGURATION.md) | 配置说明 |

---

### 🎭 [live2d/](live2d/) - Live2D 相关

**Live2D 角色和模型文档**。

| 文档 | 用途 |
|------|------|
| [LIVE2D_CHARACTER_SWITCH.md](live2d/LIVE2D_CHARACTER_SWITCH.md) | Live2D 角色切换说明 |
| [LIVE2D_MODELS_LOCATION.md](live2d/LIVE2D_MODELS_LOCATION.md) | Live2D 模型位置说明 |
| [QQ_CHARACTER_SWITCH.md](live2d/QQ_CHARACTER_SWITCH.md) | QQ Bot 角色切换功能 |

---

### 📊 [report/](report/) - 测试报告

**功能测试和项目总结报告**。

| 文档 | 用途 |
|------|------|
| [FUNCTIONAL_TEST_REPORT_2026-06-13.md](report/FUNCTIONAL_TEST_REPORT_2026-06-13.md) | 功能测试报告 |
| [TEST_REPORT_2026-06-13.md](report/TEST_REPORT_2026-06-13.md) | 完整测试报告 |
| [PROJECT_FINAL_SUMMARY.md](report/PROJECT_FINAL_SUMMARY.md) | 项目最终总结 |

---

### 📝 [changelog/](changelog/) - 变更日志

**重大功能变更和移除记录**。

| 文档 | 用途 |
|------|------|
| [WEBUI_REMOVAL_CHANGELOG.md](changelog/WEBUI_REMOVAL_CHANGELOG.md) | WebUI 移除变更日志 |
| [WEBUI_REMOVAL_COMPLETE.md](changelog/WEBUI_REMOVAL_COMPLETE.md) | WebUI 移除完成报告 |
| [WEBUI_REMOVED.md](changelog/WEBUI_REMOVED.md) | WebUI 移除说明 |

---

### 🔧 [task/](task/) - 任务记录

**开发任务和问题分析**。

| 文档 | 用途 |
|------|------|
| [ELECTRON_ESM_ISSUE.md](task/ELECTRON_ESM_ISSUE.md) | ⚠️ Electron ESM 兼容性问题（未解决） |
| [LIVE2D_CHARACTER_VERIFICATION.md](task/LIVE2D_CHARACTER_VERIFICATION.md) | ✅ Live2D 角色验证报告（已完成） |

---

## 🗺️ 推荐阅读路径

### 新用户（第一次使用）

1. 📖 [00-quick-start/SETUP.md](00-quick-start/SETUP.md) - 环境配置（首次必读）
2. 📖 [00-quick-start/run-and-config.md](00-quick-start/run-and-config.md) - 完整启动指南
3. 📖 [00-quick-start/QQ机器人指令速查.md](00-quick-start/QQ机器人指令速查.md) - 了解指令
4. 📖 [guide/QQ_BOT_GUIDE.md](guide/QQ_BOT_GUIDE.md) - QQ Bot 详细指南
5. 📖 [01-configuration/configuration.md](01-configuration/configuration.md) - 理解配置

### 使用 Live2D 角色

1. 🎭 [live2d/LIVE2D_CHARACTER_SWITCH.md](live2d/LIVE2D_CHARACTER_SWITCH.md) - 角色切换方法
2. 🎭 [live2d/QQ_CHARACTER_SWITCH.md](live2d/QQ_CHARACTER_SWITCH.md) - QQ 中切换角色
3. 🎭 [task/LIVE2D_CHARACTER_VERIFICATION.md](task/LIVE2D_CHARACTER_VERIFICATION.md) - 角色验证报告

### 遇到问题时

1. 🔍 [troubleshooting.md](01-configuration/troubleshooting.md) - 故障排查
2. 🔍 [configuration.md](01-configuration/configuration.md) - 检查配置
3. 🔍 [task/ELECTRON_ESM_ISSUE.md](task/ELECTRON_ESM_ISSUE.md) - Electron 已知问题
4. 🔍 [verification.md](04-development/verification.md) - 运行验证测试

### 开发贡献者

1. 💻 [project-overview.md](02-architecture/project-overview.md) - 理解架构
2. 💻 [development-maintenance.md](04-development/development-maintenance.md) - 开发规范
3. 💻 [testing-and-quality.md](04-development/testing-and-quality.md) - 测试要求
4. 💻 [verification.md](04-development/verification.md) - 验证流程

### 查看项目历史

1. 📋 [archive/plans/](archive/plans/) - 历史开发计划
2. 📋 [archive/reports/](archive/reports/) - 历史报告
3. 📊 [report/PROJECT_FINAL_SUMMARY.md](report/PROJECT_FINAL_SUMMARY.md) - 项目最终总结

### 深入理解

1. 🏗️ [02-architecture/](02-architecture/) - 架构文档全部阅读
2. 🔧 [03-subsystems/](03-subsystems/) - 子系统详细文档
3. 📋 [archive/plans/](archive/plans/) - 项目演进历史

---

## 📚 其他重要文档

### 项目级文档
| 文档 | 位置 | 用途 |
|------|------|------|
| README.md | [../README.md](../README.md) | **项目根入口**和当前能力概览 |
| TECHNICAL.md | [../TECHNICAL.md](../TECHNICAL.md) | 技术结构、桥接协议、风险和演进路线 |

### 综合报告（2026-06-13 生成）
| 文档 | 用途 |
|------|------|
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | 📚 **文档总索引** - 一站式文档导航 |
| [DOCUMENTATION_TREE.md](DOCUMENTATION_TREE.md) | 🌳 **文档分类树** - 2336+ 文档完整分类 |
| [PROJECT_ARCHITECTURE_2026-06-13.md](PROJECT_ARCHITECTURE_2026-06-13.md) | 🏗️ **项目架构总览** - 含 Mermaid 架构图 |
| [TEST_COVERAGE_MATRIX.md](TEST_COVERAGE_MATRIX.md) | 🧪 **测试覆盖矩阵** - 955+ 测试文件分析 |
| [DEEP_ANALYSIS_SUMMARY_2026-06-13.md](DEEP_ANALYSIS_SUMMARY_2026-06-13.md) | 📊 **深度解析总结** - 完整执行报告 |

---

## 📊 文档覆盖状态

| 范围 | 状态 |
|------|------|
| ✅ 快速启动和配置 | 已覆盖（3 个文档） |
| ✅ 配置说明和故障排查 | 已覆盖（3 个文档） |
| ✅ 项目架构和设计 | 已覆盖（4 个文档） |
| ✅ 子系统详细文档 | 已覆盖（8 个文档） |
| ✅ 开发维护规范 | 已覆盖（4 个文档） |
| ✅ 工具和第三方源码 | 已覆盖（1 个文档） |
| ✅ 使用指南 | 已覆盖（3 个文档） |
| ✅ Live2D 角色 | 已覆盖（3 个文档） |
| ✅ 测试报告 | 已覆盖（3 个文档） |
| ✅ 变更日志 | 已覆盖（3 个文档） |
| ✅ 任务记录 | 已覆盖（2 个文档） |
| ✅ 历史归档 | 已覆盖（10 个文档） |

**总计**: 47 个文档，覆盖全面

---

## 🔄 文档更新

### 2026-06-14 更新
- ✅ 新增 `guide/` 目录 - 使用指南（3 个文档）
- ✅ 新增 `live2d/` 目录 - Live2D 相关（3 个文档）
- ✅ 新增 `report/` 目录 - 测试报告（3 个文档）
- ✅ 新增 `changelog/` 目录 - 变更日志（3 个文档）
- ✅ 新增 `task/` 目录 - 任务记录（2 个文档）
- ✅ 新增 `archive/` 目录 - 历史归档（10 个文档）

### 2026-06-12 更新
本文档中心进行了分类重组，采用数字前缀分类：

- `00-quick-start/` - 快速开始
- `01-configuration/` - 配置与故障排查
- `02-architecture/` - 架构与设计
- `03-subsystems/` - 子系统文档
- `04-development/` - 开发与维护
- `05-tools/` - 工具文档

所有文档链接已更新，旧链接会自动失效。
