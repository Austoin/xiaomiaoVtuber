# xiaomiaoVirtual 快速启动指南

**版本**: v1.0  
**更新日期**: 2026-06-24  
**适用对象**: 新用户、初次使用者

---

## 📖 文档说明

这是 xiaomiaoVirtual 的**主快速启动文档**，包含完整的启动流程和配置说明。

**其他相关文档**：
- [SETUP.md](SETUP.md) - 环境配置和依赖安装（首次使用必读）
- [STARTUP.md](../guide/QUICK_START.md) - 3 分钟快速上手版
- [故障排查](../01-configuration/troubleshooting.md) - 遇到问题时查阅

---

## 🚀 最快启动方式

### 方式一：一键启动所有服务（推荐）

```powershell
cd F:\xiaomiaoVirtual
pnpm run start:all
```

**自动启动**：
- ✅ QQ 协议端 (NapCat) - 端口 5004
- ✅ xiaomiaoAgent API - 端口 8900
- ✅ xiaomiao 桌面桥接 - 端口 5519
- ✅ xiaomiaobot Web 界面 - 端口 5175

**特点**：
- 串行启动，自动健康检查
- QQ 登录窗口保持可见
- 其他服务窗口默认最小化
- 服务启动失败会自动停止

**仅检查不启动**：
```powershell
pnpm run start:check
```

### 方式二：TUI 终端（最快，无需 QQ）

```powershell
cd F:\xiaomiaoVirtual
pnpm run tui
```

**特点**：
- ⚡ 1-2 秒启动
- 💻 纯终端交互
- ✅ 完整 Agent 工具能力
- 🔧 适合测试和调试

---

## 📋 前置要求

### 首次使用必读

**如果是第一次使用，请先阅读** [SETUP.md](SETUP.md) 完成以下准备：

1. ✅ 安装 Python 3.11+ (通过 conda)
2. ✅ 安装 Node.js 18+ (如果使用 Live2D)
3. ✅ 下载 NapCat (如果使用 QQ Bot)
4. ✅ 配置 API Keys
5. ✅ 安装项目依赖

### 快速检查清单

```powershell
# 检查 Python 环境
conda activate xiaomiao
python --version  # 应该显示 3.11+

# 检查 Node.js 环境（可选）
node --version    # 应该显示 18+
pnpm --version    # 应该已安装

# 检查关键配置文件
ls config.json                    # 主配置
ls xiaomiao/config.json          # QQ Bot 配置
ls xiaomiaoAgent/.nanobot/config.json  # Agent 配置
```

---

## ⚙️ 配置文件说明

### 1. 主配置文件 (F:\xiaomiaoVirtual\config.json)

**最小配置示例**：

```json
{
  "nanobot": {
    "provider": "custom",
    "model": "deepseek-v4-flash",
    "providers": {
      "custom": {
        "apiKey": "你的中转站密钥",
        "baseUrl": "https://你的中转站地址/v1"
      }
    }
  },
  "nanobot_agent": {
    "enabled": true,
    "base_url": "http://127.0.0.1:8900/v1/chat/completions",
    "model": "",
    "session_id": "xiaomiao-unified",
    "timeout_seconds": 30
  }
}
```

**配置说明**：
- `nanobot.model` - 使用的模型名称（必填）
- `nanobot.provider` - 提供方类型，使用 `custom` 表示自定义中转站
- `nanobot.providers.custom.baseUrl` - 中转站地址，填到 `/v1` 即可
- `nanobot_agent.base_url` - xiaomiaoAgent API 地址（本机 8900 端口）

**详细配置说明** → [configuration.md](../01-configuration/configuration.md)

### 2. QQ Bot 配置 (xiaomiao/config.json)

**权限配置示例**：

```json
{
  "ROOT": "你的QQ号",
  "Super": [],
  "agent_tool_allowlist": [],
  "onebot": {
    "ws_url": "ws://127.0.0.1:5004"
  }
}
```

**权限说明**：
- `ROOT` - 最高权限，可使用所有工具（需要确认）
- `Super` - 超级用户列表
- `agent_tool_allowlist` - 允许使用高风险工具的用户列表
- 普通用户 - 只能使用低风险工具

**详细 QQ Bot 配置** → [QQ_BOT_GUIDE.md](../guide/QQ_BOT_GUIDE.md)

---

## 🔧 手动启动（分步骤）

如果一键启动失败，可以按以下步骤手动启动各个服务。

### 步骤 1: 启动 xiaomiaoAgent API

**必需**，所有服务都依赖这个 API。

```powershell
cd F:\xiaomiaoVirtual
conda activate xiaomiao
python -m xiaomiao_agent serve --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

**验证**：
- 看到 "Uvicorn running on http://127.0.0.1:8900"
- 访问 http://127.0.0.1:8900/health 应该返回 200

**常见问题**：
- 端口 8900 被占用 → 检查是否已有实例在运行
- 配置文件找不到 → 检查路径是否正确
- API Key 无效 → 检查 config.json 中的配置

### 步骤 2: 启动 QQ Bot / xiaomiao bridge

**可选**，如果不使用 QQ Bot 可以跳过。

```powershell
cd F:\xiaomiaoVirtual\xiaomiao
conda activate xiaomiao
python main.py
```

**前置条件**：
- NapCat 已启动并监听 5004 端口
- xiaomiaoAgent API 已启动 (8900)

**验证**：
- 看到 "OneBot WebSocket 连接成功"
- 看到 "桌面桥接服务启动在 http://127.0.0.1:5519"
- QQ Bot 在群里有响应

**常见问题**：
- 连接不上 NapCat → 检查 NapCat 是否运行
- 端口 5519 被占用 → 关闭旧进程
- QQ Bot 没反应 → 检查 ROOT 权限配置

### 步骤 3: 启动 xiaomiaobot Web 界面

**可选**，如果只用 QQ Bot 可以跳过。

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot
pnpm install  # 首次需要安装依赖
cd apps\stage-web
pnpm exec vite --host 127.0.0.1 --port 5175
```

**验证**：
- 看到 "Local: http://127.0.0.1:5175"
- 浏览器访问能看到 Live2D 角色
- 输入文字能得到回复

**常见问题**：
- 依赖安装失败 → 检查 Node.js 版本
- Live2D 模型加载失败 → 等待自动下载
- 无法连接桥接服务 → 检查 xiaomiao bridge 是否启动

### 步骤 4: 启动 Electron 桌面端（可选）

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot
pnpm dev:tamagotchi
```

**特点**：
- 独立桌面窗口
- TTS 语音播报
- Live2D 口型同步
- 字幕显示

---

## 💡 基本使用

### TUI 终端模式

启动后直接输入消息：

```
> 你好
小喵：你好！有什么可以帮你的吗？

> 帮我搜索一下最新新闻
小喵：好的，我来帮你搜索...
```

**退出方式**：
- 输入 `/exit`
- 按 `Ctrl+C`

### QQ Bot 模式

在 QQ 群或私聊中：

**@ 方式**：
```
@小喵 你好
```

**命令前缀**（无需 @）：
```
搜索最新新闻
帮助
关于
```

**完整指令列表** → [QQ机器人指令速查.md](QQ机器人指令速查.md)

### Web 界面模式

1. 访问 http://127.0.0.1:5175
2. 在输入框输入文字或点击麦克风录音
3. Live2D 角色会回复并播放语音
4. 聊天历史会自动保存

---

## 🔍 常见问题排查

### Q1: pnpm run start:all 启动失败

**症状**：脚本停止，后续服务未启动

**排查步骤**：
1. 查看脚本输出，找到失败的服务
2. 检查该服务的端口是否被占用
3. 手动启动该服务，查看详细错误信息

**常见原因**：
- 端口被占用 → `netstat -ano | findstr "端口号"` 查找进程
- 配置文件缺失 → 检查 config.json 是否存在
- NapCat 未启动 → 先手动启动 NapCat

### Q2: QQ Bot 没反应

**排查步骤**：
1. 检查 NapCat 是否运行
   ```powershell
   netstat -ano | findstr "5004"
   ```

2. 检查 xiaomiao 是否连接成功
   ```
   # 查看 xiaomiao 日志，应该有：
   OneBot WebSocket 连接成功
   ```

3. 检查权限配置
   ```json
   // xiaomiao/config.json
   {
     "ROOT": "你的QQ号"  // 确保填写正确
   }
   ```

4. 测试简单命令
   ```
   @小喵 帮助
   ```

### Q3: Agent 工具没有权限

**症状**：QQ Bot 回复"需要更高权限"或"工具调用被拒绝"

**解决方案**：

在 `xiaomiao/config.json` 中添加你的 QQ 号：

```json
{
  "ROOT": "你的QQ号",
  "agent_tool_allowlist": ["另一个QQ号"]
}
```

重启 xiaomiao 生效。

### Q4: xiaomiaoAgent API 调用失败

**症状**：Web 界面或 QQ Bot 无法获得回复

**排查步骤**：
1. 检查 API 是否运行
   ```powershell
   curl http://127.0.0.1:8900/health
   ```

2. 检查配置文件中的 API Key
   ```json
   // config.json
   {
     "nanobot": {
       "providers": {
         "custom": {
           "apiKey": "检查是否有效"
         }
       }
     }
   }
   ```

3. 查看 xiaomiaoAgent 日志，寻找错误信息

### Q5: Live2D 模型加载失败

**症状**：Web 界面显示"模型加载失败"或白屏

**解决方案**：
1. 等待自动下载（首次运行需要下载模型）
2. 检查网络连接
3. 清理缓存重试
   ```powershell
   rm -rf xiaomiaobot/.cache
   cd xiaomiaobot/apps/stage-web
   pnpm exec vite --host 127.0.0.1 --port 5175
   ```

**更多问题** → [troubleshooting.md](../01-configuration/troubleshooting.md)

---

## 📊 服务端口一览

| 服务 | 端口 | 说明 |
|------|------|------|
| NapCat OneBot | 5004 | QQ 协议端 WebSocket |
| xiaomiaoAgent API | 8900 | Agent 统一 API |
| xiaomiao bridge | 5519 | 桌面桥接服务 |
| xiaomiaobot Web | 5175 | Web 界面 |

**检查端口占用**：
```powershell
netstat -ano | findstr "端口号"
```

---

## 🎯 下一步

### 基础使用
- 📖 [QQ机器人指令速查.md](QQ机器人指令速查.md) - 学习所有 QQ 指令
- 📖 [QQ_BOT_GUIDE.md](../guide/QQ_BOT_GUIDE.md) - 深入了解 QQ Bot

### 自定义配置
- ⚙️ [configuration.md](../01-configuration/configuration.md) - 详细配置说明
- ⚙️ [troubleshooting.md](../01-configuration/troubleshooting.md) - 故障排查

### 深入了解
- 🏗️ [project-overview.md](../02-architecture/project-overview.md) - 项目架构
- 🏗️ [../TECHNICAL.md](../../TECHNICAL.md) - 技术细节

### 开发贡献
- 💻 [development-maintenance.md](../04-development/development-maintenance.md) - 开发规范
- 💻 [verification.md](../04-development/verification.md) - 测试验证

---

## 🔄 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-24 | 初始版本，整合快速启动文档 |

---

**有问题？** 查看 [故障排查文档](../01-configuration/troubleshooting.md) 或在项目仓库提 Issue。
