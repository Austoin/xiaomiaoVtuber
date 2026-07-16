# Scrapling 精简源码

本目录保存项目使用的 Scrapling 精简源码，需要提交到主仓库。当前接入点是 `xiaomiaoAgent/nanobot/agent/tools/scrapling_tool.py`，工具方法保持为 `ScraplingMCPServer.get(...)`。

## 保留内容

- `scrapling/` 主源码。
- `pyproject.toml`、`setup.cfg`、`MANIFEST.in` 包元数据。
- `LICENSE` 许可证。

## 已移除内容

- 本地 `.git`、`.venv`、缓存和构建产物。
- 上游 CI、发布、Docker、测试、站点文档、图片、agent skill 示例。
- 含 cookies、proxy、token、password 示例的上游文档。

## 项目边界

当前项目只开放 `scrapling_get` 低风险公网 GET 抽取：

- 只允许公网 `http/https`。
- 阻断 localhost、内网、link-local、云元数据地址。
- 适配器不传 cookies、auth、proxy。
- 浏览器会话、stealth、Spider、批量爬虫等能力不作为普通低风险能力开放。

源码中保留的参数名属于上游工具实现，不代表项目开放对应能力。
