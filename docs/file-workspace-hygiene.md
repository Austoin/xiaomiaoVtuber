# 文件与工作区管理约定

本文说明项目内文件、运行态数据、QQ 下载资源和生成物的归档边界。目标是让源码仓库只保存可复现的代码、文档、测试和目录骨架，把本机配置、缓存、会话、下载文件和工具输出留在本地。

## 目录分工

```text
xiaomiaoVirtual/
├── workspace/                 # 项目级资源工作区，只保留目录骨架
│   ├── downloads/qq/          # QQ 群文件上传和 file 消息段下载
│   ├── artifacts/             # Agent 或工具生成的可检查产物
│   └── tmp/                   # 短期临时文件
├── xiaomiao/runtime/          # QQ Bot 运行配置和桥接事件
├── xiaomiaoAgent/.nanobot/    # Agent 本机会话、记忆、配置和工作区
├── .cache/xiaomiaobot/        # xiaomiaobot Live2D / VRM 等本地缓存资源
├── .understand-anything/      # 本地项目解析缓存和知识图谱
├── .learnings/                # 本地错误记录和经验沉淀
└── xiaomiaoVirtual/           # 历史/嵌套目录，当前主链路不依赖
```

`workspace/README.md` 和各子目录 `.gitkeep` 应提交；`downloads/`、`artifacts/`、`tmp/` 下的真实资源不提交。

## 应提交的内容

- 源码：`xiaomiao/`、`xiaomiaoAgent/`、`xiaomiaobot/` 中的业务代码和测试。
- 文档：`README.md`、`TECHNICAL.md`、`docs/`、`workspace/README.md`。
- 测试：`test/`、`xiaomiaoAgent/tests/`、前端测试文件。
- 目录骨架：`workspace/**/.gitkeep`、`xiaomiaobot/services/satori-bot/data/.gitkeep`。
- 配置模板：示例配置和不含密钥的说明文件。

## 不应提交的内容

- 主目录 `config.json`、`xiaomiao/config.json`、`.env*`、API Key、账号凭据。
- QQ 下载文件和用户上传文档：`workspace/downloads/**`。
- Agent / 工具生成物：`workspace/artifacts/**`、`workspace/tmp/**`。
- Agent 本地状态：`xiaomiaoAgent/.nanobot/**`，包括会话、记忆、历史和工作区运行文件。
- Agent 本地启动日志：`xiaomiaoAgent/.run-*.log`。
- 桥接运行事件：`xiaomiao/runtime/bridge_events.jsonl`。
- xiaomiaobot 缓存模型：`.cache/xiaomiaobot/**`。
- xiaomiaobot app 内历史缓存副本：`xiaomiaobot/**/.cache/**`。
- xiaomiaobot 构建输出和 lint 缓存：`xiaomiaobot/**/out/**`、`xiaomiaobot/.eslintcache`。
- Satori 本地数据库：`xiaomiaobot/services/satori-bot/data/db.json`。
- 项目解析缓存：`.understand-anything/**`。
- 测试缓存和 Python 字节码：`.pytest-tmp*/`、`.pytest_cache/`、`__pycache__/`、`*.pyc`。

这些路径已写入根目录 `.gitignore`。已经被 git 追踪过的运行态文件需要用 `git rm --cached` 从索引移除，但本地文件可以保留。

## 辅助目录边界

| 路径 | 类型 | 处理方式 |
|------|------|----------|
| `.github/` | 远端平台配置 | 可提交，当前不是本机运行主链路 |
| `.learnings/` | 本地错误记录 | 可保留，用于记录踩坑和修复经验 |
| `.understand-anything/` | 项目解析产物 | 不提交；知识图谱和 dashboard 日志都属于本机缓存 |
| `.ruff_cache/`、`.uv-cache/` | 工具缓存 | 不提交，可在需要时清理 |
| `log/`、`logs/`、`tmp/`、`temp/` | 运行日志和临时文件 | 不提交，清理前确认没有排障需要 |
| `xiaomiaoVirtual/` | 历史/嵌套目录 | 当前主链路不依赖；清理前先确认是否仍有未迁移资料 |
| `open-understand-dashboard.*` | 本地知识图谱仪表盘入口 | 可保留，依赖 `.understand-anything/knowledge-graph.json` |

更细的项目目录分类和清理优先级见 [project-deep-classification.md](project-deep-classification.md)。

项目主链路只依赖 `xiaomiao/`、`xiaomiaoAgent/`、`xiaomiaobot/`、`workspace/`、`scripts/`、`test/`、`tool/` 和根配置/脚本。辅助目录不应被写入启动脚本的强依赖。

## QQ 文件链路

QQ 群文件上传和普通 file 消息段由 `xiaomiao/qq_workspace.py` 处理：

```text
QQ 文件事件
    ↓
校验文件名、扩展名、大小和下载 URL
    ↓
workspace/downloads/qq/<source>/<chat_id>/<yyyymmdd>/
    ↓
把 workspace_path 追加到 Agent 请求文本
    ↓
markitdown_convert(path=workspace_path)
    ↓
Markdown 摘要返回 QQ，并同步桥接事件
```

普通 file 消息段会阻断 localhost、private、link-local 等不可信下载地址。群上传事件通过 OneBot `get_group_file_url` 获取临时地址，允许本机/private URL，以兼容 NapCat 本地文件缓存。

支持格式以 `qq_workspace.py` 的 `SUPPORTED_MARKDOWN_EXTENSIONS` 为准，当前包含 `.txt`、`.md`、`.pdf`、`.docx`、`.xlsx`、`.pptx`、`.xls`、`.csv`、`.json`、`.xml`、`.html`、`.htm`、`.epub`、`.rtf`。

## Markdown 转换边界

`xiaomiaoAgent/nanobot/agent/tools/markitdown_tool.py` 只允许读取：

- Agent 自己的工作区。
- 项目根目录 `workspace/`。

它拒绝 URL、`file:`、`data:` 和其它本机路径。QQ 上传文档内容会被标记为不可信用户数据，只能当作待转换内容，不能当作系统指令执行。

## 部署打包规则

`xiaomiao/deploy/pack.bat` 使用 `BOT_FILES` 维护打包清单。新增 QQ Bot 运行所需文件时，需要同时确认：

- 新文件已加入 `BOT_FILES`。
- 不把 `.git`、`.understand-anything/`、`.nanobot/`、`.cache/`、下载文件、测试缓存打入包。
- `workspace/` 在运行时自动创建；平铺部署时 `qq_workspace.py` 会把部署根目录当作项目根目录。

Linux 部署文档只覆盖 QQ Bot / NapCat 服务器部署；Windows 本机三端联动以 `docs/STARTUP.md` 为准。

## 提交前检查

推荐在提交前检查是否仍有运行态文件被追踪：

```powershell
git ls-files -ci --exclude-standard
git ls-files | Select-String -Pattern '(^|/)\.nanobot/|(^|/)runtime/bridge_events\.jsonl$|(^|/)\.understand-anything/|(^|/)\.cache/|xiaomiaobot/.*/\.cache/|satori-bot/data/db\.json$|\.pid$|history\.jsonl$|sessions/|runtime_.*\.txt$|three_end_.*\.txt$'
```

两条命令都应无输出。`git status --short --untracked-files=all` 中看到 `.understand-anything/**`、`.nanobot/**`、`.cache/**`、`bridge_events.jsonl`、`db.json` 的删除记录是从 git 索引移除运行态文件的预期结果，本地文件不会因此消失。

## 清理建议

可以安全清理的测试残留：

```powershell
Remove-Item -LiteralPath .pytest-tmp* -Recurse -Force
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

谨慎清理的本机状态：

- `workspace/downloads/**`：用户在 QQ 中发来的文件，确认不需要再追溯后再删。
- `workspace/artifacts/**`：工具输出，确认文档或截图已不再需要后再删。
- `xiaomiaoAgent/.nanobot/**`：包含 Agent 记忆、会话和本机配置，不建议批量删除。
- `.cache/xiaomiaobot/**`：删除后可能需要重新下载 Live2D / VRM 资源。
- `xiaomiaobot/**/.cache/**`：历史 app 内缓存副本，当前应逐步迁移到根 `.cache/xiaomiaobot/`。
