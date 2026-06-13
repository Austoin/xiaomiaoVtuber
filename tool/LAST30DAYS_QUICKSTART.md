# Last30Days 工具快速开始

> 多平台研究工具，快速上手指南

---

## ✅ 环境要求

- ✅ Python 3.12.3（已确认）
- ✅ 工具已安装：`tool/vendor/last30days-skill/`
- ✅ 封装已创建：`tool/xiaomiao/last30days.py`

---

## 🚀 快速使用

### 1. Python 调用

```python
from tool.xiaomiao.last30days import last30days_research

# 基础研究
result = last30days_research("Cursor IDE")
print(result["output"])

# HTML 报告
result = last30days_research("OpenAI vs Anthropic", emit="html")
print(f"报告保存到: {result['save_path']}")

# 自定义保存路径
result = last30days_research(
    "Kanye West",
    emit="html",
    save_dir="~/Documents/MyResearch"
)
```

### 2. 命令行使用

```bash
cd tool/vendor/last30days-skill

# 基础研究
python skills/last30days/scripts/last30days.py "Cursor IDE"

# HTML 报告
python skills/last30days/scripts/last30days.py "OpenAI" --emit=html

# 指定保存目录
python skills/last30days/scripts/last30days.py "test" --save-dir ~/Research
```

### 3. 在 xiaomiaoAgent 中使用

工具会自动注册到 xiaomiaoAgent，可以通过以下方式调用：

```python
# 在 xiaomiaoAgent 会话中
# Agent 会自动发现并使用 last30days_research 工具
```

---

## 🔧 可选配置

### 基础功能（免费，开箱即用）

- ✅ Reddit（帖子 + 评论）
- ✅ Hacker News
- ✅ GitHub
- ✅ Polymarket

### 扩展功能（需配置）

**YouTube 转录**:
```bash
pip install yt-dlp
# 或
brew install yt-dlp
```

**X/Twitter** (浏览器登录即可):
1. 在浏览器登录 x.com
2. 工具会自动读取浏览器 cookies

**TikTok/Instagram/Threads** (付费 API):
```bash
export SCRAPECREATORS_API_KEY=your_key_here
```

**网页搜索** (免费额度):
```bash
export BRAVE_SEARCH_API_KEY=your_key_here
```

---

## 📝 使用示例

### 人物研究
```python
result = last30days_research("Peter Steinberger")
# 返回：X 推文、GitHub PR、Reddit 讨论、YouTube 视频
```

### 产品对比
```python
result = last30days_research("OpenClaw vs Hermes", emit="html")
# 返回：功能对比、社区讨论、GitHub 星标、用户评价
```

### 技术趋势
```python
result = last30days_research("Cursor IDE")
# 返回：最新功能、用户反馈、社区讨论、竞品对比
```

### 实时事件
```python
result = last30days_research("Universal Epic Universe")
# 返回：建设进度、等待时间、用户体验、社区建议
```

---

## 📊 返回格式

```python
{
    "success": True,              # 是否成功
    "output": "研究报告内容...",   # Markdown 或 HTML
    "save_path": "~/Documents/Last30Days/cursor-ide-raw.md",
    "error": ""                   # 错误信息（如有）
}
```

---

## 🎯 高级用法

### 自定义保存目录
```python
import os
os.environ["LAST30DAYS_MEMORY_DIR"] = "~/MyResearch"
result = last30days_research("topic")
```

### 排除特定平台
```python
os.environ["EXCLUDE_SOURCES"] = "tiktok,instagram"
result = last30days_research("topic")
```

### 包含额外平台
```python
os.environ["INCLUDE_SOURCES"] = "perplexity,youtube_comments"
result = last30days_research("topic")
```

---

## 📚 完整文档

- **完整功能**: [tool/vendor/last30days-skill/README.md](../vendor/last30days-skill/README.md)
- **配置指南**: [tool/vendor/last30days-skill/CONFIGURATION.md](../vendor/last30days-skill/CONFIGURATION.md)
- **集成说明**: [LAST30DAYS_INTEGRATION.md](LAST30DAYS_INTEGRATION.md)

---

**Last30Days 工具已就绪，开始使用吧！** 🚀
