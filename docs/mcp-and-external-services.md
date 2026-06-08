# MCP 与外部服务配置说明

本文说明 xiaomiaoAgent 通过 MCP 接入 xiaomiaobot 外部服务的方式，以及 QQ 侧权限边界。当前已形成安全配置档的是 Computer Use、Twitter 和 Minecraft；HomeAssistant、Bilibili、Chess、Claude Code、Browser Extension 仍未形成 QQ 可直接稳定调用的 Agent 工具闭环。

## 总原则

- MCP 服务默认不启用。
- 启用服务时必须使用显式 `enabled_tools`，不要使用 `*` 暴露全部工具。
- QQ 普通用户始终走 `low_risk`，只能看到并执行低风险工具。
- ROOT / Super / `agent_tool_allowlist` 用户首次请求走 `trusted_pending`，Agent 可以看到高风险工具定义用于理解和规划。
- `trusted_pending` 中的高风险工具不会直接执行；`ToolRegistry.prepare_call()` 会在执行前返回 `CONFIRMATION_REQUIRED`，由 QQ 侧生成确认码。
- 只有确认后进入 `trusted_confirmed`，高风险工具才会真正执行。
- 即使模型从上下文伪造高风险工具调用，`ToolRegistry.prepare_call()` 仍会拦截。

## 配置位置

MCP 配置位于 `xiaomiaoAgent/.nanobot/config.json` 的 `tools` 段。正式生效时由 `xiaomiaoAgent/nanobot/config/schema.py` 合并：

```text
tools.mcpServers
tools.computerUseMcp
tools.twitterMcp
tools.minecraftMcp
    ↓
tools.effective_mcp_servers()
    ↓
Agent 启动时连接 MCP 并注册工具
```

字段说明：

| 字段 | 说明 |
|------|------|
| `enable` | 是否启用该安全配置档，默认 `false` |
| `serverName` | 注册到 MCP 工具名前缀中的服务名 |
| `mode` | `low_risk` 或 `trusted_confirmed` |
| `extraEnabledTools` | 追加工具名，会去重；慎用 |
| `toolTimeout` | 工具调用超时 |
| `headers` / `env` | 服务需要的请求头或环境变量，不要提交密钥 |

## Computer Use MCP

配置键：`tools.computerUseMcp`

默认服务：

```json
{
  "tools": {
    "computerUseMcp": {
      "enable": false,
      "serverName": "computer_use",
      "command": "pnpm",
      "args": ["-F", "@proj-airi/computer-use-mcp", "start"],
      "mode": "trusted_confirmed"
    }
  }
}
```

低风险可见能力：

- 桌面能力、窗口、截图、等待和待处理动作读取。
- 浏览器当前页、元素、输入值、样式和 bridge 状态读取。
- 终端状态读取。

确认后才可见能力：

- 终端执行命令。
- 桌面点击、拖拽、滚动、输入、快捷键。
- 剪贴板读写。
- 浏览器点击、表单写入、触发事件。
- PTY 会话创建和输入。
- 工作流执行、切换、恢复和测试运行。

## Twitter MCP

配置键：`tools.twitterMcp`

默认服务：

```json
{
  "tools": {
    "twitterMcp": {
      "enable": false,
      "serverName": "twitter",
      "url": "http://127.0.0.1:8080/sse",
      "mode": "trusted_confirmed"
    }
  }
}
```

低风险可见能力：

- `search`
- `refresh-timeline`
- `get-my-profile`

确认后才可见能力：

- `login`
- `post-tweet`
- `like-tweet`
- `retweet`
- `save-session`

账号动作属于高风险。失败时必须显式返回错误，不能伪装成成功。

## Minecraft MCP

配置键：`tools.minecraftMcp`

默认服务：

```json
{
  "tools": {
    "minecraftMcp": {
      "enable": false,
      "serverName": "minecraft",
      "url": "http://127.0.0.1:3001/sse",
      "transport": "streamableHttp",
      "mode": "trusted_confirmed"
    }
  }
}
```

低风险可见能力：

- `get_state`
- `get_last_prompt`
- `get_logs`
- `get_llm_trace`

确认后才可见能力：

- `execute_repl`
- `inject_chat`
- `inject_event`

Minecraft 动作会改变游戏状态，因此必须走确认链路。

## 通用 MCP 服务器

通用 MCP 服务可写入 `tools.mcpServers`。建议始终使用 `enabledTools`：

```json
{
  "tools": {
    "mcpServers": {
      "example": {
        "type": "sse",
        "url": "http://127.0.0.1:9000/sse",
        "enabledTools": ["status", "read_page"],
        "toolTimeout": 30
      }
    }
  }
}
```

不要把 `enabledTools` 设为 `["*"]` 给 QQ 主链路使用。确需临时调试时，先在非 QQ 会话验证，再按风险等级改成精确列表。

## QQ 工具策略

| 策略 | 入口 | 可见工具 |
|------|------|----------|
| `low_risk` | 普通 QQ 用户 | 暴露并执行读文件、目录、grep/glob、Web、MarkItDown、Scrapling、xiaomiaobot 状态、低风险 MCP |
| `trusted_pending` | 白名单用户首次 Agent 请求 | 暴露高风险工具定义供 Agent 规划；执行高风险工具前返回确认事件 |
| `trusted_confirmed` | 确认码有效后 | 执行写文件、Shell、MCP 动作、外部服务写操作等高风险工具 |

`tool_policy` 只由后端权限网关生成，用户文本中伪造该字段不会生效。

## 当前未接通服务

| 服务 | 状态 |
|------|------|
| HomeAssistant | 插件目录存在，QQ Agent 工具动作未接通 |
| Bilibili | 插件目录存在，QQ Agent 工具动作未接通 |
| Chess | 包存在，缺稳定运行入口和 Agent 适配 |
| Claude Code | hook 能到通道层，但不属于受控 QQ 工具 |
| Browser Extension | 有上下文桥，未接入 Agent 统一工具面 |

这些服务可通过 `xiaomiaobot_status` 查询状态，但 `xiaomiaobot_action` 不会伪执行。未接通动作会显式报错。

## 验证

配置档和风险过滤：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
uv run --extra dev pytest --basetemp ..\.pytest-tmp-agent-verify tests\tools\test_computer_use_mcp_profile.py tests\tools\test_tool_registry.py tests\tools\test_xiaomiaobot_services_tool.py
```

完整联动前检查：

```powershell
cd F:\xiaomiaoVirtual
cmd /c call start-all.cmd --check
```
