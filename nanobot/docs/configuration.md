# 配置

配置文件位置：`~/.nanobot/config.json`

> [!NOTE]
> 如果你的配置文件早于当前 schema，可以运行 `nanobot onboard` 刷新默认字段。系统询问是否覆盖配置时选择 `N`，nanobot 会合并缺失默认字段，并保留当前设置。

## 使用环境变量保存密钥

不要把密钥直接写入 `config.json`。可以使用 `${VAR_NAME}` 引用环境变量，nanobot 会在启动时解析：

```json
{
  "channels": {
    "telegram": { "token": "${TELEGRAM_TOKEN}" },
    "email": {
      "imapPassword": "${IMAP_PASSWORD}",
      "smtpPassword": "${SMTP_PASSWORD}"
    }
  },
  "providers": {
    "groq": { "apiKey": "${GROQ_API_KEY}" }
  }
}
```

systemd 部署可在 service unit 中使用 `EnvironmentFile=` 加载只有部署用户可读的变量文件：

```ini
# /etc/systemd/system/nanobot.service（节选）
[Service]
EnvironmentFile=/home/youruser/nanobot_secrets.env
User=nanobot
ExecStart=...
```

```bash
# /home/youruser/nanobot_secrets.env（权限 600，归 youruser 所有）
TELEGRAM_TOKEN=your-token-here
IMAP_PASSWORD=your-password-here
```

## Providers

> [!TIP]
> 语音消息（Telegram、WhatsApp）会自动使用 Whisper 转写。默认 Provider 是 Groq（免费层）。如需使用 OpenAI Whisper，请在 `channels` 下设置 `"transcriptionProvider": "openai"`，并可选设置 `"transcriptionLanguage": "en"` 等 ISO-639-1 语言码。

| Provider | 用途 | 获取 API Key |
|----------|---------|-------------|
| `custom` | 任意 OpenAI 兼容端点 | — |
| `openrouter` | LLM，推荐，可访问多模型 | [openrouter.ai](https://openrouter.ai) |
| `huggingface` | LLM，Hugging Face Inference Providers | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `volcengine` | LLM，火山引擎，按量付费 | [volcengine.com](https://www.volcengine.com) |
| `byteplus` | LLM，火山引擎国际版，按量付费 | [byteplus.com](https://www.byteplus.com) |
| `anthropic` | LLM，Claude 直连 | [console.anthropic.com](https://console.anthropic.com) |
| `azure_openai` | LLM，Azure OpenAI | [portal.azure.com](https://portal.azure.com) |
| `bedrock` | LLM，AWS Bedrock Converse | [aws.amazon.com/bedrock](https://aws.amazon.com/bedrock/) |
| `openai` | LLM + Whisper 语音转写 | [platform.openai.com](https://platform.openai.com) |
| `deepseek` | LLM，DeepSeek 直连 | [platform.deepseek.com](https://platform.deepseek.com) |
| `groq` | LLM + Whisper 语音转写，默认转写 Provider | [console.groq.com](https://console.groq.com) |
| `minimax` | LLM，MiniMax 直连 | [platform.minimaxi.com](https://platform.minimaxi.com) |
| `minimax_anthropic` | LLM，MiniMax Anthropic 兼容端点，支持 thinking mode | [platform.minimaxi.com](https://platform.minimaxi.com) |
| `gemini` | LLM，Gemini 直连 | [aistudio.google.com](https://aistudio.google.com) |
| `aihubmix` | LLM API gateway，可访问多模型 | [aihubmix.com](https://aihubmix.com) |
| `siliconflow` | LLM，硅基流动 | [siliconflow.cn](https://siliconflow.cn) |
| `dashscope` | LLM，通义千问 | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) |
| `moonshot` | LLM，Moonshot/Kimi | [platform.moonshot.cn](https://platform.moonshot.cn) |
| `zhipu` | LLM，智谱 GLM | [open.bigmodel.cn](https://open.bigmodel.cn) |
| `mimo` | LLM，小米 MiMo | [platform.xiaomimimo.com](https://platform.xiaomimimo.com) |
| `longcat` | LLM，LongCat | [longcat.chat](https://longcat.chat/platform/docs/zh/) |
| `ollama` | 本地 LLM，Ollama | — |
| `lm_studio` | 本地 LLM，LM Studio | — |
| `mistral` | LLM | [docs.mistral.ai](https://docs.mistral.ai/) |
| `stepfun` | LLM，阶跃星辰 | [platform.stepfun.com](https://platform.stepfun.com) |
| `ovms` | 本地 LLM，OpenVINO Model Server | [docs.openvino.ai](https://docs.openvino.ai/2026/model-server/ovms_docs_llm_quickstart.html) |
| `vllm` | 本地 LLM，任意 OpenAI 兼容服务 | — |
| `openai_codex` | LLM，Codex OAuth | `nanobot provider login openai-codex` |
| `github_copilot` | LLM，GitHub Copilot OAuth | `nanobot provider login github-copilot` |
| `qianfan` | LLM，百度千帆 | [cloud.baidu.com](https://cloud.baidu.com/doc/qianfan/s/Hmh4suq26) |

### AWS Bedrock（Converse API）

Bedrock 使用原生 `bedrock-runtime` Converse API，可调用 Claude、Amazon Nova、Meta Llama、Mistral、Qwen 等支持 Converse 的模型。它支持普通聊天、streaming、tool calling、tool result、token usage 和 Bedrock 错误元数据。

它不是 Bedrock 的 OpenAI 兼容 `/openai/v1` 端点。如果你明确需要 OpenAI 兼容接口，可以使用 `custom`。

常见凭据方式：AWS CLI/default profile、命名 profile、EC2/ECS/Lambda IAM role，或 Bedrock API Key。

最小配置示例：

```json
{
  "providers": {
    "bedrock": {
      "region": "us-east-1"
    }
  },
  "agents": {
    "defaults": {
      "provider": "bedrock",
      "model": "bedrock/amazon.nova-lite-v1:0",
      "reasoningEffort": null
    }
  }
}
```

使用 Bedrock API Key：

```json
{
  "providers": {
    "bedrock": {
      "region": "us-east-1",
      "apiKey": "${AWS_BEARER_TOKEN_BEDROCK}"
    }
  }
}
```

模型 ID 需要带 `bedrock/` 前缀，nanobot 调用 AWS 前会移除该前缀。例如：`bedrock/amazon.nova-micro-v1:0`、`bedrock/global.anthropic.claude-opus-4-7`、`bedrock/openai.gpt-oss-20b-1:0`。

### OpenAI Codex 与 GitHub Copilot（OAuth）

这两个 Provider 使用 OAuth，不需要在 `config.json` 中写 API Key。登录会话保存在配置外部。

```bash
nanobot provider login openai-codex
nanobot provider login github-copilot
```

设置模型示例：

```json
{
  "agents": {
    "defaults": {
      "model": "openai-codex/gpt-5.1-codex"
    }
  }
}
```

Docker 用户执行交互式 OAuth 登录时需要使用 `docker run -it`。

### LongCat

LongCat 通过内置 OpenAI 兼容 Provider 流程接入。默认 API base 已指向 `https://api.longcat.chat/openai/v1`，通常只需设置 `apiKey`：

```json
{
  "providers": {
    "longcat": {
      "apiKey": "${LONGCAT_API_KEY}"
    }
  },
  "agents": {
    "defaults": {
      "provider": "longcat",
      "model": "LongCat-Flash-Chat"
    }
  }
}
```

### Custom Provider

`custom` 可连接任意 OpenAI 兼容 chat completions 端点，例如 llama.cpp、Together AI、Fireworks、Azure OpenAI 或自托管服务。模型名会原样传递。

```json
{
  "providers": {
    "custom": {
      "apiKey": "your-api-key",
      "apiBase": "https://api.your-provider.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "your-model-name"
    }
  }
}
```

本地服务不需要认证时可将 `apiKey` 设为 `null`。如果端点是 Responses API 兼容而不是 chat completions 兼容，请使用 `azure_openai` 形态。

一些 OpenAI 兼容 gateway 支持请求体扩展，例如 vLLM guided decoding 或本地采样参数。可放入 `extraBody`，nanobot 会合并进 chat-completions 请求体：

```json
{
  "providers": {
    "custom": {
      "apiKey": "your-api-key",
      "apiBase": "https://api.your-provider.com/v1",
      "extraBody": {
        "repetition_penalty": 1.15
      }
    }
  }
}
```

### 本地 Provider

Ollama：

```json
{
  "providers": {
    "ollama": {
      "apiBase": "http://localhost:11434"
    }
  },
  "agents": {
    "defaults": {
      "provider": "ollama",
      "model": "llama3.2"
    }
  }
}
```

LM Studio：

```json
{
  "providers": {
    "lm_studio": {
      "apiKey": null,
      "apiBase": "http://localhost:1234/v1"
    }
  },
  "agents": {
    "defaults": {
      "provider": "lm_studio",
      "model": "local-model"
    }
  }
}
```

OpenVINO Model Server：

```json
{
  "providers": {
    "ovms": {
      "apiBase": "http://localhost:8000/v3"
    }
  },
  "agents": {
    "defaults": {
      "provider": "ovms",
      "model": "openai/gpt-oss-20b"
    }
  }
}
```

vLLM：

```json
{
  "providers": {
    "vllm": {
      "apiKey": null,
      "apiBase": "http://localhost:8000/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "meta-llama/Llama-3.1-8B-Instruct"
    }
  }
}
```

### 添加新 Provider（开发者指南）

nanobot 使用 `nanobot/providers/registry.py` 中的 **Provider Registry** 作为单一事实来源。添加新 Provider 通常只需两步：

1. 在 `PROVIDERS` 中添加一个 `ProviderSpec`。
2. 在 `nanobot/config/schema.py` 的 `ProvidersConfig` 中添加对应字段。

```python
ProviderSpec(
    name="myprovider",
    keywords=("myprovider", "mymodel"),
    env_key="MYPROVIDER_API_KEY",
    display_name="My Provider",
    default_api_base="https://api.myprovider.com/v1",
)
```

常见 `ProviderSpec` 选项包括 `default_api_base`、`env_extras`、`model_overrides`、`is_gateway`、`detect_by_key_prefix`、`detect_by_base_keyword`、`strip_model_prefix`、`supports_max_completion_tokens`。

## 通道全局设置

这些设置位于 `~/.nanobot/config.json` 的 `channels` 下，作用于所有通道：

```json
{
  "channels": {
    "sendProgress": true,
    "sendToolHints": false,
    "sendMaxRetries": 3,
    "transcriptionProvider": "groq",
    "transcriptionLanguage": null,
    "telegram": { }
  }
}
```

| 设置 | 默认值 | 说明 |
|---------|---------|-------------|
| `sendProgress` | `true` | 将 agent 文本进度流式发送到通道 |
| `sendToolHints` | `false` | 发送工具调用提示，例如 `read_file("…")` |
| `sendMaxRetries` | `3` | 每条出站消息最大投递尝试次数，包含首次发送 |
| `transcriptionProvider` | `"groq"` | 语音转写后端：`"groq"` 或 `"openai"` |
| `transcriptionLanguage` | `null` | 可选 ISO-639-1 语言提示，例如 `"en"`、`"ko"`、`"ja"` |

`sendProgress` 和 `sendToolHints` 也可以按通道覆盖。

### 重试行为

通道 `send()` 抛错时，nanobot 会在 channel-manager 层重试。默认 `sendMaxRetries` 为 `3`，包含首次发送。退避为 `1s`、`2s`、`4s`，之后保持最大 `4s`。

如果通道完全不可达，nanobot 无法通过同一通道通知用户。请查看日志中的 `Failed to send to {channel} after N attempts`。

## Web 工具

nanobot 默认启用基础 Web 工具，包括通过 API 搜索，以及将网页抓取为 Markdown。配置位于 `tools.web`。

禁用全部 Web 工具：

```json
{
  "tools": {
    "web": {
      "enable": false
    }
  }
}
```

如需允许可信私有网段（例如 Tailscale / CGNAT），可通过 `tools.ssrfWhitelist` 从 SSRF 阻断中豁免：

```json
{
  "tools": {
    "ssrfWhitelist": ["100.64.0.0/10"]
  }
}
```

代理配置：

```json
{ "tools": { "web": { "proxy": "http://127.0.0.1:7890" } } }
```

### `tools.web`

| 选项 | 类型 | 默认值 | 说明 |
|--------|------|---------|-------------|
| `enable` | boolean | `true` | 启用或禁用内置 Web 工具（`web_search` + `web_fetch`） |
| `proxy` | string 或 null | `null` | 所有 Web 请求使用的代理 |
| `userAgent` | string 或 null | `null` | 所有 Web 请求的 User-Agent；为 null 时使用浏览器 UA |

### Web Search

默认使用 `duckduckgo`，无需 API Key。

| Provider | 配置字段 | 环境变量 fallback | 免费 |
|----------|--------------|------------------|------|
| `brave` | `apiKey` | `BRAVE_API_KEY` | 否 |
| `tavily` | `apiKey` | `TAVILY_API_KEY` | 否 |
| `jina` | `apiKey` | `JINA_API_KEY` | 免费层 |
| `kagi` | `apiKey` | `KAGI_API_KEY` | 否 |
| `olostep` | `apiKey` | `OLOSTEP_API_KEY` | 否 |
| `searxng` | `baseUrl` | `SEARXNG_BASE_URL` | 是，自托管 |
| `duckduckgo` | 无 | 无 | 是 |

```json
{
  "tools": {
    "web": {
      "search": {
        "provider": "duckduckgo",
        "maxResults": 5
      }
    }
  }
}
```

### Web Fetch

默认使用 [Jina Reader](https://jina.ai/reader/) 将网页转换为 Markdown，并在失败时回退到基于 readability-lxml 的本地转换。

强制使用本地转换：

```json
{
  "tools": {
    "web": {
      "fetch": {
        "useJinaReader": false
      }
    }
  }
}
```

## 图像生成

图像生成配置位于 `tools.imageGeneration`，使用 `providers.openrouter` 或 `providers.aihubmix` 中的凭据。详见[图像生成](./image-generation.md)。

## MCP（Model Context Protocol）

nanobot 支持 [MCP](https://modelcontextprotocol.io/)，可以连接外部工具服务器，并作为原生 agent 工具使用。配置格式兼容 Claude Desktop / Cursor。

```json
{
  "tools": {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
      },
      "my-remote-mcp": {
        "url": "https://example.com/mcp/",
        "headers": {
          "Authorization": "Bearer xxxxx"
        }
      }
    }
  }
}
```

支持两种传输方式：

| 模式 | 配置 | 示例 |
|------|--------|---------|
| **Stdio** | `command` + `args` | 通过 `npx` / `uvx` 启动本地进程 |
| **HTTP** | `url` + 可选 `headers` | 远程端点，例如 `https://mcp.example.com/sse` |

慢速服务器可用 `toolTimeout` 覆盖默认 30 秒工具超时。`enabledTools` 可只注册某个 MCP server 的部分工具；省略或设为 `["*"]` 表示注册全部，设为 `[]` 表示不注册任何工具。

## 安全

> [!TIP]
> 生产部署建议设置 `"restrictToWorkspace": true` 和 `"tools.exec.sandbox": "bwrap"`。`v0.1.4.post4` 起，空 `allowFrom` 默认拒绝所有访问；如需允许所有发送者，请设为 `"allowFrom": ["*"]`。

| 选项 | 默认值 | 说明 |
|--------|---------|-------------|
| `tools.restrictToWorkspace` | `false` | 为所有 agent 工具限制工作区范围，防止路径穿越和越界访问 |
| `tools.exec.sandbox` | `""` | shell 命令沙箱后端。设为 `"bwrap"` 可使用 bubblewrap 隔离，仅 Linux 可用 |
| `tools.exec.enable` | `true` | 为 `false` 时完全不注册 shell `exec` 工具 |
| `tools.exec.pathAppend` | `""` | 运行 shell 命令时追加到 `PATH` 的目录 |
| `channels.*.allowFrom` | `[]` | 用户 ID 白名单。空列表拒绝所有；`["*"]` 允许所有 |

官方 Docker 镜像以非 root 用户 `nanobot`（UID 1000）运行，并预装 bubblewrap。

## 子 Agent 并发

默认只允许同时运行一个 spawned subagent。达到上限时，`spawn` 工具会返回错误，让 agent 自行决定等待或重排工作。若 Provider 能处理更多并行任务，可提高限制：

```json
{
  "agents": {
    "defaults": {
      "maxConcurrentSubagents": 2
    }
  }
}
```

## 自动压缩

当用户空闲超过阈值时，nanobot 可以主动把旧会话上下文压缩成摘要，同时保留最近的合法 live message 后缀。这样用户回来时，模型不必重新处理很长的陈旧上下文。

```json
{
  "agents": {
    "defaults": {
      "idleCompactAfterMinutes": 15
    }
  }
}
```

`0` 表示禁用。推荐值是 `15`。`sessionTtlMinutes` 仍作为旧别名被接受，但推荐使用 `idleCompactAfterMinutes`。

注意：自动压缩会原地重写 `sessions/<key>.jsonl`，旧结构化消息会被最近后缀和文本摘要取代。如果你依赖完整 tool-call 轨迹进行调试或审计，请保持默认 `0`，只使用 token 驱动的软 consolidation。

## 时区

默认运行时时间上下文使用 `UTC`。如需让 agent 使用本地时间，可设置有效 [IANA timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)：

```json
{
  "agents": {
    "defaults": {
      "timezone": "Asia/Shanghai"
    }
  }
}
```

常见示例：`UTC`、`America/New_York`、`America/Los_Angeles`、`Europe/London`、`Europe/Berlin`、`Asia/Tokyo`、`Asia/Shanghai`、`Asia/Singapore`、`Australia/Sydney`。

## 统一会话

默认情况下，每个通道与 chat ID 组合都有自己的会话。如果你跨多个通道使用 nanobot，并希望它们共享同一段对话，请启用 `unifiedSession`：

```json
{
  "agents": {
    "defaults": {
      "unifiedSession": true
    }
  }
}
```

| 行为 | `false`（默认） | `true` |
|----------|-------------------|--------|
| Session key | `channel:chat_id` | `unified:default` |
| 跨通道连续性 | 否 | 是 |
| `/new` 清理 | 当前通道会话 | 共享会话 |
| `/stop` 查找任务 | 按通道会话 | 按共享会话 |
| 已有 `session_key_override` | 保留 | 仍保留 |

该功能面向单用户多设备场景，默认关闭，不会影响现有用户。

## 禁用 Skills

nanobot 内置 skills，工作区也可以在 `skills/` 下定义自定义 skills。如需对 agent 隐藏特定 skill，请将 `agents.defaults.disabledSkills` 设为 skill 目录名列表：

```json
{
  "agents": {
    "defaults": {
      "disabledSkills": ["github", "weather"]
    }
  }
}
```

被禁用的 skills 会从主 agent 的 skill 摘要、always-on skill 注入和 subagent skill 摘要中排除。

## 工具提示最大长度

工具提示是 agent 调用工具时显示的短进度消息，例如 `$ cd …/project && npm test`。默认最多 40 字符，可通过 `agents.defaults.toolHintMaxLength` 调整：

```json
{
  "agents": {
    "defaults": {
      "toolHintMaxLength": 120
    }
  }
}
```

| 选项 | 默认值 | 说明 |
|--------|---------|-------------|
| `agents.defaults.toolHintMaxLength` | `40` | 工具提示显示的最大字符数。范围：20-500。 |
