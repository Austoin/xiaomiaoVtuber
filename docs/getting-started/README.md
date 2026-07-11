# xiaomiaoVirtual 快速开始

> 3 分钟快速启动 xiaomiaoVirtual

**📖 完整启动指南** → [run-and-config.md](../00-quick-start/run-and-config.md)

---

## 🚀 最快启动

### 方式一：一键启动（推荐）
```powershell
cd F:\xiaomiaoVirtual
pnpm run start:all
```
自动启动所有服务：QQ Bot + Agent API + Web 界面

### 方式二：TUI 终端（最快）
```powershell
cd F:\xiaomiaoVirtual
pnpm run tui
```
⚡ 1-2 秒启动，纯终端交互，完整工具能力

---

## 📋 首次使用

### 1. 环境准备
- ✅ Python 3.11+ (通过 conda)
- ✅ Node.js 18+ (可选，用于 Live2D)
- ✅ NapCat (可选，用于 QQ Bot)

**详细安装步骤** → [SETUP.md](../00-quick-start/SETUP.md)

### 2. 最小配置
```json
// F:\xiaomiaoVirtual\config.json
{
  "nanobot": {
    "provider": "custom",
    "model": "deepseek-v4-flash",
    "providers": {
      "custom": {
        "apiKey": "你的密钥",
        "baseUrl": "https://你的中转站/v1"
      }
    }
  }
}
```

**完整配置说明** → [configuration.md](../01-configuration/configuration.md)

---

## 💡 基本使用

### TUI 终端
```
启动后直接输入：
> 你好

退出：/exit 或 Ctrl+C
```

### QQ Bot
```
@小喵 你好
或：搜索最新新闻
```

**所有指令** → [QQ机器人指令速查.md](../00-quick-start/QQ机器人指令速查.md)

---

## 🔧 遇到问题？

**常见问题排查** → [troubleshooting.md](../01-configuration/troubleshooting.md)

快速检查：
```powershell
# 检查环境
conda activate xiaomiao
python --version  # 应该 3.11+

# 检查端口
netstat -ano | findstr "5004"  # NapCat
netstat -ano | findstr "8900"  # Agent API

# 检查配置
ls config.json
ls xiaomiao/config.json
```

---

## 📚 更多文档

### 使用指南
- 📖 [run-and-config.md](../00-quick-start/run-and-config.md) - **完整启动指南**
- 📖 [QQ Bot 指南](QQ_BOT_GUIDE.md) - QQ 使用和权限
- 📖 [配置说明](CONFIGURATION.md) - 详细配置

### 深入了解
- 🏗️ [项目架构](../02-architecture/project-overview.md) - 系统架构
- 🔧 [子系统文档](../03-subsystems/) - 三大子系统详解
- 💻 [开发指南](../04-development/development-maintenance.md) - 开发规范

---

**版本**: v1.1 | **更新**: 2026-06-24
