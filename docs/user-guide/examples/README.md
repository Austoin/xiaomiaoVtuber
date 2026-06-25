# 示例文档

**版本**: v1.0  
**更新日期**: 2026-06-24

本目录包含 xiaomiaoVirtual 项目的各种使用示例，帮助用户快速上手常见场景。

---

## 📂 示例分类

### 配置示例
- [config-examples.md](config-examples.md) - 完整配置文件示例和说明
  - ✅ 最小配置
  - ✅ 完整配置
  - ✅ 开发/生产环境配置
  - ✅ 5 种常见配置场景
  - ✅ 配置优先级图
  - ✅ 配置验证和错误处理

### API 调用示例
- [agent-api-examples.md](agent-api-examples.md) - xiaomiaoAgent API 调用示例
  - ✅ Python 调用示例
  - ✅ JavaScript/TypeScript 调用示例
  - ✅ cURL 调用示例
  - ✅ 流式响应
  - ✅ 工具调用
  - ✅ 错误处理和重试

### 使用场景
- [qq-bot-scenarios.md](qq-bot-scenarios.md) - QQ Bot 典型使用场景
  - ✅ 15 个典型场景
  - ✅ 基础对话、信息查询
  - ✅ 文件处理、群管理
  - ✅ 工具调用、记忆管理
  - ✅ 权限管理、最佳实践

### MCP 工具示例（计划中）
- [mcp-tool-examples.md](mcp-tool-examples.md) - MCP 工具使用示例
  - ⏳ Computer Use 示例
  - ⏳ Twitter MCP 示例
  - ⏳ 自定义 MCP 服务器

---

## 🎯 如何使用示例

### 1. 选择适合的示例
- **新用户** → 从配置示例开始
- **API 开发者** → 查看 API 调用示例
- **QQ Bot 用户** → 查看使用场景示例

### 2. 复制和修改
所有示例都可以直接复制使用，只需修改：
- API Keys
- QQ 号
- 服务地址
- 个性化配置

### 3. 验证和测试
使用示例后，运行验证命令确保配置正确：
```powershell
start-all.cmd --check
```

---

## 📊 示例统计

| 类型 | 文档 | 示例数量 | 状态 |
|------|------|---------|------|
| 配置示例 | config-examples.md | 5 个场景 | ✅ 完成 |
| API 调用 | agent-api-examples.md | 10+ 示例 | ✅ 完成 |
| QQ Bot 场景 | qq-bot-scenarios.md | 15 个场景 | ✅ 完成 |
| MCP 工具 | mcp-tool-examples.md | - | ⏳ 计划中 |

**总计**: 3 个文档，30+ 个示例

---

## 🔗 快速导航

### 配置相关
- 📖 [最小配置](config-examples.md#最小配置) - 快速开始
- 📖 [完整配置](config-examples.md#完整配置) - 所有选项
- 📖 [场景配置](config-examples.md#常见配置场景) - 实际应用

### API 调用
- 💻 [Python 示例](agent-api-examples.md#python-调用示例)
- 💻 [JavaScript 示例](agent-api-examples.md#javascripttypescript-调用示例)
- 💻 [流式响应](agent-api-examples.md#流式响应)

### QQ Bot
- 🤖 [基础对话](qq-bot-scenarios.md#基础对话场景)
- 🤖 [文件处理](qq-bot-scenarios.md#文件处理场景)
- 🤖 [工具调用](qq-bot-scenarios.md#工具调用场景)

---

## 📚 相关文档

- [配置说明](../guide/CONFIGURATION.md) - 详细配置文档
- [快速启动](../00-quick-start/run-and-config.md) - 启动指南
- [故障排查](../01-configuration/troubleshooting.md) - 问题解决

---

**需要更多示例？** 欢迎在项目仓库提 Issue 或 PR。

**文档完成度**: 🟢 75% (3/4 已完成)
