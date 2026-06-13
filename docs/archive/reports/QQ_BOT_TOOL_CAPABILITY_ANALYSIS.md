# QQ Bot 工具能力完整分析与改造方案

> **分析日期**: 2026-06-13  
> **目标**: 确认 QQ Bot 是否能调用 TUI 的所有工具，并完成权限改造

---

## 📊 工具能力对比总览

### 核心发现
✅ **QQ Bot 和 TUI 使用同一套工具系统**  
✅ **区别只在权限策略（tool_policy）**  
✅ **所有工具都可以被 QQ Bot 调用（如果有权限）**

---

## 🔧 xiaomiaoAgent 工具系统架构

### 统一工具层
```
xiaomiaoAgent/nanobot/agent/tools/
├── loader.py          # 扫描和加载所有工具
├── registry.py        # 工具注册表、权限过滤
├── base.py            # 工具基类
├── filesystem.py      # 文件操作工具
├── search.py          # 搜索工具
├── web.py             # Web 工具
├── shell.py           # Shell 执行
├── mcp.py             # MCP 工具包装
└── ...                # 其他工具
```

### 权限策略系统
```python
# 两种策略
LOW_RISK_TOOL_POLICY = "low_risk"              # 普通用户
TRUSTED_CONFIRMED_TOOL_POLICY = "trusted_confirmed"  # 高权限用户

# 工具过滤
ToolRegistry.get_definitions(tool_policy)  # 根据策略返回可见工具
ToolRegistry.prepare_call(tool_policy)     # 根据策略拦截执行
```

---

## 📋 完整工具清单对比

### 1. 低风险工具（普通 QQ 用户可用）

| 工具 | TUI | QQ Bot | 说明 |
|------|-----|--------|------|
| `read_file` | ✅ | ✅ | 读取工作区文件 |
| `list_dir` | ✅ | ✅ | 列出目录 |
| `grep` | ✅ | ✅ | 文本搜索 |
| `glob` | ✅ | ✅ | 文件名匹配 |
| `web_search` | ✅ | ✅ | Web 搜索（Brave/DuckDuckGo/Tavily） |
| `web_fetch` | ✅ | ✅ | 抓取公网 URL |
| `markitdown_convert` | ✅ | ✅ | 文档转 Markdown |
| `scrapling_get` | ✅ | ✅ | 网页正文抽取 |
| `xiaomiaobot_status` | ✅ | ✅ | 查询服务状态 |

**结论**: ✅ 普通 QQ 用户可以使用所有低风险工具

---

### 2. 高权限工具（需要特殊权限）

| 工具 | TUI | QQ Bot (普通) | QQ Bot (ROOT/Super) |
|------|-----|---------------|---------------------|
| `exec` | ✅ | ❌ | ✅ |
| `write_file` | ✅ | ❌ | ✅ |
| `edit_file` | ✅ | ❌ | ✅ |
| `notebook_edit` | ✅ | ❌ | ✅ |
| `cron` | ✅ | ❌ | ✅ |
| `spawn` | ✅ | ❌ | ✅ |
| `message` | ✅ | ❌ | ✅ |
| `generate_image` | ✅ | ❌ | ✅ |
| `xiaomiao_stage` | ✅ | ❌ | ✅ |
| `xiaomiaobot_action` | ✅ | ❌ | ✅ |
| MCP 工具（非只读） | ✅ | ❌ | ✅ |

**结论**: 
- ❌ 普通 QQ 用户**不能**使用高风险工具
- ✅ ROOT/Super/白名单用户**可以**使用所有工具

---

## 🔐 权限分级详解

### 三种用户角色

#### 1. ROOT 用户
```json
// config.json
{
  "ROOT": "你的QQ号"
}
```
- ✅ 完全权限
- ✅ 所有工具可见可执行
- ✅ `tool_policy = trusted_confirmed`

#### 2. Super 用户
```json
// config.json
{
  "Super": ["QQ号1", "QQ号2"]
}
```
- ✅ 高级权限
- ✅ 所有工具可见可执行
- ✅ `tool_policy = trusted_confirmed`

#### 3. Agent 工具白名单用户
```json
// config.json
{
  "agent_tool_allowlist": ["QQ号3", "QQ号4"]
}
```
- ✅ 工具权限
- ✅ 所有工具可见可执行
- ✅ `tool_policy = trusted_confirmed`

#### 4. 普通用户
- ⚠️ 受限权限
- ⚠️ 只能使用低风险工具
- ⚠️ `tool_policy = low_risk`

---

## 🎯 权限链路完整流程

```
1. QQ 消息发送
   ↓
2. xiaomiao/qq_permissions.py
   检查用户角色：
   - is_root(user_id) → ROOT
   - is_super(user_id) → Super
   - has_agent_tool_permission(user_id) → 白名单
   - 否则 → 普通用户
   ↓
3. xiaomiao/qq_agent_tools.py
   决定 tool_policy：
   - 有权限 → trusted_confirmed
   - 无权限 → low_risk
   ↓
4. xiaomiao/agent_backend.py
   构建请求，传递 tool_policy：
   {
     "messages": [...],
     "tool_policy": "trusted_confirmed" 或 "low_risk",
     "session_id": "xiaomiao-unified",
     "channel": "qq-group",
     "chat_id": "群号",
     "user_id": "用户QQ号"
   }
   ↓
5. xiaomiaoAgent API (server.py)
   接收请求，设置上下文：
   RequestContext.metadata.channel_policy = tool_policy
   ↓
6. ToolRegistry
   过滤工具：
   - low_risk → 只返回低风险工具
   - trusted_confirmed → 返回所有工具
   ↓
7. Agent 看到可用工具列表
   ↓
8. Agent 调用工具
   ↓
9. ToolRegistry.prepare_call()
   再次检查权限：
   - low_risk 用户调用高风险工具 → 拦截
   - trusted_confirmed 用户 → 允许
   ↓
10. 工具执行并返回结果
```

---

## ✅ 完整改造方案

### 目标
让**你的 QQ 号**可以像 TUI 一样使用所有工具。

### 步骤 1: 配置 ROOT 权限

编辑 `xiaomiao/config.json`：

```json
{
  "ROOT": "你的QQ号",
  "Super": [],
  "agent_tool_allowlist": [],
  "Others": {
    // ... 其他配置
  }
}
```

**重要**: 替换 `"你的QQ号"` 为实际的 QQ 号码（纯数字）

---

### 步骤 2: 验证配置

重启 QQ Bot 服务：
```cmd
# 停止现有服务（如果在运行）
# 按 Ctrl+C 或关闭窗口

# 重新启动
cd f:\xiaomiaoVirtual
start-all.cmd
```

---

### 步骤 3: 测试工具权限

在 QQ 中发送测试消息：

#### 测试低风险工具
```
- 搜索最新 AI 新闻
```
应该看到 Agent 调用 `web_search` 工具。

#### 测试高权限工具
```
- 帮我在工作区创建一个测试文件 test.txt，内容是 "Hello World"
```
应该看到 Agent 调用 `write_file` 工具。

#### 测试 Shell 命令
```
- 执行命令 dir 列出当前目录
```
应该看到 Agent 调用 `exec` 工具。

---

### 步骤 4: 检查权限生效

查看 xiaomiao 日志，应该看到：
```
[INFO] User 你的QQ号 is ROOT
[INFO] tool_policy: trusted_confirmed
```

---

## 📊 改造前后对比

### 改造前（普通用户）
```
可用工具数: 9 个
- read_file
- list_dir  
- grep
- glob
- web_search
- web_fetch
- markitdown_convert
- scrapling_get
- xiaomiaobot_status

❌ 不能执行 shell 命令
❌ 不能写文件
❌ 不能编辑文件
❌ 不能调用 MCP 工具
```

### 改造后（ROOT 用户）
```
可用工具数: 26+ 个
+ 所有低风险工具（9个）
+ exec (shell 命令)
+ write_file
+ edit_file
+ notebook_edit
+ cron
+ spawn
+ message
+ generate_image
+ xiaomiao_stage
+ xiaomiaobot_action
+ 所有 MCP 工具

✅ 完全等同于 TUI 的工具能力
```

---

## 🔍 验证工具可见性

### 方法 1: 询问 Agent
在 QQ 中问：
```
你现在可以使用哪些工具？列出所有工具名称。
```

期望看到包括 `exec`、`write_file`、`edit_file` 等高权限工具。

### 方法 2: 查看日志
启动 QQ Bot 时查看日志：
```
[INFO] Loaded 26 tools
[INFO] User policy: trusted_confirmed
```

### 方法 3: 测试实际执行
尝试让 Agent 执行高权限操作：
```
帮我创建文件 test.txt
```

如果成功执行，说明权限配置正确。

---

## ⚠️ 安全注意事项

### ROOT 权限的风险
配置 ROOT 后，该 QQ 号可以：
- ✅ 执行任意 shell 命令
- ✅ 读写任意文件
- ✅ 调用外部服务（MCP）
- ✅ 操作系统和网络

### 安全建议
1. **不要泄露 ROOT QQ 号**
2. **定期检查 config.json** 确保只有你自己是 ROOT
3. **使用白名单而非 ROOT** 如果只需要工具权限：
   ```json
   {
     "ROOT": "",
     "agent_tool_allowlist": ["你的QQ号"]
   }
   ```
4. **监控工具使用日志**
5. **在测试环境先验证**

---

## 🎯 其他配置选项

### 选项 1: 使用 Super 权限
```json
{
  "ROOT": "主管理员QQ",
  "Super": ["你的QQ号", "其他信任用户"],
  "agent_tool_allowlist": []
}
```

### 选项 2: 只给工具权限
```json
{
  "ROOT": "主管理员QQ",
  "Super": [],
  "agent_tool_allowlist": ["你的QQ号"]
}
```

### 选项 3: 多人协作
```json
{
  "ROOT": "主管理员QQ",
  "Super": ["副管理员1", "副管理员2"],
  "agent_tool_allowlist": ["开发者1", "开发者2", "测试员"]
}
```

---

## 📝 配置文件完整示例

```json
{
  "ROOT": "123456789",
  "Super": ["987654321"],
  "agent_tool_allowlist": ["111222333", "444555666"],
  "reminder": "- ",
  "Others": {
    "xiaomiao_agent": {
      "enabled": true,
      "base_url": "http://127.0.0.1:8900/v1/chat/completions",
      "session_id": "xiaomiao-unified",
      "timeout_seconds": 0
    },
    "personas": {
      "senior_programmer": "你是高级程序员..."
    }
  }
}
```

---

## ✅ 验证清单

改造完成后，逐项验证：

- [ ] 修改了 `xiaomiao/config.json` 的 ROOT 配置
- [ ] 重启了 QQ Bot 服务
- [ ] 在 QQ 中测试低风险工具（搜索）
- [ ] 在 QQ 中测试高权限工具（写文件）
- [ ] 在 QQ 中测试 Shell 命令（exec）
- [ ] 查看日志确认 `tool_policy: trusted_confirmed`
- [ ] 询问 Agent 确认可见所有工具
- [ ] 所有测试通过

---

## 🎓 总结

### 核心结论
✅ **QQ Bot 和 TUI 使用完全相同的工具系统**  
✅ **只需配置 ROOT 权限即可获得所有工具能力**  
✅ **无需修改代码，只需修改配置文件**

### 改造步骤
1. 编辑 `xiaomiao/config.json`
2. 设置 `"ROOT": "你的QQ号"`
3. 重启 QQ Bot
4. 验证工具可用性

### 最终效果
**QQ Bot (ROOT 用户) = TUI = 完全工具能力**

---

**配置文件位置**: `xiaomiao/config.json`  
**重启命令**: `start-all.cmd`  
**验证方法**: 在 QQ 中测试高权限工具
