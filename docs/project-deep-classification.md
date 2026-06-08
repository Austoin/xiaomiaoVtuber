# 项目深度分类与清理清单

日期：2026-06-07

本文记录 `xiaomiaoVirtual` 当前目录的职责分类、主链路、上游代码边界和清理规则。目标是把源码、文档、测试、第三方工具源码和本机运行态分清楚，后续整理项目时先按分类处理，避免误删真实业务代码或可复现资源。

## 总体结论

当前项目不是单一应用，而是三端融合工程：

- `xiaomiao/` 是 QQ 入口和本地桥接层，负责 NapCat / OneBot 消息接入、QQ 权限、QQ 文件下载、Agent 请求转发和 bridge event 落盘。
- `xiaomiaoAgent/` 是统一 Agent 执行层，内部包名仍是 `nanobot`，负责 OpenAI 兼容 API、会话、记忆、工具注册、ToolRegistry 风险拦截、MCP 和 WebUI。
- `xiaomiaobot/` 是 Web、桌面、移动端表现层和服务/插件生态，来自 AIRI monorepo，内部包名仍保留 `@proj-airi/*`，整理时要尊重上游 monorepo 结构。
- `tool/` 是第三方工具源码集合，目前包含 MarkItDown 和 Scrapling，不是运行缓存；不要因为目录名像工具箱就删除。
- `workspace/` 是项目级资源工作区，只提交目录骨架，QQ 下载文件、转换结果和短期产物都留在本地。

主链路已经形成：QQ / stage-web / stage-tamagotchi / xiaomiaoAgent WebUI 都通过 `xiaomiaoAgent` 统一会话、记忆和工具能力交汇。清理项目时应保护这条链路涉及的源码、测试和文档。

## 根目录分类

| 路径 | 分类 | 当前处理建议 |
|------|------|--------------|
| `README.md` | 项目入口文档 | 保留，作为根入口 |
| `TECHNICAL.md` | 技术分析文档 | 保留，承接深层架构说明 |
| `start-all.cmd` | 一键启动脚本 | 保留，主运行入口 |
| `setup-env.cmd` | 环境配置脚本 | 保留，主环境入口 |
| `scripts/` | 启动辅助脚本 | 保留，目前包含健康检查脚本 |
| `docs/` | 中文项目文档 | 保留并继续作为唯一文档归档入口 |
| `test/` | 顶层 Python 测试 | 保留，主要覆盖 `xiaomiao` 桥接和 QQ Agent 能力 |
| `workspace/` | 本地资源工作区 | 保留目录骨架，真实资源不提交 |
| `xiaomiao/` | QQ Bot 业务子系统 | 保留 |
| `xiaomiaoAgent/` | Agent / nanobot 子系统 | 保留 |
| `xiaomiaobot/` | Web / 桌面 / 移动端表现层 | 保留 |
| `tool/` | 第三方工具源码 | 保留，按工具文档管理 |
| `.github/` | 平台配置 | 保留，非本机主链路但属于工程配置 |
| `.learnings/` | 本地错误经验 | 可保留；若要公开仓库，可迁移到 docs 后再删 |
| `.understand-anything/` | 项目解析缓存 | 不提交，可清理 |
| `.ruff_cache/`、`.uv-cache/` | 工具缓存 | 不提交，可清理 |
| `log/` | 历史日志和运行日志 | 不应继续提交，保留排障价值时迁移到 docs/plans 或删除 |
| `xiaomiaoVirtual/` | 空的历史嵌套目录 | 当前主链路不依赖，可删除空目录 |

## xiaomiao 分类

`xiaomiao/` 是当前 QQ 权限与桥接入口，不应做大批量删除。重点文件如下：

| 文件 | 作用 |
|------|------|
| `main.py` | QQ 消息主入口，包含命令处理、角色、AI 回复、QQ Agent 工具权限网关 |
| `agent_backend.py` | 调用 `xiaomiaoAgent` OpenAI 兼容 API，传递 `channel/chat_id/user_id/tool_policy/confirmation_id` |
| `qq_agent_tools.py` | QQ Agent 工具策略决策：普通用户 `low_risk`，白名单用户 `trusted_confirmed` |
| `qq_agent_bridge.py` | QQ 文本/图片/记忆命令映射，桥接事件发布 |
| `qq_workspace.py` | QQ 文件下载到 `workspace/downloads/qq/`，供 MarkItDown 转 Markdown |
| `desktop_bridge.py` | 本地 HTTP bridge、聊天同步、bridge event 查询和写入 |
| `bridge_event_store.py` | bridge event JSONL 持久化 |
| `unified_config.py` | 根配置和 `xiaomiao/config.json` 兼容读取 |
| `deploy/` | QQ Bot 打包和部署脚本 |
| `runtime/` | 本地运行权限列表和定时消息配置 |

清理边界：

- `runtime/bridge_events.jsonl` 是运行事件，不提交。
- `runtime/*.ini` 中的权限和定时消息文件当前被作为运行骨架追踪，清理前要确认是否要迁移到模板文件。
- `deploy/xiaomiaoVirtual.zip` 是打包产物，若被追踪应移除；当前未被 Git 跟踪。
- `assets/` 下字体、字典、名言图片遮罩属于真实资源，不能删除。

## xiaomiaoAgent 分类

`xiaomiaoAgent/` 是轻量 Agent 框架源码，当前应整体保留。重点目录如下：

| 路径 | 作用 |
|------|------|
| `nanobot/api/server.py` | OpenAI 兼容 API，接收 QQ/stage/WebUI metadata 和工具策略 |
| `nanobot/agent/loop.py` | Agent 主循环，多轮推理与工具调用 |
| `nanobot/agent/memory.py` | 记忆层、Dream 和记忆文件管理 |
| `nanobot/agent/tools/registry.py` | 工具注册与二次风险拦截，低风险/确认策略最终在这里兜底 |
| `nanobot/agent/tools/markitdown_tool.py` | 本地 workspace 文档转 Markdown 工具 |
| `nanobot/agent/tools/scrapling_tool.py` | 低风险网页正文抓取工具 |
| `nanobot/agent/tools/xiaomiao_stage.py` | 面向小喵舞台/bridge 的工具适配 |
| `nanobot/agent/tools/xiaomiaobot_services.py` | xiaomiaobot 服务类能力适配 |
| `nanobot/config/schema.py` | 配置模型、MCP 风险模式和服务开关 |
| `tests/` | Agent 单测与工具测试 |
| `.nanobot/` | 本机会话、记忆、配置和工作区运行态 |

清理边界：

- `.nanobot/` 不提交，也不建议批量删除，因为里面可能有记忆和本机配置。
- `.run-*.log` 是本地启动日志，可清理。
- `uv.lock` 是依赖锁文件，保留。
- `docs/`、`README.md`、`THIRD_PARTY_NOTICES.md`、`SECURITY.md` 是上游/子项目文档，保留；项目级中文入口放在根 `docs/xiaomiaoAgent/README.md`。

## xiaomiaobot 分类

`xiaomiaobot/` 是最大子系统，整理时要按 monorepo 类型分层，不要把包名 `@proj-airi/*` 误认为无关旧名。

| 路径 | 分类 | 说明 |
|------|------|------|
| `apps/stage-web/` | Web 表现层 | 接收网页输入、同步桥接事件、展示聊天和舞台状态 |
| `apps/stage-tamagotchi/` | Electron 桌面端 | 桌面角色、TTS、Live2D/VRM、插件宿主和本地服务 |
| `apps/stage-pocket/` | 移动端 | Capacitor 移动端，只读同步 bridge event 为主 |
| `apps/server/`、`apps/ui-server-auth/` | 服务端应用 | xiaomiaobot 服务端能力实验/运行入口 |
| `packages/stage-ui/` | 核心舞台 UI | 共享业务组件、状态、设置页和场景组件 |
| `packages/stage-layouts/`、`packages/stage-pages/` | 页面布局 | 多端共享页面基础 |
| `packages/stage-ui-live2d/`、`packages/stage-ui-three/` | 渲染能力 | Live2D、Three.js、VRM 相关能力 |
| `packages/server-*` | 服务运行时和 SDK | 插件与服务通信协议、运行时和 schema |
| `packages/plugin-*` | 插件协议和 SDK | 插件开发基础设施 |
| `services/*` | 外部服务 | Computer Use、Minecraft、Twitter、Discord、Telegram、Satori 等 |
| `plugins/*` | 插件 | HomeAssistant、Bilibili、Chess、Claude Code、Web Extension 等 |
| `integrations/*` | 外部集成 | VSCode 等集成，不属于当前 QQ 主链路但属于上游能力 |
| `nix/` | Nix 打包 | 依赖资源缓存路径，清理 `.cache` 时必须同步检查 |

清理边界：

- 根 `.cache/xiaomiaobot/` 是统一 Live2D 模型 / VRM 下载缓存，已忽略；删除后需要重新下载大资源。
- `apps/stage-web/.cache/`、`apps/stage-pocket/.cache/` 和 `apps/stage-tamagotchi/src/renderer/.cache/` 仍由 `DownloadLive2DSDK()` 用于 Cubism SDK 缓存，因为该外部插件暂不支持传入统一 `cacheDir`。
- `apps/stage-tamagotchi/out/` 是 Electron 构建输出，不应继续提交。
- `xiaomiaobot/.eslintcache` 是 ESLint 缓存，不应继续提交。
- `apps/*/node_modules/`、`dist/`、`.vite/`、`.turbo/` 都是运行/构建产物，不应提交。
- `public/assets/js/CubismSdkForWeb-5-r.3/Core/live2dcubismcore.min.js` 是页面实际引用的静态资源，不要和 `.cache` 混同删除。

## tool 分类

`tool/` 不是临时目录。当前两个工具都已经有项目级文档：[tool-directory-analysis.md](tool-directory-analysis.md)。

| 路径 | 分类 | 处理建议 |
|------|------|----------|
| `tool/markitdown/` | 第三方文档转 Markdown 源码 | 保留，作为 `markitdown_convert` 的来源和参考 |
| `tool/Scrapling/` | 第三方网页抓取源码 | 保留，作为 `scrapling_get` 和后续爬虫/MCP 能力参考 |

清理边界：

- 测试素材、README、MCP 示例、skill 文档属于工具源码的一部分，不应随意删除。
- 若未来只保留运行依赖而不保留源码，需要先改 `xiaomiaoAgent` 工具实现和文档引用。

## 文档分类

根 `docs/` 是唯一项目级中文文档入口。当前建议结构：

| 路径 | 作用 |
|------|------|
| `docs/README.md` | 文档总导航 |
| `docs/运行与配置.md` | 最短启动和环境说明 |
| `docs/STARTUP.md` | 详细启动、端口和常见问题 |
| `docs/project-overview.md` | 项目概览 |
| `docs/project-deep-classification.md` | 本文，目录分类和清理清单 |
| `docs/file-workspace-hygiene.md` | 文件、workspace、运行态边界 |
| `docs/QQ机器人指令速查.md` | QQ 指令速查 |
| `docs/tool-directory-analysis.md` | `tool/` 深度解析 |
| `docs/xiaomiao*/` | 子系统中文说明 |
| `docs/plans/` | 计划书、完成度和后续缺口 |

旧的 `docs/AuBot/` 已整理为 `docs/xiaomiaobot/`，不再恢复旧路径。

## 清理优先级

当前删除命令因安全审批服务不可用被拦截，未强行绕过。以下清理项已写入根 `.gitignore`，后续审批可用时再执行物理删除或 `git rm --cached`。

### 可直接清理

这些属于本机缓存或运行日志，删除不影响源码：

- `.ruff_cache/`
- `.uv-cache/`
- `.understand-anything/`
- `xiaomiao/.ruff_cache/`
- `test/**/__pycache__/`
- `log/tmp/`
- `xiaomiaoAgent/.run-*.log`

### 应从 Git 追踪中移除

这些是已被追踪的生成物或历史日志，不应继续作为源码提交：

- `xiaomiaobot/.eslintcache`
- `xiaomiaobot/apps/stage-tamagotchi/out/`
- `log/log-docs/`

### 暂缓大批量删除

这些文件看起来像缓存，但仍和构建或资源分发有关，删除前需要确认根缓存已经可用：

- `xiaomiaobot/apps/stage-web/.cache/`
- `xiaomiaobot/apps/stage-pocket/.cache/`
- `xiaomiaobot/apps/stage-tamagotchi/src/renderer/.cache/`

暂缓原因：

- 两个目录各约 252 个文件，内容是 Live2D Cubism SDK / 样例资源缓存。
- 模型和 VRM 下载缓存已改为根 `.cache/xiaomiaobot`。
- Cubism SDK 仍由 `@proj-airi/unplugin-live2d-sdk` 写入当前 app 根 `.cache/assets/js/CubismSdkForWeb-5-r.3`；要彻底集中，需要替换或扩展该插件。
- `xiaomiaobot/nix/common.nix` 与 `xiaomiaobot/nix/package.nix` 仍出现 `apps/stage-web/.cache/assets` 和 `stage-tamagotchi/src/renderer/.cache/assets` 约定。
- 如果直接删除旧 app 内缓存，需要同步修正 Nix 资产构建逻辑并验证 Nix 打包；本机当前优先保证 Windows 一键启动链路。

## 后续整合建议

1. 把 `xiaomiao/runtime/*.ini` 逐步改为模板文件加本地运行文件，避免真实权限列表进入提交。
2. 把 `log/log-docs` 中仍有价值的历史记录迁移到 `docs/plans/` 或删除，根目录 `log/` 只作为本地运行目录。
3. 统一 `xiaomiaobot` 资产缓存：保留根 `.cache/xiaomiaobot`，后续替换或扩展 `DownloadLive2DSDK()`，再修正 Nix 对 app 内 `.cache` 的历史路径依赖并移除 app 内 `.cache` 追踪。
4. 对 `xiaomiao/main.py` 这类大文件做分层重构：QQ 命令、权限、图片、Agent bridge、群管理拆为独立模块，但要先补回归测试。
5. 保持 `tool/` 作为第三方源码归档；新增接入能力时优先写 Agent 工具适配和安全边界，不直接让 QQ 调工具源码内部接口。
