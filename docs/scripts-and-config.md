# 脚本与配置说明

本文说明项目根目录脚本和本地配置文件的分工。

## 脚本

| 脚本 | 用途 |
|------|------|
| `setup-env.cmd` | 首次安装/修复依赖，创建工作区，初始化 Agent 配置 |
| `start-all.cmd` | 一键启动 QQ、Agent API、gateway、xiaomiao、stage-web、WebUI |
| `scripts/start-all-health.ps1` | 被 `start-all.cmd` 调用，执行端口和健康检查 |
| `open-understand-dashboard.cmd` | 打开 Understand Anything 仪表盘 |
| `open-understand-dashboard.ps1` | 仪表盘打开逻辑 |

## `setup-env.cmd`

常用命令：

```powershell
cd F:\xiaomiaoVirtual
cmd /c call setup-env.cmd
```

只检查：

```powershell
cmd /c call setup-env.cmd --check
```

可选参数：

| 参数 | 说明 |
|------|------|
| `--check` | 只检查工具、配置文件和依赖目录 |
| `--yes` / `-y` | 缺少 `config.json` 时复制 `config.example.json` |
| `--skip-python` | 跳过 Python 依赖安装 |
| `--skip-node` | 跳过 xiaomiaobot `pnpm install` |
| `--skip-webui` | 跳过 xiaomiaoAgent WebUI `npm install` |
| `--help` / `-h` | 查看帮助 |

它默认使用 conda 环境 `xiaomiao`，并安装：

- `xiaomiao/requirements.txt`
- `xiaomiaoAgent[api]`
- `xiaomiaobot` pnpm 依赖
- `xiaomiaoAgent/webui` npm 依赖

## `start-all.cmd`

正式启动：

```powershell
cd F:\xiaomiaoVirtual
cmd /c call start-all.cmd
```

只检查：

```powershell
cmd /c call start-all.cmd --check
```

启动顺序：

```text
1. QQ / NapCat OneBot      127.0.0.1:5004
2. xiaomiaoAgent API       127.0.0.1:8900
3. xiaomiaoAgent gateway   127.0.0.1:8765
4. xiaomiao main / bridge  127.0.0.1:5519
5. xiaomiaobot stage-web   http://127.0.0.1:5175
6. xiaomiaoAgent WebUI     http://127.0.0.1:5174
```

脚本会设置：

```text
NO_PROXY=127.0.0.1,localhost,::1
no_proxy=127.0.0.1,localhost,::1
```

这用于避免本地代理影响 xiaomiao 连接 NapCat。

## 健康检查

`scripts/start-all-health.ps1` 支持：

| 命令 | 说明 |
|------|------|
| `check` | 检查端口、HTTP、gateway 或 xiaomiao |
| `assert-free` | 检查端口未被占用 |
| `wait` | 等待服务就绪 |
| `is-open` | 检查端口是否监听 |
| `config-safe` | 检查 xiaomiaoAgent 配置安全性 |

`config-safe` 会阻止 xiaomiaoAgent 原生 QQ channel 被启用，避免和 `xiaomiao/main.py + NapCat` 的 QQ 权限入口冲突。

## 本地配置文件

| 文件 | 用途 | 是否提交 |
|------|------|----------|
| `config.example.json` | 配置模板 | 是 |
| `config.json` | 模型、中转站、Agent 后端配置 | 否 |
| `xiaomiao/config.json` | QQ、OneBot、权限、人设、本地命令 | 否 |
| `xiaomiaoAgent/.nanobot/config.json` | Agent 工作区、通道、工具和运行时 | 否 |
| `workspace/README.md` | workspace 目录说明 | 是 |

MCP、Computer Use、Twitter、Minecraft 和其它外部服务的权限边界见 [mcp-and-external-services.md](mcp-and-external-services.md)。

## 根 `config.json`

推荐结构：

```json
{
  "xiaomiao_agent": {
    "enabled": true,
    "base_url": "http://127.0.0.1:8900/v1/chat/completions",
    "model": "",
    "session_id": "xiaomiao-unified",
    "timeout_seconds": 30
  },
  "xiaomiaoAgent": {
    "provider": "custom",
    "model": "deepseek/deepseek-chat",
    "providers": {
      "custom": {
        "apiKey": "你的中转站密钥",
        "baseUrl": "https://你的中转站地址/v1"
      }
    }
  }
}
```

说明：

- `xiaomiao_agent.base_url` 固定指向本机 `8900`。
- `xiaomiao_agent.model` 建议留空，避免覆盖 Agent 模型。
- `xiaomiaoAgent.provider` 使用 `custom`。
- `xiaomiaoAgent.providers.custom.baseUrl` 填 `/v1` 地址。
- `apiKey` 不要提交。

## 修改后重启规则

| 修改内容 | 需要重启 |
|----------|----------|
| 根 `config.json` | xiaomiaoAgent API、gateway、xiaomiao |
| `xiaomiao/config.json` | xiaomiao |
| `xiaomiaoAgent/.nanobot/config.json` | xiaomiaoAgent API、gateway |
| `xiaomiaobot` 前端代码 | stage-web 或桌面端 |
| `start-all.cmd` / `setup-env.cmd` | 下次运行生效 |
