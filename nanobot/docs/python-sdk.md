# Python SDK

把 nanobot 当作库使用，不需要 CLI，不需要 gateway，只需要 Python。

## 快速开始

```python
import asyncio

from nanobot import Nanobot


async def main() -> None:
    bot = Nanobot.from_config()
    result = await bot.run("What time is it in Tokyo?")
    print(result.content)


asyncio.run(main())
```

`Nanobot.from_config()` 会复用常规的 `~/.nanobot/config.json`，所以除非你显式覆盖，否则 SDK 会使用与 CLI 相同的 Provider、模型、工具和工作区默认值。

## 常见模式

### 使用指定配置或工作区

```python
from nanobot import Nanobot

bot = Nanobot.from_config(
    config_path="~/.nanobot/config.json",
    workspace="/my/project",
)
```

### 使用 `session_key` 隔离对话

不同 session key 会保留独立的对话历史：

```python
await bot.run("hi", session_key="user-alice")
await bot.run("hi", session_key="task-42")
```

### 挂载 hook 以便观测

hook 让你可以查看工具调用、流式输出和迭代状态，而无需修改 nanobot 内部实现：

```python
from nanobot.agent import AgentHook, AgentHookContext


class AuditHook(AgentHook):
    async def before_execute_tools(self, context: AgentHookContext) -> None:
        for tc in context.tool_calls:
            print(f"[tool] {tc.name}")


result = await bot.run("Review this change", hooks=[AuditHook()])
```

## API 参考

### `Nanobot.from_config(config_path=None, *, workspace=None)`

从配置文件创建 `Nanobot` 实例。

| 参数 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `config_path` | `str \| Path \| None` | `None` | `config.json` 的路径。默认是 `~/.nanobot/config.json`。 |
| `workspace` | `str \| Path \| None` | `None` | 覆盖配置中的工作区目录。 |

如果显式配置路径不存在，会抛出 `FileNotFoundError`。

### `await bot.run(message, *, session_key="sdk:default", hooks=None)`

运行一次 agent，并返回 `RunResult`。

| 参数 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `message` | `str` | *必填* | 要处理的用户消息。 |
| `session_key` | `str` | `"sdk:default"` | 用于对话隔离的会话标识。不同 key 会拥有独立历史。 |
| `hooks` | `list[AgentHook] \| None` | `None` | 仅用于本次运行的生命周期 hook。 |

### `RunResult`

| 字段 | 类型 | 说明 |
|-------|------|-------------|
| `content` | `str` | agent 的最终文本回复。 |
| `tools_used` | `list[str]` | 预留给更丰富的 SDK 自省能力；当前版本中可能为空。 |
| `messages` | `list[dict]` | 预留给更丰富的 SDK 自省能力；当前版本中可能为空。 |

## Hooks

hook 让你可以观察或定制 agent loop。继承 `AgentHook`，并按需覆盖对应方法。

### Hook 生命周期

| 方法 | 调用时机 |
|--------|------|
| `wants_streaming()` | 如果希望逐 token 接收 `on_stream()` 回调，则返回 `True` |
| `before_iteration(context)` | 每次 LLM 调用前 |
| `on_stream(context, delta)` | 启用 streaming 时，每个流式 token 到达时 |
| `on_stream_end(context, *, resuming)` | 流式输出结束时 |
| `before_execute_tools(context)` | 工具执行前 |
| `after_iteration(context)` | 每次迭代后 |
| `finalize_content(context, content)` | 转换最终输出文本 |

`AgentHookContext` 中常用字段包括：

- `iteration`
- `messages`
- `response`
- `usage`
- `tool_calls`
- `tool_results`
- `tool_events`
- `final_content`
- `stop_reason`
- `error`

### 示例：审计工具调用

```python
from nanobot.agent import AgentHook, AgentHookContext


class AuditHook(AgentHook):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[str] = []

    async def before_execute_tools(self, context: AgentHookContext) -> None:
        for tc in context.tool_calls:
            self.calls.append(tc.name)
            print(f"[audit] {tc.name}({tc.arguments})")
```

```python
hook = AuditHook()
result = await bot.run("List files in /tmp", hooks=[hook])
print(result.content)
print(f"Tools observed: {hook.calls}")
```

### 示例：接收流式 token

```python
from nanobot.agent import AgentHook, AgentHookContext


class StreamingHook(AgentHook):
    def wants_streaming(self) -> bool:
        return True

    async def on_stream(self, context: AgentHookContext, delta: str) -> None:
        print(delta, end="", flush=True)

    async def on_stream_end(self, context: AgentHookContext, *, resuming: bool) -> None:
        print()
```

### 组合多个 hook

当你想组合多个行为时，可以传入多个 hook：

```python
result = await bot.run("hi", hooks=[AuditHook(), MetricsHook()])
```

异步 hook 方法会 fan-out 执行，并隔离错误。`finalize_content` 是一个 pipeline：每个 hook 接收前一个 hook 的输出。

### 示例：后处理最终内容

```python
from nanobot.agent import AgentHook


class Censor(AgentHook):
    def finalize_content(self, context, content):
        return content.replace("secret", "***") if content else content
```

## 完整示例

```python
import asyncio
import time

from nanobot import Nanobot
from nanobot.agent import AgentHook, AgentHookContext


class TimingHook(AgentHook):
    def __init__(self) -> None:
        super().__init__()
        self._started_at = 0.0

    async def before_iteration(self, context: AgentHookContext) -> None:
        self._started_at = time.perf_counter()

    async def after_iteration(self, context: AgentHookContext) -> None:
        elapsed_ms = (time.perf_counter() - self._started_at) * 1000
        print(f"[timing] iteration {context.iteration} took {elapsed_ms:.1f}ms")


async def main() -> None:
    bot = Nanobot.from_config(workspace="/my/project")
    result = await bot.run(
        "Explain the main function",
        session_key="sdk:demo",
        hooks=[TimingHook()],
    )
    print(result.content)


asyncio.run(main())
```
