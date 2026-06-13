# xiaomiaoVirtual 文档总索引

> **最后更新**: 2026-06-13  
> **路径说明**: 文档中的相对路径均基于项目根目录

---

## 📚 快速导航

### 新用户入口
- ⭐ [运行与配置速查](00-quick-start/run-and-config.md) - 最快启动入口
- 📖 [详细启动指南](00-quick-start/STARTUP.md) - 手动启动各服务
- 🎮 [QQ 机器人指令速查](00-quick-start/QQ机器人指令速查.md) - QQ 命令参考

### 项目架构
- 📐 [项目覆盖图](02-architecture/project-overview.md) - **包含系统架构图**
- 🔧 [技术深度分类](02-architecture/project-deep-classification.md)
- 🌉 [桥接事件协议](02-architecture/bridge-events.md)

### 配置管理
- ⚙️ [统一配置说明](01-configuration/configuration.md)
- 🛠️ [脚本和配置详解](01-configuration/scripts-and-config.md)
- 🚨 [故障排查指南](01-configuration/troubleshooting.md) - 701行完整排错

### 开发维护
- 💻 [开发维护指南](04-development/development-maintenance.md)
- ✅ [测试和质量](04-development/testing-and-quality.md)
- 🔍 [验证矩阵](04-development/verification.md)
- 📁 [文件工作区规范](04-development/file-workspace-hygiene.md)

---

## 🎯 子系统文档

### xiaomiao - QQ 桥接服务

**集成文档** (xiaomiaoVirtual 专用):
- [xiaomiao 主文档](03-subsystems/xiaomiao/README.md) - 集成说明、启动命令
- [部署指南](03-subsystems/xiaomiao/deploy/README_DEPLOY.md)

**代码位置**: `xiaomiao/`

---

### xiaomiaoAgent - Agent 能力层

**集成文档** (xiaomiaoVirtual 专用):
- [xiaomiaoAgent 集成说明](03-subsystems/xiaomiaoAgent/README.md) - 启动方式、工具清单
- [工具注册表](03-subsystems/xiaomiaoAgent/tools.md) - xiaomiaoVirtual 工具配置

**完整文档** (nanobot 上游，16个文档):
- [📖 快速开始](../xiaomiaoAgent/docs/quick-start.md)
- [⚙️ 配置详解](../xiaomiaoAgent/docs/configuration.md)
- [🖥️ CLI 参考](../xiaomiaoAgent/docs/cli-reference.md)
- [💬 聊天命令](../xiaomiaoAgent/docs/chat-commands.md)
- [🌐 OpenAI 兼容 API](../xiaomiaoAgent/docs/openai-api.md)
- [🧠 记忆系统](../xiaomiaoAgent/docs/memory.md)
- [🐍 Python SDK](../xiaomiaoAgent/docs/python-sdk.md)
- [🚀 部署指南](../xiaomiaoAgent/docs/deployment.md)
- [🎨 图像生成](../xiaomiaoAgent/docs/image-generation.md)
- [🔌 通道插件开发](../xiaomiaoAgent/docs/channel-plugin-guide.md)
- [🔌 WebSocket 协议](../xiaomiaoAgent/docs/websocket.md)
- [🔧 MyTool 自定义工具](../xiaomiaoAgent/docs/my-tool.md)
- [🤖 Agent 社交网络](../xiaomiaoAgent/docs/agent-social-network.md)
- [📱 聊天应用集成](../xiaomiaoAgent/docs/chat-apps.md)
- [🔄 多实例运行](../xiaomiaoAgent/docs/multiple-instances.md)
- [📚 文档索引](../xiaomiaoAgent/docs/README.md)

**代码位置**: `xiaomiaoAgent/nanobot/`

---

### xiaomiaobot - Web/桌面/移动表现层

**集成文档** (xiaomiaoVirtual 专用):
- [xiaomiaobot 主文档](03-subsystems/xiaomiaobot/README.md) - 启动方式、联动配置
- [操作指南](03-subsystems/xiaomiaobot/operation-guide.md) - 运维操作
- [服务和插件](03-subsystems/xiaomiaobot/services-and-plugins.md) - 服务清单
- [目录结构](03-subsystems/xiaomiaobot/struct.md) - 完整目录索引

**完整文档** (AIRI 上游):
- [🤖 AGENTS 开发指南](../xiaomiaobot/AGENTS.md) - 详细技术栈和开发实践
- [📖 VitePress 文档站](../xiaomiaobot/docs/) - 多语言文档
  - 英文文档: `xiaomiaobot/docs/content/en/docs/`
  - 简体中文: `xiaomiaobot/docs/content/zh-Hans/docs/`
  - 日文文档: `xiaomiaobot/docs/content/ja/docs/`
- [🎨 UI 组件参考](../xiaomiaobot/docs/ai/context/ui-components.md)
- [🏗️ 服务器架构](../xiaomiaobot/apps/server/docs/ai-context/) - 8个详细架构文档

**代码位置**: 
- `xiaomiaobot/apps/` - 6个应用
- `xiaomiaobot/packages/` - 45个包

---

## 🧪 测试文档

### Python 测试
- **集成测试**: `test/xiaomiao/` (10个文件, 78 tests)
- **xiaomiaoAgent 单元测试**: `xiaomiaoAgent/tests/` (180个文件)
- **pytest 配置**: `pytest.ini`

### TypeScript 测试
- **xiaomiaobot 测试**: 分布在各 app/package (765个文件, 845 tests)
- **vitest 配置**: `xiaomiaobot/vitest.config.ts`

详见: [测试覆盖矩阵](TEST_COVERAGE_MATRIX.md)

---

## 🛠️ 工具和脚本

- [工具目录分析](05-tools/tool-directory-analysis.md) - tool/ 目录说明

---

## 📋 规划文档

- [规划索引](plans/README.md) - 历史计划和待推进功能
- 规划文档: `plans/2026-*.md`

---

## 🔗 外部服务集成

- [MCP 和外部服务](02-architecture/mcp-and-external-services.md) - MCP、Computer Use、Twitter 等

---

## 📊 项目报告

- [项目检查报告 2026-06-13](PROJECT_CHECK_REPORT_2026-06-13.md) - 最新检查结果
- [项目架构总览](PROJECT_ARCHITECTURE_2026-06-13.md) - 架构分析
- [文档分类树](DOCUMENTATION_TREE.md) - 完整文档分类
- [测试覆盖矩阵](TEST_COVERAGE_MATRIX.md) - 测试统计

---

## 🚀 相关资源

### 配置示例
- `config.example.json` - 主配置模板
- `xiaomiao/config.json` - QQ 配置（本地私有）
- `xiaomiaoAgent/.nanobot/config.json` - Agent 配置

### 启动脚本
- `start-all.cmd` - 一键启动所有服务
- `setup-env.cmd` - 环境配置和依赖安装

### 工作区
- `workspace/` - 下载文件、生成物、临时文件

---

## 📞 获取帮助

1. **快速问题**: 查看 [故障排查指南](01-configuration/troubleshooting.md)
2. **深入了解**: 浏览对应子系统的完整文档
3. **开发相关**: 参考 [开发维护指南](04-development/development-maintenance.md)

---

**文档维护规则**:
- 上游功能变更 → 更新子系统 docs/
- 集成配置变更 → 更新主 docs/03-subsystems/
- 新增子系统 → 在 docs/03-subsystems/ 新建目录
