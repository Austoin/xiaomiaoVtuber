# xiaomiaoAgent

`xiaomiaoAgent` 是 `xiaomiaoVirtual` 的统一智能体核心，运行于 Python 3.11 及以上版本。后端业务包名为 `nanobot`，品牌化入口包为 `xiaomiao_agent`；它提供模型 Provider、消息总线、聊天渠道、工具系统、会话记忆、定时任务、OpenAI 兼容 API、CLI/TUI 和内嵌 WebUI。

本 README 是本目录唯一的项目入口和结构维护说明。开发规则见 [`AGENTS.md`](./AGENTS.md)，主题文档见 [`docs/README.md`](./docs/README.md)。

## 项目定位

在 `xiaomiaoVirtual` 中，QQ、Web、Pocket、Electron、Discord、Telegram 和内嵌 WebUI 只负责输入输出或界面交互，推理、记忆、会话和工具执行统一由本项目完成。

```text
QQ / Web / Pocket / Electron / 聊天渠道 / CLI
                         │
                         ├─ nanobot.api：OpenAI 兼容 API、事件、配置和健康检查
                         ├─ nanobot.bus：消息类型与异步队列
                         └─ nanobot.agent：上下文、模型、工具、记忆和子 Agent
                                      │
                                      ├─ providers：模型、图像和转录服务
                                      ├─ tools：文件、Shell、Web、MCP 和媒体
                                      └─ session / cron / heartbeat
```

默认服务端口：

| 端口 | 服务 |
| --- | --- |
| `8900` | OpenAI 兼容 HTTP API、xiaomiao 事件与配置接口 |
| `18790` | Gateway 健康检查 |
| `8765` | 内嵌 WebUI 与 WebSocket 通道 |
| `5174` | WebUI 开发服务器 |

## 快速开始

### 统一入口

从仓库根目录执行：

```powershell
menu.cmd agent-api
menu.cmd agent-gateway
menu.cmd agent-webui
menu.cmd tui
```

TUI 也可以直接通过仓库级脚本启动：

```powershell
scripts\start-tui.cmd
```

### 安装与初始化

```powershell
cd xiaomiaoAgent
uv sync
uv run python -m xiaomiao_agent onboard
```

也可以在已激活的 Python 环境中安装：

```powershell
python -m pip install -e .
python -m xiaomiao_agent onboard
```

### 直接启动

以下命令均在 `xiaomiaoAgent` 目录执行：

```powershell
# 终端 Agent
uv run python -m xiaomiao_agent agent --config ..\.cache\agent\nanobot\config.json

# OpenAI 兼容 API
uv run python -m xiaomiao_agent serve --config ..\.cache\agent\nanobot\config.json

# Gateway / WebSocket / 内嵌 WebUI
uv run python -m xiaomiao_agent gateway --config ..\.cache\agent\nanobot\config.json
```

WebUI 开发模式：

```powershell
cd webui
npm ci
npm run dev -- --host 127.0.0.1 --port 5174
```

## 配置与运行数据

源码树默认把运行数据集中到仓库根目录：

| 路径 | 内容 |
| --- | --- |
| `../config.json` | `xiaomiaoVirtual` 统一配置入口 |
| `../.cache/agent/nanobot/config.json` | Agent 展开后的运行配置 |
| `../.cache/agent/nanobot/workspace` | 角色、会话、长期记忆和工作文件 |
| `../.cache/pytest` | pytest 可复用缓存 |
| `../.cache/ruff/xiaomiaoAgent` | Ruff 缓存 |

已安装的独立版本通常使用 `~/.nanobot`。可通过 `XIAOMIAO_AGENT_HOME` 指定其他运行目录。

配置模型时只合并所需字段，不要覆盖完整配置：

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "通过本地环境或密钥系统提供"
    }
  },
  "agents": {
    "defaults": {
      "provider": "openrouter",
      "model": "anthropic/claude-opus-4-6"
    }
  }
}
```

不要把 API key、渠道 token、Cookie、用户会话或记忆提交到 Git。

## 根目录文件

| 文件 | 作用 |
| --- | --- |
| `.gitattributes` | Git 行尾和文件属性规则。 |
| `AGENTS.md` | 开发者和代码 Agent 共用的项目规则，是规则的唯一维护来源。 |
| `CLAUDE.md` | Claude Code 兼容入口，仅引用 `AGENTS.md`，避免规则复制和漂移。 |
| `CONTRIBUTING.md` | 贡献、分支和提交约定。 |
| `SECURITY.md` | 安全边界与漏洞报告说明。 |
| `THIRD_PARTY_NOTICES.md` | 内置第三方源码、资源和许可证归属。 |
| `core_agent_lines.sh` | 统计核心 Agent 代码行数。 |
| `entrypoint.sh` | 容器或部署环境启动入口。 |
| `pyproject.toml` | Python 包、依赖、命令、Ruff 和 pytest 配置。 |
| `uv.lock` | uv 精确依赖锁。 |
| `README.md` | 项目入口、结构、操作和维护说明。 |

Windows TUI 的唯一仓库级入口是 `../scripts/start-tui.cmd`；本目录不再保留功能相同的副本。

## 目录说明

### `nanobot`

后端核心包：

- `__init__.py`：公开 API 和版本入口。
- `__main__.py`：`python -m nanobot` 的命令行入口。
- `nanobot.py`：面向 Python 调用方的高层 facade 和单次运行结果模型。
- `agent`：主循环、上下文、运行器、记忆、技能、子 Agent、自动压缩和 hooks。
- `agent/tools`：文件、搜索、Shell、Web、MCP、cron、消息、媒体、文档转换、网页抓取及服务桥接工具。
- `api`：OpenAI 兼容 API，以及 xiaomiao 事件、配置和健康端点。
- `bus`：入站、出站消息模型和异步队列。
- `channels`：Discord、Email、Feishu、Matrix、Slack、Telegram、WebSocket 等聊天渠道。
- `cli`：命令行、初始化向导、TUI 和服务启动命令。
- `config`：配置 schema、加载、校验、路径和兼容迁移。
- `cron`：定时任务持久化、调度和执行。
- `heartbeat`：周期性心跳和后台唤醒。
- `providers`：Anthropic、Azure、Bedrock、GitHub Copilot、OpenAI Codex、OpenAI 兼容，以及图像和转录 Provider。
- `security`：网络访问、协议、域名和 SSRF 安全策略。
- `session`：会话历史和上下文生命周期。
- `skills`：随包发布的内置技能及其说明。
- `templates`：AGENTS、SOUL、USER、TOOLS、HEARTBEAT、memory 和 Agent prompt 模板。
- `utils`：文档、媒体、artifact、运行时、GitStore、重启和提示词辅助。
- `web`：随 Python 包发布的 WebUI 静态资源。

### `tests`

pytest 测试按模块划分：

- `agent`：主循环、上下文、记忆、hook、压缩和子 Agent。
- `channels`：渠道消息转换和生命周期。
- `cli`、`command`：命令行与聊天命令路由。
- `config`：schema、加载、环境变量和路径。
- `cron`、`heartbeat`：调度、持久化和后台任务。
- `providers`：模型、图像和转录 Provider。
- `security`：网络和访问控制。
- `session`：历史与上下文管理。
- `tools`：文件、Shell、Web、MCP、媒体等工具。
- `utils`：文档、媒体和运行时辅助。
- 根级测试文件：API、消息总线和跨模块集成。

网络和第三方渠道测试应使用 mock，避免把真实凭据或外部服务稳定性引入单元测试。

### `docs`

项目主题文档和开发说明，完整索引见 [`docs/README.md`](./docs/README.md)：

- 快速开始、配置、部署和多实例。
- CLI、TUI、聊天命令和聊天渠道。
- OpenAI 兼容 API、Python SDK 和 WebSocket。
- 记忆、自定义工具、图像生成和 Agent 社交能力。
- `development/` 下的设计目标、已知陷阱和安全约束。

新增文档应放入职责匹配的主题文件，并同步文档索引；不要在项目根目录新增第二份结构说明。

### `webui`

React、TypeScript、Vite、Tailwind 和 shadcn/ui 管理/对话前端：

- `src/components`：页面与可复用组件。
- `src/hooks`：数据请求、状态和生命周期 hook。
- `src/i18n`：多语言资源。
- `src/lib`：API 客户端、类型和工具。
- `src/providers`：主题、查询和路由上下文。
- `src/tests`：前端测试。
- `src/workers`：后台 Worker。

构建结果写入 `nanobot/web/dist`，该目录会随 Python 包发布，不应当作普通临时 `dist` 删除。

### `vendor`

- `markitdown`：内置文档转换源码。
- `scrapling`：内置网页抓取源码。

供应商代码升级时必须同步许可证、`THIRD_PARTY_NOTICES.md` 和安全审查，不要把它与本项目业务包混合重构。

### `xiaomiao_agent`

品牌化入口包，提供 `python -m xiaomiao_agent` 启动方式和版本信息；业务实现仍位于 `nanobot`。

### 环境、缓存和构建目录

- `.venv`：本地 Python 虚拟环境，可由 `uv sync` 重建，不提交。
- `webui/node_modules`：前端安装依赖，可由 `npm ci` 重建，不提交。
- 普通 `dist`、`.pytest_cache`、`.ruff_cache`、`__pycache__`：生成内容，可清理后重建。
- `nanobot/web/dist`：Python 发布包依赖的已构建 WebUI，需保留。

## 文档导航

| 主题 | 文档 |
| --- | --- |
| 文档总索引 | [`docs/README.md`](./docs/README.md) |
| 快速开始 | [`docs/quick-start.md`](./docs/quick-start.md) |
| 配置 | [`docs/configuration.md`](./docs/configuration.md) |
| CLI | [`docs/cli-reference.md`](./docs/cli-reference.md) |
| TUI | [`docs/TUI_TERMINAL_GUIDE.md`](./docs/TUI_TERMINAL_GUIDE.md) |
| 聊天渠道 | [`docs/chat-apps.md`](./docs/chat-apps.md) |
| 聊天命令 | [`docs/chat-commands.md`](./docs/chat-commands.md) |
| OpenAI 兼容 API | [`docs/openai-api.md`](./docs/openai-api.md) |
| Python SDK | [`docs/python-sdk.md`](./docs/python-sdk.md) |
| WebSocket | [`docs/websocket.md`](./docs/websocket.md) |
| 部署 | [`docs/deployment.md`](./docs/deployment.md) |
| 安全 | [`SECURITY.md`](./SECURITY.md) |

## 测试与质量检查

在本目录执行：

```powershell
# Python 单元测试
uv run pytest -q

# Python 静态检查
uv run ruff check nanobot tests

# WebUI 测试与构建
cd webui
npm test
npm run build
```

从仓库根目录可以运行统一质量入口：

```powershell
pnpm quality:python
uv run --project xiaomiaoAgent pytest -q
```

## 扩展原则

1. 新渠道实现统一渠道接口，消息转换保留在适配层，不污染 Agent 核心。
2. 新 Provider 复用统一流式事件模型，并覆盖超时、重试、错误映射和取消测试。
3. 新工具必须声明输入 schema、权限、超时和副作用；高风险操作显式确认或拒绝。
4. 配置变更同步更新 schema、默认模板、文档和必要的迁移逻辑。
5. 前后端 API 变更同步更新类型、WebUI 客户端和集成测试。
6. 运行时错误应显式暴露，不使用静默回退、假成功或隐藏默认值。

## 安全与提交边界

- 网络工具必须经过 `nanobot/security/network.py` 的协议、域名和 SSRF 策略。
- 不提交 API key、Cookie、渠道 token、用户记忆、会话历史、`.venv` 或普通构建产物。
- 日志不记录完整授权头、密钥或用户私密内容。
- vendor 代码和第三方许可证不可随意删除。
- 清理缓存时保留 `nanobot/web/dist`，并先确认目标位于当前工作区。
