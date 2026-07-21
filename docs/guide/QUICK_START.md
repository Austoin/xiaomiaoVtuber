# xiaomiaoVirtual 快速开始

## 一键启动

```powershell
cd <仓库根目录>
pnpm run start:all
```

该命令启动 NapCat、xiaomiaoAgent API、QQ 适配器和 Stage Web。所有端共用 `xiaomiaoAgent`。

## 单独启动

```powershell
pnpm run tui            # Agent 终端
pnpm run agent:api      # OpenAI 兼容 API，端口 8900
pnpm run agent:gateway  # Discord/Telegram 等通道
pnpm run agent:webui    # 内嵌 WebUI，地址 http://127.0.0.1:8765
pnpm run qq             # QQ/NapCat 适配器
pnpm run bot:web        # Stage Web 开发端
pnpm run bot:minecraft  # Minecraft 服务
pnpm run bot:twitter    # Twitter MCP 服务
```

## 首次使用

需要 Python 3.11+、Node.js 和 pnpm。QQ 另需 NapCat，Minecraft 另需可连接的游戏服务器，Twitter 首次启动需要浏览器登录。

```powershell
pnpm install
menu.cmd setup-check
```

根目录创建 `config.json`：

```json
{
  "xiaomiaoAgent": {
    "provider": "custom",
    "model": "deepseek-v4-flash",
    "providers": {
      "custom": {
        "apiKey": "你的密钥",
        "baseUrl": "https://你的中转站/v1"
      }
    }
  }
}
```

完整字段见 [配置说明](CONFIGURATION.md)，外部服务见 [集成指南](INTEGRATIONS.md)。

## 检查

```powershell
pnpm run start:check
Invoke-RestMethod http://127.0.0.1:8900/health
Invoke-RestMethod http://127.0.0.1:18790/health
```

QQ 使用见 [QQ Bot 指南](../user-guide/qq-bot/README.md)，接口格式见 [Agent API 文档](../../xiaomiaoAgent/docs/openai-api.md)。
