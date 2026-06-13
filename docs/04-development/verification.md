# 验证与验收

本文列出本项目常用验证命令。日常改动优先跑与本次修改相关的最小矩阵，跨子系统改动再跑完整矩阵。

## 一键启动检查

只检查端口、配置和健康状态，不启动新窗口：

```powershell
cd <项目根目录>
cmd /c call start-all.cmd --check
```

环境检查：

```powershell
cd <项目根目录>
cmd /c call setup-env.cmd --check
```

## xiaomiao 测试

```powershell
cd <项目根目录>
python -m pytest --basetemp .pytest-tmp-xiaomiao-verify test\xiaomiao
```

当前预期：

```text
78 passed
```

覆盖重点：

- QQ Agent 后端调用。
- QQ 工具权限和私聊裸消息入口。
- QQ 文件下载与 workspace。
- 桥接服务持久化和状态接口。
- 人设切换和控制台输出。

## xiaomiaoAgent 测试

```powershell
cd <项目根目录>\xiaomiaoAgent
uv run --extra dev pytest --basetemp ..\.pytest-tmp-agent-verify tests\test_openai_api.py tests\tools\test_tool_registry.py tests\tools\test_tool_loader.py tests\tools\test_computer_use_mcp_profile.py tests\tools\test_markitdown_tool.py tests\tools\test_scrapling_tool.py tests\tools\test_xiaomiao_stage_tool.py tests\tools\test_xiaomiaobot_services_tool.py
```

当前预期：

```text
97 passed
```

覆盖重点：

- OpenAI 兼容 API。
- 工具注册和工具风险过滤。
- MarkItDown 文档转换。
- Scrapling 网页抽取。
- xiaomiaobot 舞台和服务工具。
- Computer Use MCP 安全配置档。

## xiaomiaobot 桥接事件测试

```powershell
cd <项目根目录>\xiaomiaobot
pnpm exec vitest run apps/stage-pocket/src/modules/xiaomiao-bridge-events.test.ts packages/stage-ui/src/xiaomiao-bridge-events.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.test.ts apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.test.ts
```

当前预期：

```text
4 files / 32 tests passed
```

覆盖重点：

- bridge event 渲染。
- tool start / finish / error 同步。
- stage action 事件。
- 桌面端 bridge reaction。

## 文档和脚本格式检查

```powershell
cd <项目根目录>
git diff --check
```

该命令会检查空白格式问题。Windows 下可能出现 LF/CRLF warning，只要没有 whitespace error 即可。

## 联调验收

| 场景 | 预期 |
|------|------|
| QQ 发送 `- 记忆状态` | 返回 xiaomiaoAgent 状态 |
| QQ 发送 `- 整理记忆` | 触发 Dream 和记忆事件 |
| QQ 普通用户请求本机命令 | 明确拒绝 |
| QQ 白名单用户请求本机命令 | 直接执行高风险 Agent 工具 |
| QQ 私聊裸发自然语言 | 不加 `-` 也进入 Agent |
| QQ 私聊发送图片/表情包/文档 | 默认下载或转媒体后交给 Agent |
| QQ 上传文档后提问 | 保存到 `workspace/downloads/qq/` 并可转 Markdown |
| QQ 请求抓取公网网页 | 调用 `scrapling_get` 返回摘要 |
| stage-web 输入文本 | 通过 bridge 进入统一 Agent |
| stage-tamagotchi 在线 | 能消费字幕、TTS、聊天和舞台事件 |

## 最小回归建议

| 修改范围 | 建议验证 |
|----------|----------|
| 只改文档 | `git diff --check` |
| 改 `xiaomiao/` | `python -m pytest --basetemp .pytest-tmp-xiaomiao-verify test\xiaomiao` |
| 改 `xiaomiaoAgent/` 工具或 API | xiaomiaoAgent 相关 pytest |
| 改 `xiaomiaobot` bridge / stage | 指定 Vitest bridge 测试 |
| 改启动脚本 | `setup-env.cmd --check` 和 `start-all.cmd --check` |
| 跨系统改动 | 跑完整最小矩阵 |
