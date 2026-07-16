# QQ Bot 使用指南

> xiaomiao QQ Bot 完整使用手册

---

## 🎯 核心功能

- 🤖 自然对话（支持图片理解）
- 🔧 26+ 工具调用（需权限）
- 🎭 多种人设切换
- 💾 会话记忆管理
- 🎨 Live2D 虚拟角色（可选）

---

## ⚙️ 权限配置

### 权限等级

#### 1. ROOT（最高权限）
```json
// xiaomiao/config.json
{
  "ROOT": "你的QQ号"
}
```
- ✅ 所有 26+ 工具
- ✅ Shell 命令执行
- ✅ 文件读写
- ✅ MCP 工具

#### 2. Super（管理员）
```json
{
  "ROOT": "主管理员",
  "Super": ["副管理员1", "副管理员2"]
}
```
- ✅ 与 ROOT 相同权限
- 💡 适合多人管理

#### 3. 白名单（开发者）
```json
{
  "agent_tool_allowlist": ["开发者QQ号"]
}
```
- ✅ 所有工具权限
- 💡 适合开发测试

#### 4. 普通用户
- ⚠️ 仅 9 个低风险工具
- ❌ 不能执行命令
- ❌ 不能写文件

---

## 🔧 工具能力

### 低风险工具（所有用户）
```
✅ read_file        - 读取文件
✅ list_dir         - 列出目录
✅ grep             - 文本搜索
✅ glob             - 文件匹配
✅ web_search       - Web 搜索
✅ web_fetch        - 抓取网页
✅ markitdown       - 文档转换
✅ scrapling_get    - 网页抓取
✅ xiaomiaobot_status - 服务状态
```

### 高权限工具（ROOT/Super/白名单）
```
✅ exec             - Shell 命令
✅ write_file       - 写入文件
✅ edit_file        - 编辑文件
✅ generate_image   - 生成图片
✅ xiaomiao_stage   - 舞台控制（TTS/字幕）
✅ cron             - 定时任务
✅ spawn            - 启动子 Agent
✅ message          - 发送消息
✅ MCP 工具         - 外部工具集成
```

---

## 💬 基本使用

### 触发方式
```
# 方式 1: @ 机器人
@小喵 你好

# 方式 2: 命令前缀（配置中的 reminder）
- 你好

# 方式 3: 私聊
直接发送消息
```

### 常用命令
```
# 搜索
- 搜索最新 AI 新闻

# 文件操作（需权限）
- 读取 README.md 的内容
- 创建文件 test.txt，内容是 "Hello"

# Shell 命令（需权限）
- 执行命令 dir
- 执行命令 git status

# 记忆管理
记忆状态             # 查看记忆状态
整理记忆             # 整理记忆
恢复记忆             # 恢复记忆
```

---

## 🎭 人设切换

### 配置人设（xiaomiao/config.json）
```json
{
  "Others": {
    "personas": {
      "senior_programmer": "高级程序员人设...",
      "girl_friend": "女朋友人设...",
      "sister": "姐姐人设...",
      "mother": "妈妈人设..."
    }
  }
}
```

### 人设自动匹配
- 默认：高级程序员
- 特定用户：其他人设（配置中指定）

---

## 🎨 Live2D 集成

### 舞台功能（需 ROOT 权限）
```
- 播放 TTS "你好"
- 显示字幕 "欢迎"
- 切换 Live2D 模型
```

### 舞台事件
- TTS 语音播放
- 字幕同步显示
- 模型表情控制
- 背景切换

---

## 📊 权限对比

| 功能 | 普通用户 | ROOT/Super/白名单 |
|------|----------|------------------|
| 对话 | ✅ | ✅ |
| 搜索 | ✅ | ✅ |
| 读文件 | ✅ | ✅ |
| 写文件 | ❌ | ✅ |
| Shell命令 | ❌ | ✅ |
| 生成图片 | ❌ | ✅ |
| 舞台控制 | ❌ | ✅ |
| MCP工具 | ❌ | ✅ |

---

## ⚠️ 安全建议

### ROOT 权限风险
- ⚠️ 可执行任意系统命令
- ⚠️ 可读写任意文件
- ⚠️ 可访问网络和外部服务

### 安全措施
1. ✅ 只配置信任的 QQ 号为 ROOT
2. ✅ 定期检查配置文件
3. ✅ 监控工具使用日志
4. ✅ 使用白名单而非 ROOT（如果只需工具权限）

---

## 🔧 配置示例

### 单人使用
```json
{
  "ROOT": "你的QQ号",
  "Super": [],
  "agent_tool_allowlist": []
}
```

### 多人协作
```json
{
  "ROOT": "主管理员",
  "Super": ["副管理1", "副管理2"],
  "agent_tool_allowlist": ["开发者1", "开发者2"]
}
```

### 测试环境
```json
{
  "ROOT": "",
  "Super": [],
  "agent_tool_allowlist": ["测试QQ号"]
}
```

---

## 📚 相关文档

- [快速开始](../../guide/QUICK_START.md) - 启动和基本配置
- [配置说明](../../guide/CONFIGURATION.md) - 详细配置选项
