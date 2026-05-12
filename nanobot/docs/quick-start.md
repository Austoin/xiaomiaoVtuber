# 安装与快速开始

## 安装

> [!IMPORTANT]
> 本 README 可能描述最新源码中先行提供的功能。
> 如果你想体验最新功能和实验性能力，请从源码安装。
> 如果你希望获得更稳定的日常体验，请从 PyPI 安装，或使用 `uv` 安装。

**从源码安装**（最新功能，实验性变更可能会最先进入这里；推荐用于开发）

```bash
git clone https://github.com/HKUDS/nanobot.git
cd nanobot
pip install -e .
```

**使用 [uv](https://github.com/astral-sh/uv) 安装**（稳定版本，速度快）

```bash
uv tool install nanobot-ai
```

**从 PyPI 安装**（稳定版本）

```bash
pip install nanobot-ai
```

### 更新到最新版本

**PyPI / pip**

```bash
pip install -U nanobot-ai
nanobot --version
```

**uv**

```bash
uv tool upgrade nanobot-ai
nanobot --version
```

**如果你使用 WhatsApp**，升级后需要重建本地桥接：

```bash
rm -rf ~/.nanobot/bridge
nanobot channels login whatsapp
```

## 快速开始

> [!TIP]
> 请在 `~/.nanobot/config.json` 中设置 API Key。
> 获取 API Key：[OpenRouter](https://openrouter.ai/keys)（全球可用）。
>
> 其他 LLM Provider 请参考 [`configuration.md`](./configuration.md)。
>
> Web 搜索能力配置请参考 [`configuration.md`](./configuration.md#web-search) 中的 web-search 章节。

**1. 初始化**

```bash
nanobot onboard
```

如果你想使用交互式配置向导，可以运行：

```bash
nanobot onboard --wizard
```

**2. 配置**（`~/.nanobot/config.json`）

在配置文件中配置下面 **两部分** 即可，其他选项都有默认值。

*设置 API Key*（例如 OpenRouter，推荐全球用户使用）：

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  }
}
```

*设置模型*（可以指定 Provider；默认会自动检测）：

```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "provider": "openrouter"
    }
  }
}
```

**3. 开始聊天**

```bash
nanobot agent
```

完成。现在你已经在 2 分钟内启动了一个可用的 AI Agent。
