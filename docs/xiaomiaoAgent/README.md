# xiaomiaoAgent 集成说明

`xiaomiaoAgent` 是本项目统一 Agent 能力层。内部 Python 包名仍是 `nanobot`，命令入口同时支持 `xiaomiao` 和 `nanobot`。

## 职责

| 能力 | 说明 |
|------|------|
| Agent Loop | 负责多轮任务、上下文、工具调用和回复生成 |
| 记忆层 | 支持 session、历史、Dream 和记忆恢复 |
| OpenAI 兼容 API | 提供 `POST /v1/chat/completions`，供 QQ 和 bridge 调用 |
| gateway | 提供 WebUI、WebSocket、会话 API 和多通道入口 |
| 工具层 | 文件、搜索、Web、Shell、MCP、Cron、Notebook、Subagent、图片等 |
| xiaomiaoVirtual 工具 | 文档转 Markdown、网页抓取、舞台动作、xiaomiaobot 服务状态 |

## 运行入口

初始化本地配置：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
conda activate xiaomiao
xiaomiao onboard --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json --workspace F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\workspace
```

启动 OpenAI 兼容 API：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
conda activate xiaomiao
python -m xiaomiao_agent serve --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

启动 gateway：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
conda activate xiaomiao
python -m xiaomiao_agent gateway --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

命令行聊天：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
conda activate xiaomiao
xiaomiao agent --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

## API 请求元数据

QQ 和 bridge 会把来源和权限写入请求体：

```json
{
  "channel": "qq-group",
  "chat_id": "10001",
  "user_id": "3554978979",
  "session_id": "xiaomiao-unified",
  "tool_policy": "low_risk",
  "confirmation_id": "ABC123"
}
```

常见 `tool_policy`：

| 值 | 含义 |
|----|------|
| `low_risk` | 只暴露低风险工具 |
| `trusted_pending` | 已识别高风险请求，但还未确认 |
| `trusted_confirmed` | 用户已二次确认，可暴露高风险工具 |

## QQ 工具权限

普通 QQ 群用户默认是 `low_risk`。低风险工具包括：

- 文件读取和搜索类工具。
- Web 搜索和公网网页抓取。
- `markitdown_convert` 文档转 Markdown。
- `scrapling_get` 公网网页正文抽取。
- xiaomiaobot 状态查询。

高风险能力必须是 ROOT、Super 或 Agent 工具白名单用户，并且通过确认码后才执行：

- `exec` 和本机命令。
- 写文件或修改工作区。
- MCP 动作。
- 桌面、终端、浏览器、Minecraft、Twitter、HomeAssistant 等外部动作。
- 记忆恢复。

## xiaomiaoVirtual 已接入工具

| 工具 | 状态 | 用途 |
|------|------|------|
| `markitdown_convert` | 已接入 | QQ 文档、workspace 文件转 Markdown |
| `scrapling_get` | 已接入 | 公网网页正文抽取 |
| `xiaomiao_stage` | 已接入 | 发布字幕、TTS、表情、背景、模型等舞台事件 |
| `xiaomiaobot_status` | 已接入 | 查询 xiaomiaobot 服务和 bridge 状态 |
| `xiaomiaobot_action` | 部分接入 | 当前端到端可执行 stage 动作 |
| Computer Use MCP | 配置档可启用 | 本机窗口、终端、浏览器操作 |
| Minecraft MCP | 配置档可启用 | 状态查询和游戏动作 |
| Twitter MCP | 配置档可启用 | 搜索读取和账号动作 |

## 配置来源

`xiaomiaoAgent/.nanobot/config.json` 保存 Agent 工作区、通道、工具和运行时配置。

启动时会向上查找项目根 `config.json`，并用其中的 `xiaomiaoAgent` / `xiaomiao_agent` 段覆盖模型和运行配置。也可以通过环境变量指定统一配置：

```powershell
set XIAOMIAO_UNIFIED_CONFIG=F:\xiaomiaoVirtual\config.json
```

推荐根配置结构见 [scripts-and-config.md](../scripts-and-config.md)。

## 相关文档

- 工具目录清单：[tools.md](tools.md)
- 原始 Agent 文档：[../../xiaomiaoAgent/docs/README.md](../../xiaomiaoAgent/docs/README.md)
- OpenAI 兼容 API：[../../xiaomiaoAgent/docs/openai-api.md](../../xiaomiaoAgent/docs/openai-api.md)
- 记忆：[../../xiaomiaoAgent/docs/memory.md](../../xiaomiaoAgent/docs/memory.md)
- 启动说明：[../STARTUP.md](../STARTUP.md)
- 验证矩阵：[../verification.md](../verification.md)
