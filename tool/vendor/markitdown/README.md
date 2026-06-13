# MarkItDown 精简源码

本目录保存项目使用的 MarkItDown 精简源码，需要提交到主仓库。当前接入点是 `xiaomiaoAgent/nanobot/agent/tools/markitdown_tool.py`，工具方法保持为 `MarkItDown(enable_plugins=False).convert(fp)`。

## 保留内容

- `packages/markitdown/src/markitdown/` 主源码。
- `packages/markitdown/pyproject.toml` 包元数据。
- `packages/markitdown/README.md`、`ThirdPartyNotices.md`。
- 根目录 `LICENSE`、`SECURITY.md`。

## 已移除内容

- 本地 `.git`、`.venv`、缓存和构建产物。
- 上游 CI、发布、Docker、测试、临时 workspace。
- `markitdown-mcp`、`markitdown-ocr`、`markitdown-sample-plugin` 等当前未接入扩展包。

## 项目边界

当前项目只开放 `markitdown_convert` 本地文件转 Markdown：

- 只允许 Agent workspace 和项目 `workspace/` 内文件。
- 拒绝 URL、`file:`、`data:` 和其它本机任意路径。
- 禁用 MarkItDown 插件加载。
- OCR、云文档理解、远程 URI 转换和 MCP 包不作为当前能力开放。
