# xiaomiaoVirtual 配置指南

> 详细的配置说明和参数解释

---

## 📁 配置文件位置

```
xiaomiaoVirtual/
├── config.json                    # 主配置（xiaomiaoAgent）
├── xiaomiao/config.json           # QQ Bot 配置
└── xiaomiaoAgent/.nanobot/config.json  # Agent 运行配置
```

---

## ⚙️ 主配置（config.json）

### 基本结构
```json
{
  "xiaomiao_agent": {
    "enabled": true,
    "base_url": "http://127.0.0.1:8900/v1/chat/completions",
    "model": "",
    "session_id": "xiaomiao-unified",
    "timeout_seconds": 30
  },
  "xiaomiaoAgent": {
    "model": "deepseek-v4-flash",
    "providers": {
      "custom": {
        "apiKey": "your-api-key",
        "baseUrl": "https://api.deepseek.com/v1"
      }
    },
    "provider": "custom"
  }
}
```

### 参数说明

#### xiaomiao_agent（QQ Bot → Agent 配置）
- `enabled`: 是否启用 Agent 后端
- `base_url`: Agent API 地址
- `model`: 覆盖模型（可选）
- `session_id`: 会话 ID（默认 xiaomiao-unified）
- `timeout_seconds`: 超时时间（0 = 无限等待）

#### xiaomiaoAgent（Agent 核心配置）
- `model`: 默认模型
- `provider`: 提供商（custom/anthropic/openai）
- `providers.custom`: 自定义提供商配置

---

## 🤖 QQ Bot 配置（xiaomiao/config.json）

### 完整结构
```json
{
  "ROOT": "你的QQ号",
  "Super": [],
  "agent_tool_allowlist": [],
  "owner": ["你的QQ号"],
  "black_list": [],
  "silents": [],
  "Connection": {
    "mode": "FWS",
    "host": "127.0.0.1",
    "port": 5004,
    "listener_host": "127.0.0.1",
    "listener_port": 5003
  },
  "Log_level": "DEBUG",
  "protocol": "OneBot",
  "Others": {
    "bot_name": "小喵",
    "reminder": "- ",
    "personas": {
      "senior_programmer": "高级程序员人设..."
    }
  }
}
```

### 权限配置

#### ROOT（最高权限）
```json
{
  "ROOT": "3554978979"
}
```
- 单个 QQ 号（字符串）
- 完整工具权限

#### Super（管理员）
```json
{
  "Super": ["QQ号1", "QQ号2"]
}
```
- 多个 QQ 号（数组）
- 完整工具权限

#### agent_tool_allowlist（白名单）
```json
{
  "agent_tool_allowlist": ["QQ号3", "QQ号4"]
}
```
- 多个 QQ 号（数组）
- 完整工具权限

### 连接配置

#### NapCat 连接
```json
{
  "Connection": {
    "mode": "FWS",              // 正向 WebSocket
    "host": "127.0.0.1",        // NapCat 地址
    "port": 5004,               // NapCat WebSocket 端口
    "listener_host": "127.0.0.1",
    "listener_port": 5003       // HTTP 回调端口
  }
}
```

### 其他配置

#### Bot 基本信息
```json
{
  "Others": {
    "bot_name": "小喵",         // Bot 名称
    "bot_name_en": "XiaoMiao",  // 英文名
    "reminder": "- "            // 命令前缀
  }
}
```

#### 人设配置
```json
{
  "personas": {
    "senior_programmer": "你叫{bot_name}，是{event_user}的高级程序员助手...",
    "girl_friend": "你叫{bot_name}，是{event_user}的女朋友...",
    "sister": "你叫{bot_name}，是{event_user}的姐姐...",
    "mother": "你叫{bot_name}，是{event_user}的妈妈..."
  }
}
```

---

## 🔧 Agent 配置（.nanobot/config.json）

### 基本配置
```json
{
  "model": "deepseek-chat",
  "provider": "custom",
  "providers": {
    "custom": {
      "apiKey": "sk-xxx",
      "baseUrl": "https://api.deepseek.com/v1"
    },
    "anthropic": {
      "apiKey": "sk-ant-xxx"
    },
    "openai": {
      "apiKey": "sk-xxx"
    }
  }
}
```

### 工具配置
```json
{
  "tools": {
    "exec": {
      "enabled": true
    },
    "web_search": {
      "enabled": true,
      "provider": "brave"
    }
  }
}
```

### MCP 配置
```json
{
  "mcp": {
    "servers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem"]
      }
    }
  }
}
```

---

## 🎨 人设配置

### 人设变量
```
{bot_name}      - Bot 名称
{bot_name_en}   - Bot 英文名
{event_user}    - 用户昵称
```

### 自定义人设
```json
{
  "personas": {
    "my_persona": "你叫{bot_name}，是一个...（人设描述）"
  }
}
```

### 人设切换规则
- 默认：`senior_programmer`
- 特定用户：在配置中指定映射

---

## 🔐 安全配置

### 黑名单
```json
{
  "black_list": ["恶意QQ号"]
}
```

### 静默名单
```json
{
  "silents": ["不响应的QQ号"]
}
```

### 自动审批
```json
{
  "Auto_approval": ["自动同意好友请求的QQ号"]
}
```

---

## 📊 配置示例

### 开发环境
```json
{
  "ROOT": "你的QQ号",
  "Log_level": "DEBUG",
  "Others": {
    "bot_name": "小喵Dev",
    "reminder": "dev-"
  }
}
```

### 生产环境
```json
{
  "ROOT": "管理员",
  "Super": ["副管理1", "副管理2"],
  "Log_level": "INFO",
  "Others": {
    "bot_name": "小喵",
    "reminder": "- "
  }
}
```

### 测试环境
```json
{
  "ROOT": "",
  "agent_tool_allowlist": ["测试账号"],
  "Log_level": "DEBUG"
}
```

---

## ⚠️ 注意事项

### 配置修改后
1. ✅ 重启服务生效
2. ✅ 备份配置文件
3. ✅ 检查 JSON 格式

### 敏感信息
- ⚠️ 不要提交 API Key 到 Git
- ⚠️ 使用环境变量存储密钥
- ⚠️ 定期更换 API Key

---

## 📚 相关文档

- [快速开始](QUICK_START.md) - 基本配置
- [QQ Bot 指南](QQ_BOT_GUIDE.md) - 权限配置
- [故障排查](TROUBLESHOOTING.md) - 配置问题
