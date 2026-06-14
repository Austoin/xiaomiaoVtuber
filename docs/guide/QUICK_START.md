# xiaomiaoVirtual 快速开始

> 3 分钟快速启动 xiaomiaoVirtual

---

## 🚀 快速启动

### 方式一：TUI 终端（最快）
```cmd
cd f:\xiaomiaoVirtual
start-tui.cmd
```
- ⚡ 启动最快（1-2秒）
- 💻 纯终端操作
- ✅ 完整工具能力

### 方式二：QQ Bot + Live2D
```cmd
cd f:\xiaomiaoVirtual
start-all.cmd
```
- 🤖 QQ 群聊/私聊
- 🎭 Live2D 虚拟角色
- 🔊 TTS 语音和字幕

---

## 📋 前置要求

### 必需
- Python 3.11+（通过 conda）
- Node.js 18+（如果使用 Live2D）

### 可选
- NapCat（QQ Bot）
- API Keys（LLM 提供商）

---

## ⚙️ 环境配置

### 1. 首次配置
```cmd
setup-env.cmd
```
自动安装：
- xiaomiao（QQ Bot）
- xiaomiaoAgent（Agent 核心）
- xiaomiaobot（前端，可选）

### 2. 配置文件

#### 主配置（f:\xiaomiaoVirtual\config.json）
```json
{
  "xiaomiao_agent": {
    "enabled": true,
    "base_url": "http://127.0.0.1:8900/v1/chat/completions"
  },
  "xiaomiaoAgent": {
    "model": "deepseek-v4-flash",
    "provider": "custom"
  }
}
```

#### QQ Bot 配置（xiaomiao\config.json）
```json
{
  "ROOT": "你的QQ号",
  "Super": [],
  "agent_tool_allowlist": []
}
```

---

## 💡 基本使用

### TUI 终端
```
启动后直接输入消息：
> 你好

退出：
- 输入 /exit
- 按 Ctrl+C
```

### QQ Bot
```
在 QQ 中发送：
@小喵 你好

或使用命令前缀：
- 搜索最新新闻
```

---

## 🔧 常见问题

### Q: 启动失败？
**A**: 检查 conda 环境
```cmd
conda activate xiaomiao
python --version  # 应该是 3.11+
```

### Q: QQ Bot 没反应？
**A**: 检查 NapCat 是否运行
```
查看端口：netstat -ano | findstr "5003"
```

### Q: 没有工具权限？
**A**: 配置 ROOT 权限
```json
// xiaomiao/config.json
{
  "ROOT": "你的QQ号"
}
```

---

## 📚 进阶文档

- [配置说明](CONFIGURATION.md) - 详细配置指南
- [QQ Bot 指南](QQ_BOT_GUIDE.md) - QQ 使用和权限
- [故障排查](TROUBLESHOOTING.md) - 问题解决
- [项目架构](ARCHITECTURE.md) - 技术架构
