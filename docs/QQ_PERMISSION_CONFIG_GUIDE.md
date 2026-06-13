# QQ Bot 权限配置说明

## ✅ 配置已完成

你的 QQ 号 **3554978979** 已经配置为 ROOT 用户，现在拥有完整的工具权限！

---

## 📍 权限 QQ 号设置位置

### 配置文件位置
```
xiaomiao/config.json
```

### 权限配置字段（文件开头）
```json
{
    "ROOT": "3554978979",              ← ROOT 用户（最高权限）
    "Super": [],                        ← Super 用户列表（高级权限）
    "agent_tool_allowlist": [],         ← 工具白名单用户（工具权限）
    "owner": ["3554978979"],            ← 机器人所有者（原有字段）
    ...
}
```

---

## 🔑 三种权限等级

### 1. ROOT（最高权限）
```json
"ROOT": "你的QQ号"
```
- ✅ 完全权限，可使用所有工具
- ✅ 单个用户（字符串，不是数组）
- ⚠️ 只设置一个 QQ 号

### 2. Super（高级权限）
```json
"Super": ["QQ号1", "QQ号2", "QQ号3"]
```
- ✅ 可使用所有工具
- ✅ 多个用户（数组）
- 💡 适合管理员团队

### 3. agent_tool_allowlist（工具白名单）
```json
"agent_tool_allowlist": ["QQ号4", "QQ号5"]
```
- ✅ 可使用所有工具
- ✅ 多个用户（数组）
- 💡 适合开发者/测试人员

### 4. 普通用户（默认）
- ⚠️ 只能使用低风险工具
- ⚠️ 不能执行命令、写文件

---

## 🎯 当前配置

```json
{
    "ROOT": "3554978979",               ← 你是 ROOT
    "Super": [],                        ← 暂无 Super 用户
    "agent_tool_allowlist": [],         ← 暂无白名单用户
    ...
}
```

**你的 QQ 号（3554978979）权限**：
- ✅ ROOT 最高权限
- ✅ 可以使用全部 26+ 工具
- ✅ 等同于 TUI 的完整能力

---

## 🔧 如何修改权限

### 添加其他管理员（Super）
```json
{
    "ROOT": "3554978979",
    "Super": ["另一个QQ号"],           ← 添加到这里
    "agent_tool_allowlist": [],
    ...
}
```

### 添加开发者（工具白名单）
```json
{
    "ROOT": "3554978979",
    "Super": [],
    "agent_tool_allowlist": ["开发者QQ号"],  ← 添加到这里
    ...
}
```

### 修改 ROOT 用户
```json
{
    "ROOT": "新的QQ号",                ← 直接修改这里
    "Super": [],
    "agent_tool_allowlist": [],
    ...
}
```

---

## 📊 权限对比

| 用户类型 | 低风险工具 | 高权限工具 | Shell命令 | 文件写入 | MCP工具 |
|---------|-----------|-----------|----------|---------|---------|
| **ROOT** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Super** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **白名单** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **普通用户** | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## ✅ 下一步操作

### 1. 重启 QQ Bot 服务
```cmd
# 关闭现有服务（如果在运行）
# 按 Ctrl+C 或关闭窗口

# 重新启动
cd f:\xiaomiaoVirtual
start-all.cmd
```

### 2. 在 QQ 中测试

#### 测试 1: 文件写入
```
发送: - 帮我创建一个测试文件 test.txt，内容是 "Hello World"

预期: Agent 调用 write_file 工具，文件创建成功
```

#### 测试 2: Shell 命令
```
发送: - 执行命令 dir 查看当前目录

预期: Agent 调用 exec 工具，返回目录列表
```

#### 测试 3: 文件读取（低风险工具）
```
发送: - 读取 README.md 文件的内容

预期: Agent 调用 read_file 工具（普通用户也能用）
```

#### 测试 4: Web 搜索（低风险工具）
```
发送: - 搜索最新的 AI 新闻

预期: Agent 调用 web_search 工具（普通用户也能用）
```

---

## 🔍 验证权限生效

### 查看日志
启动 QQ Bot 后，查看控制台日志，应该看到：
```
[INFO] User 3554978979 identified as ROOT
[INFO] Tool policy: trusted_confirmed
[INFO] Available tools: 26
```

### 询问 Agent
在 QQ 中问：
```
- 你现在可以使用哪些工具？列出所有工具名称
```

如果看到包含 `exec`、`write_file`、`edit_file` 等，说明权限配置成功。

---

## ⚠️ 安全注意事项

### ROOT 权限风险
你的 QQ 号现在在 Agent 中拥有**系统级权限**：
- ⚠️ 可以执行任意系统命令
- ⚠️ 可以读写任意文件
- ⚠️ 可以访问网络和外部服务
- ⚠️ 可以操作 MCP 工具（如 Computer Use）

### 安全建议
1. ✅ **不要泄露 config.json** 文件
2. ✅ **定期检查配置** 确保只有信任的人有权限
3. ✅ **监控 Agent 操作** 留意异常的工具调用
4. ✅ **使用白名单** 如果只需要工具权限而不需要 ROOT：
   ```json
   {
     "ROOT": "",
     "agent_tool_allowlist": ["3554978979"]
   }
   ```

---

## 🔄 如何撤销配置

如果想撤销 ROOT 权限：

### 方法 1: 恢复备份
```cmd
cd f:\xiaomiaoVirtual\xiaomiao
copy config.json.backup.* config.json
```

### 方法 2: 手动修改
编辑 `xiaomiao/config.json`，删除或清空：
```json
{
    "ROOT": "",                     ← 改为空字符串
    "Super": [],                    ← 保持空数组
    "agent_tool_allowlist": [],     ← 保持空数组
    ...
}
```

---

## 📞 快速参考

### 配置文件位置
```
f:\xiaomiaoVirtual\xiaomiao\config.json
```

### 备份文件位置
```
f:\xiaomiaoVirtual\xiaomiao\config.json.backup.*
```

### 重启服务
```cmd
start-all.cmd
```

### 查看完整文档
```
docs\QQ_BOT_TOOL_CAPABILITY_ANALYSIS.md
```

---

## ✨ 总结

### 配置内容
- ✅ 你的 QQ 号：**3554978979**
- ✅ 权限等级：**ROOT（最高权限）**
- ✅ 可用工具：**26+ 个（全部）**

### 配置位置
- 📁 文件：`xiaomiao/config.json`
- 📍 字段：文件开头的 `ROOT`、`Super`、`agent_tool_allowlist`

### 生效方式
- 🔄 重启 QQ Bot 服务（`start-all.cmd`）

---

**配置已完成！重启服务后即可在 QQ 中使用完整工具能力。** 🎉
