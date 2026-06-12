# 配置文件完整说明

> 最后更新：2026-06-12

本文档详细说明 xiaomiaoVirtual 项目的所有配置文件及其关系。

## 配置文件结构

```
xiaomiaoVirtual/
├── config.json                              # 主配置（不提交）
├── config.example.json                      # 配置模板
├── xiaomiao/
│   ├── config.json                          # QQ Bot 配置
│   └── runtime/                             # 运行态配置（不提交）
│       ├── permissions.ini                  # QQ 权限列表
│       ├── roles.ini                        # 角色定义
│       └── timing_message.ini               # 定时消息
└── xiaomiaoAgent/
    └── .nanobot/
        └── config.json                      # Agent 本地配置（自动生成）
```

---

## 一、主配置文件

### config.json

**位置**: `F:\xiaomiaoVirtual\config.json`  
**状态**: 不提交到 Git（包含密钥）  
**作用**: 项目级配置，包含两个主要配置段

#### 1.1 xiaomiao_agent 段（下划线）

**作用**: xiaomiao 作为**客户端**连接 xiaomiaoAgent API 的配置

```json
{
  "xiaomiao_agent": {
    "enabled": true,
    "api_base": "http://localhost:8900/v1",
    "model": "custom/deepseek-v4-flash",
    "timeout": 0,
    "tools_allowed_by_default": true,
    "enable_streaming": true
  }
}
```

**字段说明**:
- `enabled`: 是否启用 Agent 后端（false 则使用本地逻辑）
- `api_base`: xiaomiaoAgent OpenAI 兼容 API 地址
- `model`: 请求的模型名称（格式：`provider/model-name`）
- `timeout`: 请求超时（0 表示无限等待）
- `tools_allowed_by_default`: 工具是否默认允许
- `enable_streaming`: 是否启用流式响应

#### 1.2 xiaomiaoAgent 段（驼峰）

**作用**: xiaomiaoAgent 作为**服务端**的模型提供方配置

```json
{
  "xiaomiaoAgent": {
    "agents": {
      "defaults": {
        "provider": "custom",
        "model": "deepseek-v4-flash"
      }
    },
    "providers": {
      "custom": {
        "api_base": "http://localhost:12345/v1",
        "api_key": "sk-your-key-here"
      },
      "anthropic": {
        "api_key": "sk-ant-..."
      },
      "openai": {
        "api_key": "sk-..."
      }
    }
  }
}
```

**字段说明**:
- `agents.defaults.provider`: 默认提供方（custom/anthropic/openai/minimax 等）
- `agents.defaults.model`: 默认模型名
- `providers.{name}.api_base`: 自定义提供方的 API 地址
- `providers.{name}.api_key`: 提供方的 API 密钥

**命名区别总结**:
| 配置段 | 角色 | 用途 |
|--------|------|------|
| `xiaomiao_agent` (下划线) | 客户端配置 | xiaomiao 调用 Agent |
| `xiaomiaoAgent` (驼峰) | 服务端配置 | Agent 调用模型提供方 |

---

## 二、子系统配置

### xiaomiao/config.json

**作用**: QQ 机器人的人设、命令、OneBot 配置

```json
{
  "bot_name": "小喵",
  "personality": {
    "girlfriend": "可爱活泼的女朋友人设",
    "programmer": "高级编程助手人设"
  },
  "commands": {
    "agent_prompt_word": "喵喵",
    "exact_agent_prompts": ["重置", "清空", "状态"]
  },
  "onebot": {
    "reverse_ws_host": "localhost",
    "reverse_ws_port": 5004
  },
  "desktop_bridge": {
    "host": "localhost",
    "port": 5519
  }
}
```

**关键字段**:
- `personality`: 人设模板（对应 `xiaomiao/personas/` 目录）
- `commands.agent_prompt_word`: 触发 Agent 的关键词
- `onebot.*`: NapCat WebSocket 反向连接配置
- `desktop_bridge.*`: 桌面桥接服务地址

---

## 三、运行态配置

### xiaomiao/runtime/*.ini

这些文件包含**运行时数据**，不应提交到 Git。

#### 3.1 permissions.ini

QQ 用户权限列表：

```ini
[permissions]
# 格式：QQ号 = 权限等级
# root > super > manage > allowlist > common
123456789 = root
987654321 = allowlist
```

#### 3.2 roles.ini

角色映射（用户 → 人设）：

```ini
[roles]
# 格式：QQ号 = 角色名
123456789 = girlfriend
987654321 = programmer
```

#### 3.3 timing_message.ini

定时消息配置（由 QQ 指令动态生成）

---

## 四、Agent 本地配置

### xiaomiaoAgent/.nanobot/config.json

**作用**: nanobot 框架的本地持久化配置（自动生成，很少手动编辑）

**内容示例**:
```json
{
  "agents": {
    "defaults": {
      "provider": "custom",
      "model": "deepseek-v4-flash"
    }
  },
  "providers": {
    "custom": {
      "api_base": "http://localhost:12345/v1",
      "api_key": "..."
    }
  },
  "tools": {
    "web": {
      "search": {
        "provider": "brave",
        "api_key": "..."
      }
    }
  }
}
```

**说明**:
- 首次运行 `python -m nanobot login` 时自动创建
- 与主配置的 `xiaomiaoAgent` 段内容**优先级不同**：
  - 主配置优先级更高（覆盖本地配置）
  - 本地配置作为备用

---

## 五、配置优先级

### 5.1 xiaomiaoAgent 配置加载顺序

```
1. 主配置 config.json 的 xiaomiaoAgent 段（最高优先级）
   ↓
2. xiaomiaoAgent/.nanobot/config.json（备用）
   ↓
3. 环境变量（如 ANTHROPIC_API_KEY）
   ↓
4. 内置默认值
```

### 5.2 xiaomiao 配置加载顺序

```
1. 主配置 config.json 的 xiaomiao_agent 段
   ↓
2. xiaomiao/config.json（人设和命令）
   ↓
3. xiaomiao/runtime/*.ini（权限和角色）
```

---

## 六、配置验证

### 6.1 检查配置完整性

```powershell
# 检查主配置
python -c "import json; json.load(open('config.json'))"

# 检查 xiaomiao 配置
python -c "import json; json.load(open('xiaomiao/config.json'))"
```

### 6.2 验证 Agent 配置

```powershell
cd xiaomiaoAgent
conda activate xiaomiao
python -m nanobot config show
```

### 6.3 验证所有端口

```powershell
.\start-all.cmd --check
```

---

## 七、环境变量支持

可以使用环境变量替代配置文件中的敏感信息：

```powershell
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:OPENAI_API_KEY = "sk-..."
$env:CUSTOM_API_BASE = "http://localhost:12345/v1"
$env:CUSTOM_API_KEY = "sk-your-key"

# 启动服务
.\start-all.cmd
```

**优先级**: 环境变量 < 主配置文件 < 本地配置文件

---

## 八、配置模板

### 快速开始配置（最小配置）

**config.json** (最简版)：

```json
{
  "xiaomiao_agent": {
    "enabled": true,
    "api_base": "http://localhost:8900/v1",
    "model": "custom/deepseek-v4-flash"
  },
  "xiaomiaoAgent": {
    "agents": {
      "defaults": {
        "provider": "custom",
        "model": "deepseek-v4-flash"
      }
    },
    "providers": {
      "custom": {
        "api_base": "http://localhost:12345/v1",
        "api_key": "sk-your-key-here"
      }
    }
  }
}
```

---

## 九、常见配置问题

### 9.1 模型调用失败

**症状**: `xiaomiaoAgent` 返回 502 错误

**检查**:
1. `providers.{name}.api_key` 是否正确
2. `providers.{name}.api_base` 是否可达
3. 模型名是否正确

### 9.2 QQ 消息无响应

**检查**:
1. `xiaomiao_agent.enabled` 是否为 true
2. `xiaomiao_agent.api_base` 是否可达（默认 8900 端口）
3. NapCat 是否正常连接（5004 端口）

### 9.3 权限不生效

**检查**:
1. `xiaomiao/runtime/permissions.ini` 是否存在
2. QQ 号是否正确添加
3. 权限等级拼写是否正确（root/super/manage/allowlist）

---

## 十、安全建议

1. **永远不要提交包含密钥的 config.json**
   - 已在 `.gitignore` 中排除
   - 使用 `config.example.json` 作为模板

2. **使用环境变量存储密钥**
   - 更安全，避免文件泄露
   - 适合 CI/CD 环境

3. **定期轮换 API 密钥**
   - 特别是在团队协作场景

4. **限制配置文件权限**
   ```powershell
   # Windows: 仅当前用户可读
   icacls config.json /inheritance:r /grant:r "%USERNAME%:R"
   ```

---

## 相关文档

- [运行与配置](./运行与配置.md) - 快速启动指南
- [STARTUP.md](./STARTUP.md) - 详细启动流程
- [troubleshooting.md](./troubleshooting.md) - 故障排查
- [xiaomiaoAgent/README.md](./xiaomiaoAgent/README.md) - Agent 框架文档
