# OpenAI 兼容 API

nanobot 可以暴露一个最小化的 OpenAI 兼容端点，用于本地集成：

```bash
pip install "nanobot-ai[api]"
nanobot serve
```

默认情况下，API 绑定到 `127.0.0.1:8900`。你可以在 `config.json` 中修改。

## xiaomiaoVirtual 集成

在 `xiaomiaoVirtual` 中，该端点是网页、桌面 bridge 和 QQ 普通 AI 回复的统一 Agent 能力层。推荐从仓库根目录启动项目内配置：

```powershell
cd F:\xiaomiaoVirtual
conda activate xiaomiao
nanobot serve --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

集成链路：

```text
AuBot stage-web
    ↓ POST http://127.0.0.1:5519/v1/chat/completions
xiaomiao desktop_bridge.py
    ↓
xiaomiao agent_backend.py
    ↓ POST http://127.0.0.1:8900/v1/chat/completions
nanobot OpenAI-compatible API

QQ 群/私聊普通 AI 回复
    ↓
xiaomiao generate_agent_reply()
    ↓ POST http://127.0.0.1:8900/v1/chat/completions
nanobot OpenAI-compatible API
```

`xiaomiao` 默认使用统一 session：

```json
{
  "session_id": "xiaomiao-unified"
}
```

这会让网页、桌面 bridge 和 QQ 普通 AI 回复共享同一个 Agent 上下文。命令型 QQ 功能、权限管理、生图、撤回和配置类命令仍由 `xiaomiao` 本地逻辑处理。

如果 `nanobot serve` 未启动，`xiaomiao` bridge 会返回明确 HTTP 502 错误；`stage-web` 会把错误写入聊天历史，不会静默回退到 AuBot provider。

## 行为

- 会话隔离：在请求体中传入 `"session_id"` 可隔离对话；省略时使用共享默认会话（`api:default`）。
- 单消息输入：每个请求必须且只能包含一条 `user` 消息。
- 固定模型：省略 `model`，或传入与 `/v1/models` 显示相同的模型。
- 流式输出：设置 `stream=true` 可接收 Server-Sent Events（`text/event-stream`），返回 OpenAI 兼容的 delta chunk，并以 `data: [DONE]` 结束；省略或设置 `stream=false` 时返回单个 JSON 响应。
- **文件上传**：支持通过 JSON base64 或 `multipart/form-data` 上传图片、PDF、Word（.docx）、Excel（.xlsx）、PowerPoint（.pptx），单文件最大 10MB。
- API 请求运行在合成的 `api` 通道中，因此 `message` 工具**不会**自动投递到 Telegram、Discord 等平台。若要主动发送到其他聊天，请调用 `message`，并显式传入已启用通道的 `channel` 和 `chat_id`。

API 会话中跨通道投递的工具调用示例：

```json
{
  "content": "Build finished successfully.",
  "channel": "telegram",
  "chat_id": "123456789"
}
```

如果 `channel` 指向配置中未启用的通道，nanobot 会将出站事件入队，但不会发生平台投递。

## 端点

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`

## curl

```bash
curl http://127.0.0.1:8900/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "hi"}],
    "session_id": "my-session"
  }'
```

## 文件上传（JSON base64）

使用 OpenAI 多模态内容格式内联发送图片：

```bash
curl http://127.0.0.1:8900/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": [
      {"type": "text", "text": "Describe this image"},
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBOR..."}}
    ]}]
  }'
```

## 文件上传（multipart/form-data）

通过 multipart 上传任意受支持文件类型（图片、PDF、Word、Excel、PPT）：

```bash
# 单个文件
curl http://127.0.0.1:8900/v1/chat/completions \
  -F "message=Summarize this report" \
  -F "files=@report.docx"

# 多个文件，并隔离会话
curl http://127.0.0.1:8900/v1/chat/completions \
  -F "message=Compare these files" \
  -F "files=@chart.png" \
  -F "files=@data.xlsx" \
  -F "session_id=my-session"
```

支持的文件类型：

- **图片**：PNG、JPEG、GIF、WebP（以 base64 发送给 AI 进行视觉分析）。
- **文档**：PDF、Word（.docx）、Excel（.xlsx）、PowerPoint（.pptx）（提取文本后发送给 AI）。
- **文本**：TXT、Markdown、CSV、JSON 等（直接读取）。

## Python（`requests`）

```python
import requests

resp = requests.post(
    "http://127.0.0.1:8900/v1/chat/completions",
    json={
        "messages": [{"role": "user", "content": "hi"}],
        "session_id": "my-session",  # optional: isolate conversation
    },
    timeout=120,
)
resp.raise_for_status()
print(resp.json()["choices"][0]["message"]["content"])
```

## Python（`openai`）

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8900/v1",
    api_key="dummy",
)

resp = client.chat.completions.create(
    model="MiniMax-M2.7",
    messages=[{"role": "user", "content": "hi"}],
    extra_body={"session_id": "my-session"},  # optional: isolate conversation
)
print(resp.choices[0].message.content)
```
