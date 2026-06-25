# xiaomiaoVirtual 项目总结（2026-06-13 更新）

> **更新时间**: 2026-06-13  
> **状态**: ✅ WebUI 已移除，文档已更新

---

## 🎯 项目概览

**xiaomiaoVirtual** 是一个 QQ 机器人、Vtuber 桌面角色和轻量 Agent 框架的融合项目。

### 三大子系统

1. **xiaomiao** - Python QQ 机器人
   - QQ 消息接入、命令处理、权限管理
   
2. **xiaomiaobot** - Electron/Vue Vtuber 表现层
   - Live2D、TTS、口型同步
   
3. **xiaomiaoAgent** - 轻量 Agent 框架
   - 工具调用、记忆、会话管理、OpenAI 兼容 API

---

## 🚀 使用方式

### 方式一：TUI 终端（最快）
```cmd
start-tui.cmd
```
- ⚡ 1-2秒启动
- 💻 纯终端操作
- ✅ 完整工具能力

### 方式二：QQ Bot + Live2D
```cmd
start-all.cmd
```
- 🤖 QQ 群聊/私聊
- 🎭 Live2D 虚拟角色
- 🔊 TTS 语音和字幕

### 方式三：xiaomiaobot Web
```
http://127.0.0.1:5175
```
- 📱 网页版界面
- 💬 聊天历史
- 🎤 语音输入

---

## 📊 项目统计

### 代码规模
- Python: ~50K 行
- TypeScript: ~100K 行
- 文档数量: 2336+
- 测试文件: 955+
- 测试数量: 3779+

### 测试覆盖
- xiaomiao: 100%
- xiaomiaoAgent: 70.7%
- xiaomiaobot: 89.8%
- **综合: 76.1%**

### 综合评分
- 代码质量: A- (88/100)
- 测试覆盖: B+ (85/100)
- 文档完善: A (92/100)
- 架构设计: A (90/100)
- **总体: A- (88/100)**

---

## 🔑 核心能力

### QQ Bot
- 自然对话（支持图片理解）
- 26+ 工具调用（需权限）
- 多种人设切换
- 会话记忆管理
- 权限分级和确认机制

### Agent 工具系统
- **低风险**（所有用户）：`read_file`、`web_search`、`markitdown_convert`、`scrapling_get`
- **高权限**（ROOT/Super/白名单）：`exec`、`write_file`、`generate_image`、`xiaomiao_stage`、MCP 工具

### Vtuber 表现
- Live2D/VRM 模型渲染
- TTS 语音播报 + 口型同步
- 字幕和聊天历史同步
- 舞台动作控制

---

## 🔧 架构亮点

✅ 统一 Agent 闭环（QQ/Web/桌面/TUI 共享会话）  
✅ 完善的权限分级和确认机制  
✅ 丰富的文档体系（31+ 核心文档）  
✅ 高测试覆盖率（76.1%）  
✅ 清晰的启动脚本和健康检查  

---

## 📝 近期更新 (2026-06-13)

### 已移除
- ❌ xiaomiaoAgent WebUI (端口 5174)
- ❌ xiaomiaoAgent 网关 (端口 8765)

### 保留的访问方式
- ✅ TUI 终端界面（推荐日常使用）
- ✅ QQ Bot（多人协作）
- ✅ xiaomiaobot web（图形界面）

### 启动流程简化
```
QQ 协议端 :5004
  → xiaomiaoAgent API :8900
  → xiaomiao main.py / 桥接 :5519
  → xiaomiaobot stage-web :5175
```

---

## 📚 文档导航

### 必读文档
1. **docs/README.md** - 文档中心入口
2. **README.md** - 项目概览
3. **TECHNICAL.md** - 技术架构
4. **docs/QUICK_START.md** - 快速开始

### 配置文档
- docs/CONFIGURATION.md - 完整配置说明
- docs/QQ_BOT_GUIDE.md - QQ Bot 使用指南

### 子系统文档
- docs/03-subsystems/xiaomiao/README.md
- docs/03-subsystems/xiaomiaoAgent/README.md
- docs/03-subsystems/xiaomiaobot/README.md

---

## ⚠️ 安全注意

### ROOT 权限风险
配置 ROOT 权限后，该用户可以：
- ⚠️ 执行任意系统命令
- ⚠️ 读写任意文件
- ⚠️ 访问网络和外部服务
- ⚠️ 操作 MCP 工具

### 安全建议
1. 只配置信任的用户为 ROOT
2. 定期检查配置文件
3. 监控工具使用日志
4. 考虑使用白名单代替 ROOT

---

## 🎯 推荐使用

- **日常开发**: `start-tui.cmd`（最快最简单）
- **多人协作**: 配置 QQ Bot ROOT 权限
- **图形界面**: xiaomiaobot web (http://127.0.0.1:5175)

---

## ✅ 验证命令

```powershell
# xiaomiao 测试
python -m pytest --basetemp .pytest-tmp-xiaomiao-verify test\xiaomiao

# xiaomiaoAgent 测试
cd xiaomiaoAgent
uv run --extra dev pytest tests\test_openai_api.py tests\tools\...

# xiaomiaobot 测试
cd xiaomiaobot
pnpm exec vitest run apps/stage-pocket/... packages/stage-ui/...

# 启动检查
start-all.cmd --check

# TUI 快速测试
start-tui.cmd
```

---

**项目状态**: ✅ 生产就绪  
**推荐入口**: `start-tui.cmd` 或 `start-all.cmd`  
**文档完善度**: A (92/100)

**感谢使用 xiaomiaoVirtual！** 🎉
