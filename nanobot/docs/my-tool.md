# My Tool

让 agent 感知并调整自己的运行时状态，就像问同事：“你现在忙吗？能不能换个更大的显示器？”

## 为什么需要它

普通工具让 agent 操作外部世界（读写文件、搜索代码）。但 agent 对自己一无所知，它不知道自己正在使用哪个模型、还剩多少轮迭代，或已经消耗了多少 token。

My Tool 用来填补这个空白。借助它，agent 可以：

- **知道自己是谁**：我正在使用什么模型？工作区在哪里？还剩多少次迭代？
- **即时适应**：任务复杂？扩大上下文窗口。只是简单聊天？切换到更快的模型。
- **跨轮记忆**：把备注存入 scratchpad，并在下一轮对话中继续保留。

## 配置

默认启用（只读模式）。agent 可以检查自己的状态，但不能修改状态。

```yaml
tools:
  my:
    enable: true       # default: true
    allow_set: false   # default: false (read-only)
```

如果要允许 agent 修改自己的配置（例如切换模型、调整参数），请设置 `tools.my.allow_set: true`。

旧版 `tools.myEnabled` / `tools.mySet` 键会在加载时自动迁移，并在下次 `nanobot onboard` 刷新配置时原地重写。

所有修改都只保存在内存中，重启后会恢复默认值。

---

## check - 检查当前“my”状态

不带参数时，会返回关键配置概览：

```text
my(action="check")
# → max_iterations: 40
#   context_window_tokens: 65536
#   model: 'anthropic/claude-sonnet-4-20250514'
#   workspace: PosixPath('/tmp/workspace')
#   provider_retry_mode: 'standard'
#   max_tool_result_chars: 16000
#   _current_iteration: 3
#   _last_usage: {'prompt_tokens': 45000, 'completion_tokens': 8000}
#   Note: prompt_tokens is cumulative across all turns, not current context window occupancy.
```

带 `key` 参数时，可以深入查看特定配置：

```text
my(action="check", key="_last_usage.prompt_tokens")
# → How many prompt tokens I've used so far

my(action="check", key="model")
# → What model I'm currently running on

my(action="check", key="web_config.enable")
# → Whether web search is enabled
```

### 可以用它做什么

| 场景 | 方法 |
|----------|-----|
| “你正在使用什么模型？” | `check("model")` |
| “你还能调用多少次工具？” | `check("max_iterations")` 减去 `check("_current_iteration")` |
| “这次对话用了多少 token？” | `check("_last_usage")`，它是所有轮次的累计值 |
| “你的工作目录在哪里？” | `check("workspace")` |
| “显示完整配置” | `check()` |
| “有没有子 agent 正在运行？” | `check("subagents")`，显示阶段、迭代次数、耗时和工具事件 |

---

## set - 运行时调优

修改会立即生效，无需重启。

```text
my(action="set", key="max_iterations", value=80)
# → Bump iteration limit from 40 to 80

my(action="set", key="model", value="fast-model")
# → Switch to a faster model

my(action="set", key="context_window_tokens", value=131072)
# → Expand context window for long documents
```

你也可以在 scratchpad 中存储自定义状态：

```text
my(action="set", key="current_project", value="nanobot")
my(action="set", key="user_style_preference", value="concise")
my(action="set", key="task_complexity", value="high")
# → These values persist into the next conversation turn
```

### 受保护参数

这些参数带有类型和范围校验，无效值会被拒绝：

| 参数 | 类型 | 范围 | 用途 |
|-----------|------|-------|---------|
| `max_iterations` | int | 1-100 | 每轮对话最大工具调用次数 |
| `context_window_tokens` | int | 4,096-1,000,000 | 上下文窗口大小 |
| `model` | str | 非空 | 使用的 LLM 模型 |

其他参数（例如 `workspace`、`provider_retry_mode`、`max_tool_result_chars`）可以自由设置，只要值是 JSON-safe 的。

---

## 实用场景

### “这个任务很复杂，我需要更多空间”

```text
Agent: This codebase is large, let me expand my context window to handle it.
→ my(action="set", key="context_window_tokens", value=131072)
```

### “简单问题，不要浪费算力”

```text
Agent: This is a straightforward question, let me switch to a faster model.
→ my(action="set", key="model", value="fast-model")
```

### “跨轮记住用户偏好”

```text
Turn 1: my(action="set", key="user_prefers_concise", value=True)
Turn 2: my(action="check", key="user_prefers_concise")
# → True (still remembers the user likes concise replies)
```

### “自我诊断”

```text
User: "Why aren't you searching the web?"
Agent: Let me check my web config.
→ my(action="check", key="web_config.enable")
# → False
Agent: Web search is disabled — please set web.enable: true in your config.
```

### “Token 预算管理”

```text
Agent: Let me check how much budget I have left.
→ my(action="check", key="_last_usage")
# → {"prompt_tokens": 45000, "completion_tokens": 8000}
Agent: I've used ~53k tokens total so far. I'll keep my remaining replies concise.
```

### “子 agent 监控”

```text
Agent: Let me check on the background tasks.
→ my(action="check", key="subagents")
# → 2 subagent(s):
#   [task-1] 'Code review'
#     phase: running, iteration: 5, elapsed: 12.3s
#     tools: read(✓), grep(✓)
#     usage: {'prompt_tokens': 8000, 'completion_tokens': 1200}
#   [task-2] 'Write tests'
#     phase: pending, iteration: 0, elapsed: 0.2s
#     tools: none
Agent: The code review is progressing well. The test task hasn't started yet.
```

---

## 安全机制

核心设计原则：**所有修改只存在于内存中。重启会恢复默认值。** agent 无法造成持久破坏。

### 禁区（已阻止）

不能检查或修改，完全隐藏：

| 类别 | 属性 | 原因 |
|----------|-----------|--------|
| 核心基础设施 | `bus`、`provider`、`_running` | 修改会导致系统崩溃 |
| 工具注册表 | `tools` | 不能移除自己的工具 |
| 子系统 | `runner`、`sessions`、`consolidator` 等 | 会影响其他用户或会话 |
| 敏感数据 | `_mcp_servers`、`_pending_queues` 等 | 包含凭据和消息路由 |
| 安全边界 | `restrict_to_workspace`、`channels_config` | 绕过会破坏隔离 |
| Python 内部结构 | `__class__`、`__dict__` 等 | 防止沙箱逃逸 |

### 只读（只能 check）

可以检查，但不能设置：

| 类别 | 属性 | 原因 |
|----------|-----------|--------|
| 子 agent 管理器 | `subagents` | 可观察，但替换会破坏系统 |
| 执行配置 | `exec_config` | 可以检查沙箱/启用状态，不能修改 |
| Web 配置 | `web_config` | 可以检查启用状态，不能修改 |
| 迭代计数器 | `_current_iteration` | 只能由 runner 更新 |

### 敏感字段保护

匹配敏感名称的子字段（`api_key`、`password`、`secret`、`token` 等）会被同时禁止 check 和 set，无论其父路径是什么。这可以防止通过 dot-path 遍历泄露凭据，例如 `web_config.search.api_key`。
