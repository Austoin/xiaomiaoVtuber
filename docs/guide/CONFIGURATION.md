# xiaomiaoVirtual 配置

项目只使用根目录的 `config.json` 作为统一配置入口。QQ 端和各 UI 端不持有独立模型配置，所有推理请求都交给 `xiaomiaoAgent`。

## 最小配置

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
    "provider": "custom",
    "model": "deepseek-v4-flash",
    "providers": {
      "custom": {
        "apiKey": "替换为真实密钥",
        "baseUrl": "https://api.deepseek.com/v1"
      }
    },
    "channels": {
      "websocket": {
        "enabled": true,
        "host": "127.0.0.1",
        "port": 8765,
        "allowFrom": ["*"]
      },
      "discord": { "enabled": false, "token": "", "allowFrom": [] },
      "telegram": { "enabled": false, "token": "", "allowFrom": [] }
    }
  }
}
```

## Agent 配置

`xiaomiaoAgent` 是唯一模型与工具运行层：

| 字段 | 说明 |
| --- | --- |
| `provider` | 当前 Provider 名称，现有统一配置使用 `custom` |
| `model` | Provider 实际模型名 |
| `providers.custom.apiKey` | Provider API 密钥，不能为空 |
| `providers.custom.baseUrl` | OpenAI 兼容 API 的绝对 HTTP(S) 地址 |

配置不完整时，Agent 会显式报告未配置或上游错误，不会静默切换模型。

## QQ 客户端配置

`xiaomiao_agent` 只负责 QQ 端连接 Agent：

| 字段 | 说明 |
| --- | --- |
| `enabled` | 是否启用 Agent 后端 |
| `base_url` | 固定指向 Agent 的 `/v1/chat/completions` |
| `model` | 留空时由 Agent 使用统一配置模型 |
| `session_id` | QQ、Web 和桌面端共享会话 ID |
| `timeout_seconds` | QQ 请求超时秒数 |

Web、Pocket 和 Electron 通过共享的 Stage UI 客户端访问同一 `127.0.0.1:8900` Agent API，不需要重复配置 Provider。

## 通道与 MCP

- `channels.websocket` 提供内嵌 WebUI，默认监听 `127.0.0.1:8765`。
- `channels.discord` 与 `channels.telegram` 是 Agent 原生通道，只配置 token 和访问白名单。
- `tools.twitterMcp` 指向 Twitter 服务的 `http://127.0.0.1:8080/sse`。
- `tools.minecraftMcp` 指向启用调试 MCP 后的 Minecraft 服务。

完整启动和环境变量见 [外部通道与服务](INTEGRATIONS.md)。

## 接口检查

Agent 启动后可检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8900/health
Invoke-RestMethod http://127.0.0.1:8900/v1/xiaomiao/config
Invoke-RestMethod http://127.0.0.1:8900/v1/xiaomiao/events
Invoke-RestMethod http://127.0.0.1:18790/health
Invoke-RestMethod http://127.0.0.1:8765/webui/bootstrap
```

聊天请求使用 `POST /v1/chat/completions`。完整请求格式见 [Agent API 文档](../../xiaomiaoAgent/docs/openai-api.md)。

## 安全要求

- 不要提交真实 API Key。
- `baseUrl` 必须是合法的绝对 HTTP(S) URL。
- 修改 Provider 配置后重启 Agent，使运行实例加载新配置。
