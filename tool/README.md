# tool/ 目录 - xiaomiaoVirtual 统一工具层

> **版本**: 1.0.0  
> **创建时间**: 2026-06-13  
> **目的**: 统一管理所有工具、记忆层和第三方依赖

---

## 📋 目录结构

```
tool/
├── __init__.py                 # 统一入口
├── README.md                   # 本文件
├── REFACTOR_PLAN.md            # 重构方案文档
│
├── core/                       # 核心工具
│   ├── __init__.py
│   ├── base.py                 # 工具基类
│   ├── registry.py             # 工具注册器
│   ├── loader.py               # 工具加载器
│   ├── schema.py               # 工具 Schema
│   ├── filesystem.py           # 文件系统工具
│   ├── shell.py                # Shell 执行
│   ├── search.py               # Web 搜索
│   ├── web.py                  # Web 抓取
│   ├── mcp.py                  # MCP 服务器
│   ├── cron.py                 # 定时任务
│   ├── notebook.py             # Notebook 编辑
│   ├── spawn.py                # 子 Agent
│   ├── self.py                 # 自修改
│   ├── message.py              # 消息工具
│   ├── ask.py                  # 询问工具
│   ├── image_generation.py     # 图片生成
│   └── ...                     # 其他核心工具
│
├── xiaomiao/                   # xiaomiaoVirtual 专属工具
│   ├── __init__.py
│   ├── markitdown.py           # 文档转 Markdown（MarkItDown）
│   ├── scrapling.py            # 网页正文抽取（Scrapling）
│   ├── stage.py                # 舞台动作控制
│   ├── services.py             # xiaomiaobot 服务状态
│   └── permissions.py          # QQ 权限策略
│
├── memory/                     # 记忆层
│   ├── __init__.py
│   └── store.py                # 记忆存储、整理和 Dream
│
├── vendor/                     # 第三方源码
│   ├── __init__.py
│   ├── markitdown/             # MarkItDown 完整源码
│   └── scrapling/              # Scrapling 完整源码
│
└── adapters/                   # 调用适配器
    ├── __init__.py
    ├── nanobot_adapter.py      # xiaomiaoAgent 适配
    ├── qq_adapter.py           # QQ Bot 适配
    └── tui_adapter.py          # TUI 适配
```

---

## 🎯 设计目标

### 1. 统一管理
所有工具集中在 `tool/` 目录，便于维护和扩展。

### 2. 清晰分层
- **core**: 通用工具（文件、Shell、Web、MCP 等）
- **xiaomiao**: 项目专属工具
- **memory**: 记忆系统
- **vendor**: 第三方源码
- **adapters**: 调用适配

### 3. 解耦调用
通过适配器解耦不同入口的调用逻辑，保持各入口独立。

### 4. 向后兼容
保持原有导入路径可用，渐进式迁移。

---

## 🔌 使用方式

### xiaomiaoAgent (nanobot)

原有导入路径继续有效：
```python
from nanobot.agent.tools import ToolRegistry, Tool
from nanobot.agent.tools.filesystem import list_dir, read_file
```

内部已自动重定向到 `tool/core/`。

### xiaomiao QQ Bot

使用适配器：
```python
from tool.adapters.qq_adapter import decide_tool_request, get_tool_policy

# 获取用户工具策略
tool_policy = get_tool_policy(user_id, has_permission)

# 判断工具调用
decision = decide_tool_request(
    text=message,
    user_id=user_id,
    chat_id=chat_id,
    has_tool_permission=has_permission
)
```

### TUI 终端

TUI 通过 xiaomiaoAgent 间接调用，无需修改。

---

## 📚 核心工具列表

### 文件系统
- `read_file` - 读取文件
- `write_file` - 写入文件
- `edit_file` - 编辑文件
- `list_dir` - 列出目录
- `glob` - 文件匹配
- `grep` - 文本搜索

### Shell
- `exec` - 执行命令

### Web
- `web_search` - Web 搜索
- `web_fetch` - 抓取网页

### MCP
- `mcp_*` - MCP 工具集成

### 其他
- `cron` - 定时任务
- `spawn` - 子 Agent
- `message` - 发送消息
- `ask` - 询问用户
- `generate_image` - 图片生成

---

## 🔧 项目专属工具

### markitdown
```python
from tool.xiaomiao.markitdown import MarkitdownTool

# 文档转 Markdown
result = markitdown_convert(path="document.pdf")
```

### scrapling
```python
from tool.xiaomiao.scrapling import ScraplingTool

# 网页正文抽取
result = scrapling_get(url="https://example.com")
```

### stage
```python
from tool.xiaomiao.stage import XiaomiaoStageTool

# 舞台动作控制
result = xiaomiao_stage(action="tts", text="Hello")
```

### services
```python
from tool.xiaomiao.services import XiaomiaobotServicesTool

# 查询 xiaomiaobot 服务状态
result = xiaomiaobot_status()
```

### last30days ⭐ 新增
```python
from tool.xiaomiao.last30days import last30days_research

# 多平台研究（Reddit、X、YouTube、GitHub 等）
result = last30days_research(
    topic="OpenAI vs Anthropic",
    emit="html",
    save_dir="~/Documents/Research"
)

print(result["output"])      # 研究报告
print(result["save_path"])   # 保存路径
```

**Last30Days 功能**:
- 🌐 多平台搜索：Reddit、X/Twitter、YouTube、GitHub、HN、Polymarket
- 🧠 智能预研究：自动解析相关账号、频道、仓库
- 📊 真实数据：基于点赞、评论、真金白银的参与度评分
- 📄 HTML 简报：生成可分享的独立报告

**依赖**: Python 3.12+, yt-dlp (可选), 各平台 API (可选)  
**文档**: [LAST30DAYS_INTEGRATION.md](LAST30DAYS_INTEGRATION.md)

---

## 🔐 权限策略

### 低风险工具（所有用户）
- 文件读取和搜索
- Web 搜索和抓取
- markitdown 转换
- scrapling 抽取
- 服务状态查询

### 高权限工具（ROOT/Super/白名单）
- Shell 命令执行
- 文件写入和修改
- MCP 工具
- 舞台控制
- 子 Agent 启动
- 定时任务
- 消息发送

---

## 🔄 迁移说明

从旧路径迁移到新路径：

### 旧代码（继续有效）
```python
from nanobot.agent.tools import Tool
from xiaomiao.qq_agent_tools import decide_agent_tool_request
```

### 新代码（推荐）
```python
from tool.core.base import Tool
from tool.adapters.qq_adapter import decide_tool_request
```

两种方式都能正常工作，建议新代码使用新路径。

---

## ✅ 验证

### 测试 TUI
```cmd
start-tui.cmd
```

### 测试 QQ Bot
```cmd
start-all.cmd
```

### 测试 xiaomiaobot web
访问 http://127.0.0.1:5175

---

## 📝 维护指南

### 添加新工具

1. 在适当目录创建工具文件：
   - 通用工具 → `tool/core/`
   - 项目专属 → `tool/xiaomiao/`

2. 实现工具类：
```python
from tool.core.base import Tool

class MyTool(Tool):
    name = "my_tool"
    description = "..."
    
    def execute(self, **kwargs):
        # 实现
        pass
```

3. 注册工具（如需要）

### 更新第三方源码

第三方源码位于 `tool/vendor/`，独立维护。

---

## 🎉 总结

- ✅ 所有工具统一在 `tool/` 目录
- ✅ QQ、网页端、TUI 都能正常调用
- ✅ 保持向后兼容
- ✅ 清晰的分层结构
- ✅ 易于维护和扩展

**工具层重构完成！**
