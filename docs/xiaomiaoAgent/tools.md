# xiaomiaoAgent 工具目录清单

本文按源码文件说明 `xiaomiaoAgent/nanobot/agent/tools/` 的工具职责、QQ 可见性和风险边界。`xiaomiaoAgent` 内部包名仍是 `nanobot`，工具由 `ToolLoader` 扫描并注册，再由 `ToolRegistry` 根据请求来源和 `tool_policy` 过滤。

## 注册与权限入口

| 文件 | 作用 |
|------|------|
| `loader.py` | 扫描 `nanobot.agent.tools` 下的工具类，跳过基础模块，并加载外部 entry point `nanobot.tools` |
| `registry.py` | 保存工具、输出 schema、执行前校验；QQ `low_risk` 和高权限工具策略的最终拦截也在这里完成 |
| `base.py` | 工具抽象基类、schema 输出、参数转换、启用条件和工具元信息 |
| `schema.py` | 工具参数 schema 类型定义 |
| `context.py` | 每次请求的来源、会话和 metadata 上下文 |
| `mcp.py` | MCP 工具、资源、prompt 包装器，把外部 MCP 暴露为 Agent 工具 |
| `sandbox.py`、`file_state.py`、`runtime_state.py` | 工具运行时辅助状态，不直接作为 QQ 指令入口 |

`ToolRegistry` 的关键规则：

- `low_risk` 只暴露并执行低风险工具。
- `trusted_confirmed` 允许暴露并执行 `exec`、写文件、编辑文件、舞台动作和其它高风险工具。
- `trusted_pending` 仅作为旧 API 兼容值保留；工具层按高权限策略处理。
- 即使模型在历史上下文中伪造工具调用，`prepare_call()` 仍会按当前请求上下文拦截。
- MCP 工具按名称后缀识别低风险读取工具，其它动作默认只对高权限策略开放。

## 低风险工具

这些工具默认可供普通 QQ 用户通过 Agent 使用，但仍要经过 URL、路径和输出长度限制。

| 工具 | 文件 | 说明 |
|------|------|------|
| `read_file` | `filesystem.py` | 读取允许工作区内文件 |
| `list_dir` | `filesystem.py` | 列目录 |
| `grep` | `search.py` | 文本搜索 |
| `glob` | `search.py` | 文件名匹配 |
| `web_search` | `web.py` | Web 搜索，按配置选择 Brave、DuckDuckGo、Tavily 等 provider |
| `web_fetch` | `web.py` | 读取公网 URL 并抽取正文，阻断不安全 URL |
| `markitdown_convert` | `markitdown_tool.py` | 把 Agent 工作区或项目 `workspace/` 内文档转 Markdown |
| `scrapling_get` | `scrapling_tool.py` | 低风险公网网页正文抓取，默认主内容抽取 |
| `xiaomiaobot_status` | `xiaomiaobot_services.py` | 查询 bridge 和 xiaomiaobot 服务能力状态 |

## 高权限工具

这些工具默认不暴露给普通 QQ 用户。ROOT、Super 或 `agent_tool_allowlist` 用户会以 `trusted_confirmed` 策略进入 Agent，可直接让 Agent 看到并执行高风险工具。

| 工具 | 文件 | 风险点 |
|------|------|--------|
| `exec` | `shell.py` | 执行本机 shell 命令 |
| `write_file` | `filesystem.py` | 写入文件 |
| `edit_file` | `filesystem.py` | 修改文件内容 |
| `notebook_edit` | `notebook.py` | 修改 Notebook |
| `cron` | `cron.py` | 创建或管理定时任务 |
| `spawn` | `spawn.py` | 启动子 Agent 或外部任务 |
| `message` | `message.py` | 向外部通道发送消息 |
| `generate_image` | `image_generation.py` | 调用图像生成 provider，可能消耗额度或涉及外部服务 |
| `xiaomiao_stage` | `xiaomiao_stage.py` | 发布舞台动作事件，如 TTS、字幕、模型、背景 |
| `xiaomiaobot_action` | `xiaomiaobot_services.py` | 发布 xiaomiaobot 服务动作；当前只有 stage 动作端到端可执行 |
| MCP 非只读工具 | `mcp.py` | Computer Use、Twitter、Minecraft、HomeAssistant 等外部动作 |

## 其它内置工具

| 工具 | 文件 | 说明 |
|------|------|------|
| `ask_user` | `ask.py` | Agent 需要用户补充信息时使用 |
| `my` | `self.py` | 读取或维护 Agent 自身说明、偏好、记忆相关上下文 |
| `context` 相关模块 | `context.py` | 工具请求上下文，不直接作为用户工具使用 |

## QQ 与工具链路

```text
QQ 消息
    ↓
xiaomiao/main.py
    ↓ 用户权限识别，生成 tool_policy
xiaomiao/agent_backend.py
    ↓ tool_policy
xiaomiaoAgent API server.py
    ↓ RequestContext.metadata.channel_policy
ToolRegistry.get_definitions() / prepare_call()
    ↓
低风险工具按 low_risk 执行；高权限用户可执行高风险工具
```

普通用户看到的工具集合来自 `LOW_RISK_ALLOWED_TOOLS` 和低风险 MCP 后缀。ROOT、Super 或 `agent_tool_allowlist` 用户请求会带 `tool_policy=trusted_confirmed`，高风险工具可直接进入执行链路。`tool_policy` 只由 QQ 后端权限网关生成，用户文本中伪造字段不会生效。

## MCP 低风险后缀

MCP 工具如果名称以 `mcp_` 开头，并带有只读后缀，可在低风险策略中暴露。常见后缀包括：

- 桌面读取：`desktop_get_state`、`desktop_observe_windows`、`desktop_screenshot`、`desktop_wait`。
- 浏览器读取：`browser_dom_read_page`、`browser_dom_find_elements`、`browser_dom_get_active_tab`、`list_tabs`。
- Twitter 读取：`search_tweets`、`get_tweet`、`get_profile`、`get_timeline`。
- Minecraft / 服务状态：`get_status`、`get_state`、`get_logs`、`status`。
- 工具目录：`tool_directory`、`tool_search`。

不在低风险后缀内的 MCP 动作默认按高风险处理。

## 已知边界

- `markitdown_convert` 不允许任意本机路径、URL、`file:` 或 `data:` 输入。
- `scrapling_get` 只允许公网 `http/https`，阻断本机、内网和元数据地址。
- `xiaomiao_stage` 当前标记为高风险，因为它会改变桌面表现层状态。
- `xiaomiaobot_action` 对未接通服务会显式报错，不静默假成功。
- Computer Use、Minecraft、Twitter 需要在 Agent 配置中显式启用 MCP profile。
