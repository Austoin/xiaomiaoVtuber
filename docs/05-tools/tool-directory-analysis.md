# tool 目录精简说明

`tool/` 保存项目需要提交到主仓库的第三方工具精简源码。当前只保留 `markitdown_convert` 和 `scrapling_get` 所需的主功能源码、安装元数据、许可证和最小说明；本地环境、缓存、嵌套 `.git`、上游 CI/发布材料、示例凭证文档和非当前接入的扩展包已移除。

## 保留内容

| 路径 | 用途 |
|------|------|
| `tool/markitdown/packages/markitdown/src/markitdown/` | MarkItDown 文档转 Markdown 主源码 |
| `tool/markitdown/packages/markitdown/pyproject.toml` | MarkItDown 包元数据 |
| `tool/markitdown/LICENSE`、`README.md`、`SECURITY.md` | 许可证和精简说明 |
| `tool/Scrapling/scrapling/` | Scrapling 网页抓取主源码 |
| `tool/Scrapling/pyproject.toml`、`setup.cfg`、`MANIFEST.in` | Scrapling 包元数据 |
| `tool/Scrapling/LICENSE`、`README.md` | 许可证和精简说明 |

## 接入边界

| Agent 工具 | 源码来源 | 当前方法 | 安全边界 |
|------------|----------|----------|----------|
| `markitdown_convert` | `tool/markitdown/packages/markitdown/src` | `MarkItDown(enable_plugins=False).convert(fp)` | 只允许 Agent workspace 和项目 `workspace/` 内本地文件；拒绝 URL、`file:`、`data:` |
| `scrapling_get` | `tool/Scrapling` | `ScraplingMCPServer.get(...)` | 只允许公网 `http/https` GET；阻断本机、内网、link-local、云元数据地址；不传 cookies/auth/proxy |

工具适配器位于：

- `xiaomiaoAgent/nanobot/agent/tools/markitdown_tool.py`
- `xiaomiaoAgent/nanobot/agent/tools/scrapling_tool.py`

适配器会优先把仓库内精简源码加入导入路径，确保提交到主仓库的 `tool/` 能被实际使用；调用方法保持原工具方法不变。

## 已删除内容

- 嵌套 `.git`。
- `.venv`、`venv`、`__pycache__`、`.pytest_cache`、`.ruff_cache`、`.mypy_cache`、`.cache`。
- 上游 `.github`、`.devcontainer`、Docker、tox、ruff、pre-commit、benchmark、release 等开发发布材料。
- Scrapling 上游 `docs/`、`agent-skill/`、`images/`、`tests/`、`scrapling.egg-info/`。
- MarkItDown 上游 `tests/`、`workspace/`、`markitdown-mcp`、`markitdown-ocr`、`markitdown-sample-plugin`。

## 不保留凭证

`tool/` 不应提交真实凭证、本机 token、cookies、代理账号、浏览器用户目录或会话状态。上游示例中涉及 cookies、proxy、token、password 的文档已不作为项目文档保留；源码里的参数名和安全阻断逻辑属于工具实现，不代表项目开放这些能力。

## 恢复扩展的规则

如需重新启用 OCR、MCP 示例、浏览器渲染、stealth、会话、Spider 或批量爬虫，必须先补齐：

- 对应源码和许可证说明。
- `xiaomiaoAgent/pyproject.toml` 依赖。
- QQ Agent 权限分级和测试。
- 文档中的安全边界。
