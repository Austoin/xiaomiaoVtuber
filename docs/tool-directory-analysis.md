# tool 目录深度解析

日期：2026-06-06

## 结论

`tool/` 当前包含两个独立工具项目：

| 目录 | 定位 | 文件数 | 对 xiaomiaoAgent/QQ 的价值 |
| --- | --- | ---: | --- |
| `tool/markitdown` | 多格式文件转 Markdown，含 MCP、OCR 插件、示例插件 | 191 | 适合做“文档读取/转换”Agent 工具 |
| `tool/Scrapling` | 网页抓取、动态浏览器抓取、反机器人抓取、Spider、MCP、Agent skill | 263 | 适合增强 Web 抓取、网页抽取和长任务爬虫能力 |

总体判断：

- MarkItDown 的第一批低风险接入已完成：`xiaomiaoAgent` 新增 `markitdown_convert`，只允许转换 Agent 工作区和项目根 `workspace/` 内本地文件，拒绝 URL、`file:`、`data:` 和其它本机路径。
- QQ 文档资源链路已接入：群文件上传和普通 file 消息段会保存到 `workspace/downloads/qq/`，再由 Agent 调用 `markitdown_convert` 转 Markdown 和总结。
- Scrapling 的第一批低风险接入已完成：`xiaomiaoAgent` 新增 `scrapling_get`，只允许公网 `http/https` GET，复用 SSRF 校验，固定 `main_content_only=true`，不暴露 cookies/auth/proxy/browser/stealth/浏览器会话。
- 两者都已有 MCP 形态，可以优先通过 xiaomiaoAgent 的 MCP/ToolRegistry 接入，而不是让 QQ 直接操作这些项目。
- `tool/` 中二进制测试素材已按目录和用途纳入审计；深度阅读对象为 Markdown、Python 源码、配置、测试入口和技能文档。

## 当前接入状态

已完成的 Agent 工具：

| 工具名 | 来源 | 风险等级 | QQ `low_risk` 可见 | 边界 |
| --- | --- | --- | --- | --- |
| `markitdown_convert` | `tool/markitdown` / MarkItDown | low | 是 | 仅 Agent 工作区和项目根 `workspace/` 内本地文件；禁止 URI；缺依赖显式报错；输出截断 |
| `scrapling_get` | `tool/Scrapling` / `ScraplingMCPServer.get` | low | 是 | 仅公网 `http/https` GET；阻断内网/元数据地址；固定主内容抽取；不开放浏览器/浏览器会话/凭据 |

已补测试：

- `xiaomiaoAgent/tests/tools/test_markitdown_tool.py`
- `xiaomiaoAgent/tests/tools/test_scrapling_tool.py`
- `xiaomiaoAgent/tests/tools/test_tool_registry.py`
- `xiaomiaoAgent/tests/tools/test_tool_loader.py`

仍未接入的高风险能力：

- MarkItDown OCR、Azure Document Intelligence、Azure Content Understanding。
- MarkItDown 任意本机路径、远程 URI、ZIP 深度/大体积转换。
- Scrapling `bulk_get`、`fetch`、`stealthy_fetch`、`open_session`、`screenshot`、Spider、cookies/auth/proxy/CDP/有界面浏览器。

## 阅读范围

已重点阅读：

- `tool/markitdown/README.md`
- `tool/markitdown/packages/markitdown/README.md`
- `tool/markitdown/packages/markitdown/src/markitdown/_markitdown.py`
- `tool/markitdown/packages/markitdown/src/markitdown/__main__.py`
- `tool/markitdown/packages/markitdown/src/markitdown/converters/*`
- `tool/markitdown/packages/markitdown-mcp/README.md`
- `tool/markitdown/packages/markitdown-mcp/src/markitdown_mcp/__main__.py`
- `tool/markitdown/packages/markitdown-ocr/README.md`
- `tool/markitdown/packages/markitdown-ocr/src/markitdown_ocr/*`
- `tool/markitdown/packages/markitdown-sample-plugin/*`
- `tool/Scrapling/README.md`
- `tool/Scrapling/docs/**/*.md`
- `tool/Scrapling/agent-skill/Scrapling-Skill/SKILL.md`
- `tool/Scrapling/agent-skill/Scrapling-Skill/references/**/*.md`
- `tool/Scrapling/scrapling/cli.py`
- `tool/Scrapling/scrapling/core/ai.py`
- `tool/Scrapling/scrapling/parser.py`
- `tool/Scrapling/scrapling/core/storage.py`
- `tool/Scrapling/scrapling/core/shell.py`
- `tool/Scrapling/scrapling/fetchers/*`
- `tool/Scrapling/scrapling/engines/*`
- `tool/Scrapling/scrapling/spiders/*`
- 两个项目的测试入口和测试素材目录

文件类型分布：

| 类型 | 数量 | 说明 |
| --- | ---: | --- |
| `.py` | 181 | 主要源码和测试 |
| `.md` | 81 | README、官方文档、skill references |
| `.png/.jpg/.svg/.ico` | 29 | 文档图片、赞助图、测试/展示资产 |
| `.pdf/.docx/.pptx/.xlsx/.xls/.csv/.epub/.msg/.ipynb/.mp3/.wav/.m4a/.zip/.bin` | 68 | MarkItDown/OCR 转换测试素材 |
| 配置文件 | 约 30 | `pyproject.toml`、CI、Docker、lint、tox、pytest 等 |

## MarkItDown 解析

### 定位

MarkItDown 是 Microsoft AutoGen 团队维护的 Python 工具，目标是把常见文件、网页、音频、图片等输入转换成适合 LLM 消费的 Markdown。

支持格式包括：

- PDF
- Word DOCX
- PowerPoint PPTX
- Excel XLS/XLSX
- 图片 EXIF 和可选 LLM OCR
- 音频转写
- HTML
- CSV、JSON、XML 等文本格式
- ZIP 内部文件遍历
- YouTube URL 字幕
- EPUB
- Outlook `.msg`
- Azure Document Intelligence
- Azure Content Understanding

### 核心实现

核心类是 `MarkItDown`：

- `convert(source)` 是宽入口，接受本地路径、URL、`requests.Response`、二进制流。
- `convert_local(path)` 读取本地文件。
- `convert_uri(uri)` 支持 `file:`、`data:`、`http:`、`https:`。
- `convert_stream(stream)` 处理二进制流。
- `convert_response(response)` 处理 HTTP 响应。
- `_get_stream_info_guesses()` 使用扩展名、MIME、Magika、charset-normalizer 识别格式。
- `_convert()` 按 converter 优先级尝试转换，失败时收集尝试记录，最后显式抛错。

converter 架构：

- 所有 converter 继承 `DocumentConverter`。
- 每个 converter 实现 `accepts(file_stream, stream_info, **kwargs)` 和 `convert(...)`。
- converter 注册有 priority，数值越小越优先。
- 插件可通过 entry point `markitdown.plugin` 注册 converter。

内置 converter 包括：

- `PlainTextConverter`
- `HtmlConverter`
- `RssConverter`
- `WikipediaConverter`
- `YouTubeConverter`
- `IpynbConverter`
- `BingSerpConverter`
- `PdfConverter`
- `DocxConverter`
- `XlsxConverter`
- `XlsConverter`
- `PptxConverter`
- `ImageConverter`
- `AudioConverter`
- `OutlookMsgConverter`
- `ZipConverter`
- `EpubConverter`
- `CsvConverter`
- `DocumentIntelligenceConverter`
- `ContentUnderstandingConverter`

### 命令行接口

入口：`markitdown.__main__:main`

能力：

- `markitdown file.pdf`
- `markitdown file.pdf -o file.md`
- 从 stdin 读取。
- 使用 `--extension/--mime-type/--charset` 传格式提示。
- `--use-plugins` 启用插件。
- `--list-plugins` 列出插件。
- `--use-docintel --endpoint ...` 使用 Azure Document Intelligence。
- `--use-cu --cu-endpoint ...` 使用 Azure Content Understanding。
- `--keep-data-uris` 保留 data URI。

### MCP 接口

入口：`tool/markitdown/packages/markitdown-mcp/src/markitdown_mcp/__main__.py`

MCP 暴露一个工具：

```text
convert_to_markdown(uri)
```

支持 URI：

- `http:`
- `https:`
- `file:`
- `data:`

传输：

- STDIO
- Streamable HTTP
- SSE

安全要点：

- HTTP/SSE 默认绑定 localhost，但没有认证。
- 工具会以当前进程权限读取本地文件和网络资源。
- 如果接入 xiaomiaoAgent，不能把 `file:` 任意路径开放给 QQ 普通用户。

### OCR 插件

目录：`tool/markitdown/packages/markitdown-ocr`

能力：

- PDF 内嵌图片 OCR。
- 扫描 PDF 整页 OCR fallback。
- DOCX 图片 OCR。
- PPTX 图片 OCR。
- XLSX 工作表图片 OCR。

实现方式：

- 插件注册 `PdfConverterWithOCR`、`DocxConverterWithOCR`、`PptxConverterWithOCR`、`XlsxConverterWithOCR`。
- 优先级是 `-1.0`，会先于内置转换器运行。
- `LLMVisionOCRService` 使用 OpenAI 兼容客户端。
- 如果没有 `llm_client` 或 `llm_model`，插件加载但 OCR 跳过。

风险：

- OCR 会把图片内容发送给外部 LLM 提供方。
- 扫描文档可能包含隐私数据。
- 应默认关闭，只允许 ROOT/Super/白名单显式启用。

### 测试覆盖

MarkItDown 测试覆盖面较广：

- 命令行输入输出。
- 本地文件和 URL。
- data URI。
- PDF 表格和复杂 PDF。
- PDF 内存优化。
- DOCX 注释、公式。
- Content Understanding converter。
- Document Intelligence HTML。
- OCR 插件对 PDF/DOCX/PPTX/XLSX 的图片位置和 fallback。
- 示例 RTF 插件。

## Scrapling 解析

### 定位

Scrapling 是 Web Scraping 框架，覆盖从单页请求到大规模爬虫：

- HTML 解析器。
- HTTP 抓取器。
- DynamicFetcher 浏览器渲染。
- StealthyFetcher 反机器人/Cloudflare 场景。
- Session 管理。
- Proxy rotation。
- 自适应抓取。
- Spider 框架。
- 命令行接口。
- MCP 服务端。
- Agent 技能。

### 解析器

核心类：`scrapling.parser.Selector`

特点：

- 基于 `lxml.html`，但不直接继承 `HtmlElement`，避免 pickle 和生命周期问题。
- 支持 CSS3 选择器、XPath、文本搜索、正则搜索、BeautifulSoup 风格 `find/find_all`。
- 支持 `::text` 和 `::attr(name)` 伪元素。
- 返回对象是 `Selector` 或 `Selectors`，文本是 `TextHandler` 或 `TextHandlers`。
- 属性是只读 `AttributesHandler`。
- 大量属性采用懒加载，提高解析速度。

常用能力：

- `css()`
- `xpath()`
- `find()`
- `find_all()`
- `find_by_text()`
- `find_by_regex()`
- `find_similar()`
- `get()`
- `getall()`
- `re()`
- `re_first()`
- `json()`
- `get_all_text()`
- 生成 CSS/XPath 选择器

### 自适应抓取

能力：

- 第一次通过 `auto_save=True` 存储元素特征。
- 页面结构变化后用 `adaptive=True` 重新定位元素。
- 默认 SQLite 存储：`elements_storage.db`。
- 可按域名隔离，也可用 `adaptive_domain` 复用旧站点特征。

存储内容：

- 元素标签、文本、属性。
- 同级标签。
- DOM 路径。
- 父级标签、属性、文本。

风险：

- 会在本地写 SQLite 数据。
- 如果接 QQ，默认应归为 medium，不应让普通群用户写入持久自适应存储。

### 抓取器

Scrapling 有三类抓取器：

| 抓取器 | 用途 | 风险建议 |
| --- | --- | --- |
| `Fetcher` / `AsyncFetcher` | HTTP 请求，无 JS | low 到 medium |
| `DynamicFetcher` | Playwright/Chrome 渲染 JS | medium |
| `StealthyFetcher` | 反机器人、Cloudflare、指纹伪装 | high |

`Fetcher` 特点：

- 基于 `curl_cffi`。
- 支持浏览器 TLS 指纹模拟。
- 支持 HTTP/3。
- 支持 cookies、headers、params、proxy、auth。
- `follow_redirects` 默认 `"safe"`，可拒绝重定向到内网/private IP，具备 SSRF 防护意识。

`DynamicFetcher` 特点：

- 基于 Playwright Chromium/Chrome。
- 支持无头/有界面模式。
- 支持真实 Chrome。
- 支持 CDP 连接。
- 支持 wait、wait_selector、network_idle。
- 支持 page_action/page_setup。
- 支持资源屏蔽、广告屏蔽、XHR 捕获。

`StealthyFetcher` 特点：

- 基于 DynamicFetcher 增强。
- 支持 Cloudflare Turnstile/Interstitial 自动处理。
- 支持 WebRTC 限制、canvas 噪声、指纹伪装。
- 支持 proxy、真实 Chrome、CDP。
- 属于高价值但高风险能力。

### 命令行接口

入口：`scrapling.cli:main`

命令：

- `scrapling install`
- `scrapling shell`
- `scrapling mcp`
- `scrapling extract get`
- `scrapling extract post`
- `scrapling extract put`
- `scrapling extract delete`
- `scrapling extract fetch`
- `scrapling extract stealthy-fetch`

关键参数：

- `--ai-targeted`：抽取主内容并清理隐藏 prompt injection 内容。
- `--css-selector`：提前缩小抽取范围。
- `--proxy`
- `--cookies`
- `--headers`
- `--headless/--no-headless`
- `--network-idle`
- `--wait-selector`
- `--solve-cloudflare`
- `--block-webrtc`
- `--hide-canvas`

接入建议：

- QQ/Agent 不应直接开放 `post/put/delete`。
- `extract get --ai-targeted` 可作为低风险候选。
- `fetch/stealthy-fetch` 应要求白名单，必要时确认。

### MCP 服务端

入口：`scrapling.core.ai.ScraplingMCPServer`

暴露工具：

| 工具 | 功能 | 风险建议 |
| --- | --- | --- |
| `get` | 单 URL HTTP 抓取 | low/medium |
| `bulk_get` | 多 URL 并发 HTTP 抓取 | medium |
| `fetch` | 单 URL 浏览器抓取 | medium |
| `bulk_fetch` | 多 URL 浏览器抓取 | medium/high |
| `stealthy_fetch` | 单 URL stealth 抓取 | high |
| `bulk_stealthy_fetch` | 多 URL stealth 抓取 | high |
| `open_session` | 开持久浏览器会话 | high |
| `close_session` | 关闭会话 | medium |
| `list_sessions` | 列出会话 | low |
| `screenshot` | 用已有会话截图 | medium/high |

MCP 输出：

- 抓取工具返回 `ResponseModel`：`status/content/url`。
- `screenshot` 返回 MCP 图像内容块和最终 URL 文本。

安全特性：

- `main_content_only=true` 默认启用。
- 清理 CSS-hidden、`aria-hidden`、`template`、HTML comments、zero-width 字符。
- 浏览器工具默认屏蔽广告。

接入风险：

- HTTP 抓取可能触发 SSRF、内网探测、访问未授权目标。
- 浏览器会话会消耗资源，可能残留 cookies/会话。
- Stealth/Cloudflare 绕过可能违反站点服务条款。
- `headless=false` 会打开可见浏览器。
- `cdp_url` 可连接已有浏览器，权限很高。

### Spider 框架

核心模块：

- `scrapling.spiders.spider.Spider`
- `scrapling.spiders.engine.CrawlerEngine`
- `scrapling.spiders.scheduler.Scheduler`
- `scrapling.spiders.session.SessionManager`
- `scrapling.spiders.checkpoint.CheckpointManager`
- `scrapling.spiders.cache.ResponseCacheManager`
- `scrapling.spiders.result.CrawlResult/CrawlStats/ItemList`
- `scrapling.spiders.templates.crawler.CrawlSpider`
- `scrapling.spiders.templates.sitemap.SitemapSpider`

能力：

- 异步爬虫。
- 优先级队列。
- URL 指纹去重。
- 允许域名。
- robots.txt obey。
- 并发控制。
- per-domain concurrency。
- 下载延迟。
- 阻断响应检测与重试。
- checkpoint pause/resume。
- 开发缓存。
- 流式结果。
- 生命周期钩子。
- JSON/JSONL 导出。

接入建议：

- 不要把 Spider 作为同步 QQ 命令直接跑到底。
- 应封装成 Agent 长任务：
  - `scrapling_spider_start`
  - `scrapling_spider_status`
  - `scrapling_spider_stop`
  - `scrapling_spider_result`
- 返回任务 ID，并通过桥接事件实时显示状态。
- 默认要求 `allowed_domains` 和 `robots_txt_obey=True`。

### Agent 技能

Scrapling 自带官方技能：

- 路径：`tool/Scrapling/agent-skill/Scrapling-Skill/SKILL.md`
- 明确要求 CLI 使用 `--ai-targeted` 防 prompt injection。
- 建议从 `get` 开始，失败再升级到 `fetch`、`stealthy-fetch`。
- 包含 MCP、抓取、解析、spiders 参考资料。

这份 skill 可以直接转化为 xiaomiaoAgent 的工具说明和系统提示约束。

## 与 xiaomiaoAgent/QQ 的接入建议

### 第一阶段：MarkItDown 文档转换工具

已新增 Agent 工具：

```text
markitdown_convert(path, max_chars=120000)
```

默认策略：

- 普通 QQ 用户只能转换 Agent 工作区或项目根 `workspace/` 内文件。
- QQ 群文件上传和普通 file 消息段先由 `xiaomiao/qq_workspace.py` 校验扩展名、大小和下载 URL，并归档到 `workspace/downloads/qq/<channel>/<chat>/<date>/`。
- 禁止任意 `file:` URI、`data:` URI、`http/https` URI。
- 默认禁止远程 URI，复用现有 `web_fetch` 或 `scrapling_get` 更安全。
- ZIP 转换要限制最大文件数、最大递归深度、总大小。
- OCR 插件默认关闭。

风险分级：

| 动作 | 风险 |
| --- | --- |
| 转换已上传文件 | low |
| 转换工作区白名单文件 | low |
| 转换任意本机路径 | high |
| 转换远程 URL | medium |
| 启用 OCR/LLM Vision | medium/high |
| Azure Document Intelligence / Content Understanding | medium/high |

### 第二阶段：Scrapling 受控网页抽取

已新增第一批 Agent 工具：

```text
scrapling_get(url, css_selector=None, extraction_type="markdown")
```

后续建议新增：

```text
scrapling_bulk_get(urls, css_selector=None)
scrapling_fetch(url, css_selector=None, wait_selector=None)
scrapling_session_list()
```

默认策略：

- `scrapling_get` 可作为低风险候选，但必须限制 URL：
  - 禁止 localhost。
  - 禁止 private IP。
  - 禁止 link-local。
  - 禁止云厂商元数据服务。
  - 限制最大响应体。
  - 限制重定向。
- `bulk_get` 需要限制 URL 数量和并发。
- `fetch` 需要白名单或中风险策略。
- `stealthy_fetch/open_session/screenshot` 默认高风险，需要白名单加确认。

风险分级：

| 动作 | 风险 |
| --- | --- |
| `get` 公网 URL，主内容抽取 | low/medium |
| `bulk_get` | medium |
| 带 cookies/auth/proxy 的请求 | high |
| `fetch` 浏览器渲染 | medium |
| `stealthy_fetch` | high |
| `open_session` | high |
| `screenshot` | medium/high |
| `post/put/delete` | high |
| Spider 长爬虫 | high |

### 第三阶段：MCP 配置档

建议建立 `qq-agent-tool-profile`：

低风险默认可见：

- `markitdown_convert`
- `scrapling_get`

白名单但可直接运行：

- `scrapling_fetch`，仅无头模式、无 proxy、无 cookies、无 CDP。
- `scrapling_session_list`

高风险确认：

- MarkItDown 任意本机文件。
- MarkItDown OCR/外部云服务。
- Scrapling `stealthy_fetch`。
- Scrapling `open_session`。
- Scrapling `screenshot`。
- Scrapling `post/put/delete`。
- Scrapling Spider。
- 任何 cookies/auth/proxy/CDP/有界面浏览器。

### 桥接事件建议

工具事件应统一写入：

```json
{
  "event_type": "tool_start|tool_finish|tool_error",
  "tool_name": "markitdown_convert",
  "risk_level": "low|medium|high",
  "result_summary": "...",
  "artifact_path": "..."
}
```

对于长任务：

```json
{
  "event_type": "tool_start",
  "tool_name": "scrapling_spider_start",
  "task_id": "spider-...",
  "result_summary": "爬虫已启动"
}
```

## 建议的最小落地顺序

1. 已完成：接入 MarkItDown 工作区本地文件转换，并打通 QQ 文档下载到 `workspace/downloads/qq/` 后转 Markdown 的链路。
2. 已完成：接入 Scrapling `get`，只允许公网 URL 和 `main_content_only=true`。
3. 后续：如改走 Scrapling MCP 形态，再建立独立低风险后缀白名单。
4. 后续：接入 `scrapling_fetch`，要求白名单用户。
5. 后续：接入 `stealthy_fetch/open_session/screenshot`，要求二次确认。
6. 后续：把 Spider 封装成长任务，不阻塞 QQ 消息。
7. 后续：将结果文件写入统一产物目录，并同步桥接事件。

## 测试建议

MarkItDown：

- 转换上传 PDF/DOCX/XLSX/PPTX 成 Markdown。
- 任意本机路径被普通 QQ 用户拒绝。
- `file:` URI 逃逸被拒绝。
- QQ file 消息段缺 URL、不支持扩展名、超大文件、private URL 下载均显式失败。
- ZIP 超限显式失败。
- OCR 未配置时显式提示未启用，不假成功。

Scrapling：

- 公网 `get` 成功返回 Markdown 摘要。
- localhost/private IP 被拒绝。
- `bulk_get` 超数量被拒绝。
- `fetch` 对普通用户不可见或被拒绝。
- `stealthy_fetch/open_session/screenshot` 首次返回确认码。
- 浏览器会话创建后可 `list_sessions`，超时或关闭后状态正确。
- Spider 启动返回任务 ID，状态和取消可用。

联调：

- QQ 发送“把这个 PDF 转成 Markdown”，返回摘要和产物。
- QQ 发送“抓取这个网页正文”，返回正文摘要。
- QQ 普通用户请求“用 stealth 绕过 Cloudflare”，明确拒绝。
- QQ 白名单用户请求高风险抓取，先收到确认码。
- stage-web/stage-tamagotchi 能看到工具开始、完成、失败事件。

## 最终判断

`tool/` 已从“可复用工具资产”推进到“第一批低风险 Agent 工具已接入”：

- MarkItDown 已作为 `markitdown_convert` 接入 Agent 工具层和 QQ `low_risk` 策略。
- QQ 文档上传/文件段已进入项目根 `workspace/downloads/qq/`，Agent 可在低风险策略下转换这些文件。
- Scrapling 已作为 `scrapling_get` 接入 Agent 工具层和 QQ `low_risk` 策略。
- 两者都需要严格的路径、URL、网络、资源、权限和确认边界。
- 最安全的产品路线保持不变：QQ 不直接调用这些库，而是通过 xiaomiaoAgent 工具层和 ToolRegistry 风险策略调用；后续应把工具开始/完成/失败结果进一步统一写入桥接事件和产物目录。
