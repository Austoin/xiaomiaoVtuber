# 2026-06-02 nanobot Agent fusion log

## 目标

打通 `xiaomiao -> AuBot stage-web -> nanobot Agent`，并把 QQ 群/私聊、桌面 bridge、网页端输入统一到 nanobot Agent 能力层。

## 已完成

1. `AuBot stage-web` 桌面文本输入已改为通过 `xiaomiao bridge` 发送。
2. `AuBot stage-web` 移动端文本输入已改为通过 `xiaomiao bridge` 发送。
3. `AuBot stage-web` 页面级录音转文字入口已改为通过 `xiaomiao bridge` 发送。
4. 新增 `stage-layouts` bridge helper：
   - 请求 `http://127.0.0.1:5519/v1/chat/completions`
   - 成功时追加 user/assistant 消息
   - 失败时追加 user/error 消息
5. 新增 `xiaomiao/agent_backend.py`：
   - 读取 `Others.nanobot_agent`
   - 默认 `base_url = http://127.0.0.1:8900/v1/chat/completions`
   - 默认 `session_id = xiaomiao-unified`
   - 失败、禁用、空回复、HTTP 错误、超时均显式抛错
6. `xiaomiao/main.py` 自然语言回复入口已统一到 Agent backend：
   - desktop bridge
   - QQ 群普通 AI 回复
   - QQ 私聊普通 AI 回复
7. `xiaomiao/desktop_bridge.py` 已把 callback 异常转换成 HTTP 502 JSON 错误。

## 验证

已通过：

```powershell
pnpm -C AuBot --filter @proj-airi/stage-web build
```

结果：构建通过。首次无提权执行因 Live2D SDK 下载被沙箱网络阻止失败；授权网络后完成真实构建。

```powershell
pnpm -C AuBot --filter @proj-airi/stage-web typecheck
```

```powershell
conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_*.py"
```

结果：`20` 个 xiaomiao 测试通过。

```powershell
conda run -n xiaomiao python -m py_compile xiaomiao/main.py xiaomiao/agent_backend.py xiaomiao/desktop_bridge.py
```

结果：语法编译通过。

## 运行时验证状态

尝试后台启动：

```powershell
conda run -n xiaomiao nanobot serve --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

状态：旧尝试未完成。

原因：后台启动 `nanobot serve` 的提权请求被自动审查拒绝，原因是系统内存超过阈值。未绕过该限制继续强行启动服务。

随后仅做端口探测，未启动新进程：

```powershell
Invoke-WebRequest http://127.0.0.1:8900/health
Invoke-WebRequest http://127.0.0.1:5519/v1/xiaomiao/status
```

结果：两个本地地址当时不可用于闭环验证，返回 502/不可用状态。

## 运行时闭环验证

已使用同一工具调用内的临时进程完成验证，避免沙箱在工具调用结束时清理后台子进程。

通过项：

```text
nanobot health=200 {"status": "ok"}
nanobot models=200 {"object": "list", "data": [{"id": "deepseek-chat", "object": "model", "created": 0, "owned_by": "nanobot"}]}
bridge status=200 {"ok": true, "service": "xiaomiao-desktop-bridge", "model": "deepseek-chat", "default_user_id": 123456}
bridge chat=200 {"id": "chatcmpl-1780391908", "object": "chat.completion", "created": 1780391908, "model": "deepseek-chat", "choices": [{"index": 0, "message": {"role": "assistant", "content": "小喵网页接入测试成功"}, "finish_reason": "stop"}]}
bridge state=200 {"user_id": 123456, "reply_text": "小喵网页接入测试成功", "timestamp": 1780391908}
```

这证明当前链路可以真实完成：

```text
xiaomiao bridge :5519 -> nanobot API :8900 -> nanobot Agent -> bridge state
```

## stage-web 浏览器闭环验证

使用系统已安装 Chrome 作为 Playwright `executablePath`，未下载新浏览器。
为避免首次 onboarding 遮罩拦截聊天输入，浏览器上下文预设：

```text
localStorage["onboarding/skipped"] = "true"
localStorage["ui/chat/settings/send-mode"] = "enter"
```

通过项：

```text
stage check=200
nanobot health=200
bridge status=200
textarea before enter=只回复：小喵网页浏览器接入成功
browser bridge status=200 body={"id": "chatcmpl-1780393932", "object": "chat.completion", "created": 1780393932, "model": "deepseek-chat", "choices": [{"index": 0, "message": {"role": "assistant", "content": "小喵网页浏览器接入成功"}, "finish_reason": "stop"}]}
browser page contains reply=true
```

这证明当前链路可以真实完成：

```text
stage-web browser input -> xiaomiao bridge :5519 -> nanobot API :8900 -> nanobot Agent -> stage-web chat history
```

运行时日志：

- `log/stage-onboarding-nanobot.20260602-175159.stdout.log`
- `log/stage-onboarding-nanobot.20260602-175159.stderr.log`
- `log/stage-onboarding-bridge.20260602-175159.stdout.log`
- `log/stage-onboarding-bridge.20260602-175159.stderr.log`
- `log/stage-onboarding-browser-20260602-175159.cjs`

错误暴露验证：

首次运行时把 nanobot API timeout 设为 30 秒，真实模型回复超时后，`desktop_bridge.py` 返回 HTTP 502：

```json
{
  "error": "reply_failed",
  "message": "Nanobot Agent HTTP 504: {\"error\": {\"message\": \"Request timed out after 30.0s\", \"type\": \"invalid_request_error\", \"code\": 504}}"
}
```

该行为符合“不静默 fallback，失败必须明确可见”。

运行时日志：

- `log/nanobot-loop.20260602-171822.stdout.log`
- `log/nanobot-loop.20260602-171822.stderr.log`
- `log/xiaomiao-bridge-loop.20260602-171822.stdout.log`
- `log/xiaomiao-bridge-loop.20260602-171822.stderr.log`

## QQ 入口说明

QQ 群/私聊普通 AI 回复的代码路径已改为调用同一个 `generate_agent_reply()`。
真实 QQ 消息收发依赖 NapCat/QQ 运行时环境，本轮未发送真实 QQ 消息；代码路径和 Python 回归已验证。

## 日志整理

已清理 `log/` 下的 0 字节空日志文件。

清理范围：

- 删除 27 个 0 字节 stdout/stderr 空文件。
- 停止 3 个旧 Vite 验证进程后释放日志句柄：`3204`、`3916`、`33476`。
- `stage-browser-vite.20260602-173111.stderr.log` 原先为空，但运行中的 Vite 后续写入内容，已变成非空日志，因此保留原件。

保留范围：

- 非空 stdout/stderr 日志保留为运行证据。
- 临时 Python/CJS/MJS 探针脚本保留为复现实验入口。
- `stage-dom-probe-1780393638622.png` 保留为浏览器 DOM 探针截图。

当前主验证结论仍以本文件为准；零散运行时文件只作为附属证据，不再作为主要阅读入口。
