# xiaomiaoAgent 工具系统重组方案

## 目标

将 xiaomiaoAgent 的工具系统按功能领域重新组织,提高代码可维护性和可发现性。

## 当前问题

**tools/ 目录现状** (27 个文件平铺):
```
tools/
├── ask.py                    # 交互
├── base.py                   # 基类
├── context.py                # 上下文
├── cron.py                   # 定时任务
├── filesystem.py             # 文件系统
├── file_state.py             # 文件状态
├── image_generation.py       # 图片生成
├── loader.py                 # 加载器
├── markitdown_tool.py        # 文档转换
├── mcp.py                    # MCP 协议
├── message.py                # 消息
├── notebook.py               # Notebook
├── registry.py               # 注册表
├── runtime_state.py          # 运行时状态
├── sandbox.py                # 沙箱
├── schema.py                 # Schema
├── scrapling_tool.py         # 网页抓取
├── search.py                 # 搜索
├── self.py                   # 自修改
├── shell.py                  # Shell
├── spawn.py                  # 子进程
├── web.py                    # Web
├── xiaomiao_stage.py         # 舞台动作
├── xiaomiaobot_services.py   # xiaomiaobot 服务
├── xiaomiao_tools.py         # xiaomiao 工具
├── _repo_tool_source.py      # 仓库工具
└── __init__.py
```

**问题**:
1. 文件过多,难以浏览
2. 缺少逻辑分组
3. 功能边界不清晰
4. 新人难以快速定位

## 目标架构

```
nanobot/agent/tools/
├── __init__.py                    # 导出所有工具
│
├── core/                          # 核心基础设施
│   ├── __init__.py
│   ├── base.py                    # 工具基类
│   ├── registry.py                # 工具注册表
│   ├── loader.py                  # 工具加载器
│   ├── schema.py                  # Schema 定义
│   └── context.py                 # 上下文管理
│
├── filesystem/                    # 文件系统工具
│   ├── __init__.py
│   ├── operations.py              # 文件操作 (原 filesystem.py)
│   ├── state.py                   # 文件状态 (原 file_state.py)
│   └── notebook.py                # Notebook 编辑
│
├── execution/                     # 执行相关工具
│   ├── __init__.py
│   ├── shell.py                   # Shell 执行
│   ├── sandbox.py                 # 沙箱执行
│   ├── spawn.py                   # 子进程管理
│   └── runtime.py                 # 运行时状态 (原 runtime_state.py)
│
├── web/                           # 网络工具
│   ├── __init__.py
│   ├── fetch.py                   # 基础 Web 请求 (原 web.py)
│   ├── search.py                  # 搜索
│   └── scraping.py                # 网页抓取 (原 scrapling_tool.py)
│
├── conversion/                    # 格式转换工具
│   ├── __init__.py
│   └── markitdown.py              # 文档转 Markdown (原 markitdown_tool.py)
│
├── interaction/                   # 交互工具
│   ├── __init__.py
│   ├── ask.py                     # 询问用户
│   └── message.py                 # 消息发送
│
├── generation/                    # 生成工具
│   ├── __init__.py
│   └── image.py                   # 图片生成 (原 image_generation.py)
│
├── scheduling/                    # 调度工具
│   ├── __init__.py
│   └── cron.py                    # 定时任务
│
├── external/                      # 外部集成
│   ├── __init__.py
│   ├── mcp.py                     # MCP 协议
│   ├── xiaomiao_stage.py          # xiaomiao 舞台动作
│   ├── xiaomiaobot_services.py    # xiaomiaobot 服务
│   └── xiaomiao_tools.py          # xiaomiao 通用工具
│
└── advanced/                      # 高级工具
    ├── __init__.py
    ├── self_modify.py             # 自修改 (原 self.py)
    └── repo_source.py             # 仓库工具 (原 _repo_tool_source.py)
```

## 领域划分

### 1. core/ - 核心基础设施
**职责**: 工具系统的基础框架
- 工具基类和接口
- 注册表和加载机制
- Schema 定义
- 上下文管理

### 2. filesystem/ - 文件系统工具
**职责**: 文件和目录操作
- 读写文件
- 列出目录
- 文件状态跟踪
- Notebook 编辑

### 3. execution/ - 执行相关工具
**职责**: 代码和命令执行
- Shell 命令
- 沙箱执行
- 子进程管理
- 运行时状态

### 4. web/ - 网络工具
**职责**: 网络请求和内容获取
- HTTP 请求
- 搜索引擎
- 网页抓取和解析

### 5. conversion/ - 格式转换工具
**职责**: 文件格式转换
- 文档转 Markdown
- 图片格式转换(未来)
- 数据格式转换(未来)

### 6. interaction/ - 交互工具
**职责**: 与用户交互
- 询问用户
- 发送消息
- 确认操作

### 7. generation/ - 生成工具
**职责**: 内容生成
- 图片生成
- 文本生成(未来)
- 代码生成(未来)

### 8. scheduling/ - 调度工具
**职责**: 定时和异步任务
- Cron 定时任务
- 延迟任务(未来)
- 任务队列(未来)

### 9. external/ - 外部集成
**职责**: 与外部系统集成
- MCP 协议服务器
- xiaomiao 系统集成
- xiaomiaobot 服务集成

### 10. advanced/ - 高级工具
**职责**: 高级和实验性功能
- 自修改能力
- 仓库工具源
- 元编程工具

## 迁移步骤

### 阶段 1: 创建新目录结构

```bash
cd xiaomiaoAgent/nanobot/agent/tools
mkdir -p core filesystem execution web conversion interaction generation scheduling external advanced
```

### 阶段 2: 移动文件(保持向后兼容)

**策略**: 复制 → 更新导入 → 删除原文件

```python
# 示例: filesystem/__init__.py
"""文件系统工具包"""

from .operations import (
    ReadFileTool,
    WriteFileTool,
    EditFileTool,
    ListFilesTool,
    # ... 其他工具
)
from .state import FileStateStore, bind_file_states, reset_file_states
from .notebook import NotebookEditTool

__all__ = [
    'ReadFileTool',
    'WriteFileTool',
    'EditFileTool',
    'ListFilesTool',
    'FileStateStore',
    'bind_file_states',
    'reset_file_states',
    'NotebookEditTool',
]
```

**向后兼容层** (在根 `__init__.py`):

```python
# nanobot/agent/tools/__init__.py
"""
工具系统主入口

向后兼容: 从新位置重新导出所有工具
"""

# 核心
from .core.base import Tool, ToolResult
from .core.registry import ToolRegistry
from .core.loader import ToolLoader

# 文件系统
from .filesystem import (
    ReadFileTool,
    WriteFileTool,
    EditFileTool,
    ListFilesTool,
    FileStateStore,
)

# 执行
from .execution import (
    ShellTool,
    SandboxTool,
    SpawnTool,
)

# Web
from .web import (
    WebFetchTool,
    WebSearchTool,
    ScrapingTool,
)

# 转换
from .conversion import MarkitdownTool

# 交互
from .interaction import AskTool, MessageTool

# 生成
from .generation import ImageGenerationTool

# 调度
from .scheduling import CronTool

# 外部
from .external import (
    MCPTool,
    XiaomiaoStageTool,
    XiaomiaoToolsTool,
    XiaomiaoBotServicesTool,
)

# 高级
from .advanced import MyTool

# 保持原有导入路径可用
# 旧代码: from nanobot.agent.tools.filesystem import ReadFileTool
# 新代码: from nanobot.agent.tools.filesystem import ReadFileTool
# 都能工作!

__all__ = [
    # 核心
    'Tool',
    'ToolResult',
    'ToolRegistry',
    'ToolLoader',
    
    # 文件系统
    'ReadFileTool',
    'WriteFileTool',
    'EditFileTool',
    'ListFilesTool',
    'FileStateStore',
    
    # ... 其他工具
]
```

### 阶段 3: 更新内部导入

在每个工具文件中,更新相对导入:

```python
# 旧代码 (filesystem.py)
from .base import Tool, ToolResult
from .registry import tool_registry

# 新代码 (filesystem/operations.py)
from ..core.base import Tool, ToolResult
from ..core.registry import tool_registry
```

### 阶段 4: 文档和测试更新

```python
# tests/tools/test_filesystem.py

# 旧导入
# from nanobot.agent.tools.filesystem import ReadFileTool

# 新导入 (两种都支持)
from nanobot.agent.tools.filesystem import ReadFileTool
# 或
from nanobot.agent.tools import ReadFileTool
```

### 阶段 5: 逐步废弃旧路径

在迁移完成后,添加废弃警告:

```python
# nanobot/agent/tools/filesystem.py (兼容层,最终删除)

import warnings
from .filesystem.operations import ReadFileTool  # noqa

warnings.warn(
    "直接从 nanobot.agent.tools.filesystem 导入已废弃, "
    "请使用 from nanobot.agent.tools.filesystem import ReadFileTool",
    DeprecationWarning,
    stacklevel=2,
)
```

## 文件映射表

| 原文件 | 新位置 | 说明 |
|--------|--------|------|
| `base.py` | `core/base.py` | 工具基类 |
| `registry.py` | `core/registry.py` | 注册表 |
| `loader.py` | `core/loader.py` | 加载器 |
| `schema.py` | `core/schema.py` | Schema |
| `context.py` | `core/context.py` | 上下文 |
| `filesystem.py` | `filesystem/operations.py` | 文件操作 |
| `file_state.py` | `filesystem/state.py` | 文件状态 |
| `notebook.py` | `filesystem/notebook.py` | Notebook |
| `shell.py` | `execution/shell.py` | Shell |
| `sandbox.py` | `execution/sandbox.py` | 沙箱 |
| `spawn.py` | `execution/spawn.py` | 子进程 |
| `runtime_state.py` | `execution/runtime.py` | 运行时 |
| `web.py` | `web/fetch.py` | Web 请求 |
| `search.py` | `web/search.py` | 搜索 |
| `scrapling_tool.py` | `web/scraping.py` | 抓取 |
| `markitdown_tool.py` | `conversion/markitdown.py` | 文档转换 |
| `ask.py` | `interaction/ask.py` | 询问 |
| `message.py` | `interaction/message.py` | 消息 |
| `image_generation.py` | `generation/image.py` | 图片生成 |
| `cron.py` | `scheduling/cron.py` | 定时任务 |
| `mcp.py` | `external/mcp.py` | MCP |
| `xiaomiao_stage.py` | `external/xiaomiao_stage.py` | 舞台 |
| `xiaomiaobot_services.py` | `external/xiaomiaobot_services.py` | 服务 |
| `xiaomiao_tools.py` | `external/xiaomiao_tools.py` | 工具 |
| `self.py` | `advanced/self_modify.py` | 自修改 |
| `_repo_tool_source.py` | `advanced/repo_source.py` | 仓库源 |

## 优势

1. **可发现性**: 按功能分类,快速找到相关工具
2. **可扩展性**: 每个领域独立扩展
3. **向后兼容**: 保持原有导入路径可用
4. **模块化**: 清晰的边界和职责
5. **文档化**: 每个包有明确的 README

## 风险控制

1. **双轨运行**: 保留旧文件,添加兼容层
2. **增量迁移**: 逐个包迁移
3. **测试覆盖**: 每个迁移后运行完整测试
4. **文档更新**: 同步更新所有文档

## 验证标准

- [ ] 所有测试通过
- [ ] 旧导入路径仍可用
- [ ] 新导入路径工作正常
- [ ] 文档已更新
- [ ] IDE 自动补全正常

## 时间估算

- 创建目录结构: 0.5 天
- 移动文件并更新导入: 2 天
- 测试和修复: 1 天
- 文档更新: 0.5 天
- **总计**: 4 天

## 后续优化

1. 每个包添加 README.md
2. 工具自动发现机制
3. 工具依赖管理
4. 工具性能监控
