# xiaomiaoVirtual 启动指南

本文说明如何在本机启动 `xiaomiaoVirtual` 的三个核心部分：

1. `xiaomiao`：QQ Bot 主体。
2. `AuBot`：Vtuber 桌面端。
3. `nanobot`：独立 Agent 框架，可提供 CLI、gateway、OpenAI 兼容 API 和 WebUI。

推荐启动顺序：先启动 NapCat 和 `xiaomiao`，再启动 `AuBot` 桌面端；如需 Agent 能力，再单独启动 `nanobot`。

## 运行前准备

### Python 环境

项目当前推荐使用 conda 环境 `xiaomiao`：

```powershell
conda activate xiaomiao
```

首次运行或依赖缺失时，在 `xiaomiao` 目录安装依赖：

```powershell
cd F:\xiaomiaoVirtual\xiaomiao
pip install -r requirements.txt
```

### Node / pnpm 环境

`AuBot` 使用 `pnpm@10.33.0`：

```powershell
cd F:\xiaomiaoVirtual\AuBot
corepack enable
corepack prepare pnpm@10.33.0 --activate
pnpm install
```

### nanobot Python / Bun 环境

`nanobot` 是独立 Python Agent 框架。首次运行时，在 `nanobot` 目录从源码安装：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\nanobot
pip install -e .
```

如果需要运行 `nanobot` WebUI，还需要 Bun。当前已在 `xiaomiao` conda 环境中通过 npm 安装 Bun：

```powershell
conda activate xiaomiao
npm install -g bun --prefix "F:\Anaconda3\envs\xiaomiao"
bun --version
```

当前验证版本：

```text
1.3.13
```

如果以后换了 conda 环境路径，请先用下面命令确认环境位置，再替换 `--prefix`：

```powershell
conda run -n xiaomiao python -c "import sys; print(sys.prefix)"
```

安装 Bun 后，进入 `webui` 安装前端依赖：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\nanobot\webui
bun install
```

当前已在 `nanobot/webui` 下执行过 `bun install`，结果为 `396 packages installed`。

### 本地配置

运行前确认以下本地配置存在且正确：

- `xiaomiao/config.json`：QQ Bot、OneBot、模型 API 等配置。
- `AuBot/**/.env`：如使用相关服务，保留本地环境变量文件。

这些文件已被根 `.gitignore` 忽略，不应提交到仓库。

## 启动 xiaomiao QQ Bot

进入 `xiaomiao`：

```powershell
cd F:\xiaomiaoVirtual\xiaomiao
conda activate xiaomiao
```

### 方式一：手动启动

先启动 NapCat，并确保 OneBot WebSocket 监听在：

```text
127.0.0.1:5004
```

然后启动小喵：

```powershell
python main.py
```

### 方式二：使用脚本启动

如果本地存在 NapCat 一键包，可直接运行：

```powershell
start.bat
```

脚本会尝试启动 NapCat，然后再启动：

```powershell
python main.py
```

## 启动 AuBot 桌面端

新开一个 PowerShell 窗口，进入 `AuBot`：

```powershell
cd F:\xiaomiaoVirtual\AuBot
```

启动桌面端：

```powershell
pnpm dev:tamagotchi
```

该命令会启动 `apps/stage-tamagotchi` 的 Electron 开发模式。

## 启动 nanobot

`nanobot` 当前可作为独立子系统运行，不要求 `xiaomiao` 或 `AuBot` 已启动。

### 1. 初始化配置和工作区

进入 `nanobot` 目录：

```powershell
cd F:\xiaomiaoVirtual\nanobot
```

初始化项目内配置和工作区：

```powershell
conda activate xiaomiao（你自己的环境）
nanobot onboard `
  --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json `
  --workspace F:\xiaomiaoVirtual\nanobot\.nanobot\workspace

如果只写nanobot onboard 就是默认盘
```

当前项目已执行过该命令，并生成：

```text
F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
F:\xiaomiaoVirtual\nanobot\.nanobot\workspace\
```

`nanobot/.nanobot/` 已加入根 `.gitignore`，用于避免本地 API Key、会话、记忆和运行时状态被提交。

### 2. 配置模型 Provider

编辑项目内配置文件：

```text
F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

最小 OpenRouter 示例：

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "你的 API Key"
    }
  },
  "agents": {
    "defaults": {
      "provider": "openrouter",
      "model": "anthropic/claude-opus-4-5"
    }
  }
}
```

不要把真实 API Key 写入仓库文件。推荐后续改用环境变量形式保存。

当前已从 `xiaomiao/config.json` 的 `Others.openai_key` 同步到项目内 nanobot 配置，不在文档中记录真实 Key。同步后的有效配置为：

```json
{
  "providers": {
    "deepseek": {
      "apiBase": "https://api.deepseek.com",
      "apiKey": "<来自 xiaomiao/config.json 的 openai_key>"
    }
  },
  "agents": {
    "defaults": {
      "provider": "deepseek",
      "model": "deepseek-chat"
    }
  }
}
```

本次同步使用的字段来源：

```text
xiaomiao/config.json -> Others.openai_key
xiaomiao/config.json -> Others.openai_base_url
xiaomiao/config.json -> Others.default_model
```

如果以后 `xiaomiao/config.json` 中的 Key 变更，需要重新同步到：

```text
F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

确认 `agents.defaults.workspace` 指向项目内工作区：

```json
{
  "agents": {
    "defaults": {
      "workspace": "F:\\xiaomiaoVirtual\\nanobot\\.nanobot\\workspace"
    }
  }
}
```

### 3. CLI 交互运行

启动交互聊天：

```powershell
conda activate xiaomiao
nanobot agent --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

直接发送一条消息：

```powershell
conda activate xiaomiao
nanobot agent -m "你好" --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

查看状态：

```powershell
nanobot status
```

注意：`status` 当前不支持 `--config` 参数，只显示默认状态信息。需要使用项目内配置时，请对 `agent`、`gateway` 或 `serve` 指定 `--config`。

### 4. 启动 gateway

如果需要聊天通道、WebSocket、OpenAI 兼容 API 或 WebUI 接入，启动 gateway：

```powershell
conda activate xiaomiao
nanobot gateway --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json

如果是默认的config路径就不用加--config后面的东西
```

### 5. 启动 WebUI

WebUI 需要同时运行 `nanobot gateway`。另开一个 PowerShell 窗口，并确保处于 `xiaomiao` conda 环境：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\nanobot\webui
bun run dev
```

如需使用 OpenAI 兼容 API，可安装 API extra 后运行：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\nanobot
pip install "nanobot-ai[api]"
nanobot serve --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

## 默认端口

```text
NapCat OneBot WebSocket: 127.0.0.1:5004
xiaomiao 桌面桥接服务: 127.0.0.1:5519
nanobot gateway 默认端口: 127.0.0.1:8765
nanobot OpenAI 兼容 API 默认端口: 127.0.0.1:8900
```

`AuBot` 桌面端会读取 `xiaomiao` 的本地桥接接口，将 Bot 回复同步到：

- 桌面字幕。
- 聊天历史。
- TTS 语音播报。
- Live2D 口型和表现层。

## 启动验证

### 验证 xiaomiao 测试

在项目根目录运行：

```powershell
cd F:\xiaomiaoVirtual
conda run -n xiaomiao python -m unittest discover -s test/xiaomiao -p "test_*.py"
```

预期结果：

```text
Ran 12 tests
OK
```

### 验证桥接服务

启动 `xiaomiao` 后，访问：

```text
http://127.0.0.1:5519/v1/xiaomiao/status
```

如果服务正常，应返回类似：

```json
{
  "ok": true,
  "service": "xiaomiao-desktop-bridge",
  "model": "deepseek-chat",
  "default_user_id": 3554978979
}
```

### 验证 nanobot

初始化并配置模型后，运行：

```powershell
cd F:\xiaomiaoVirtual\nanobot
conda activate xiaomiao
nanobot agent -m "你好，用一句话回复我。" --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

如果需要验证 gateway，可运行：

```powershell
conda activate xiaomiao
nanobot gateway --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

再检查日志中是否出现 gateway 启动和通道加载信息。

## 常见问题

### NapCat 连接失败

检查 NapCat 是否已登录，并确认 OneBot WebSocket 端口是：

```text
127.0.0.1:5004
```

同时检查 `xiaomiao/config.json` 中的连接配置是否指向该地址。

### AuBot 无法同步小喵回复

先确认 `xiaomiao` 已启动，并检查桥接状态接口：

```text
http://127.0.0.1:5519/v1/xiaomiao/status
```

如果接口不可访问，优先检查 `python main.py` 是否正常运行。

### pnpm install 很慢或失败

确认 Node.js 和 Corepack 可用：

```powershell
node -v
corepack --version
pnpm -v
```

如果 `pnpm` 版本不一致，重新执行：

```powershell
corepack prepare pnpm@10.33.0 --activate
```

### Python 依赖缺失

在 `xiaomiao` 目录重新安装依赖：

```powershell
cd F:\xiaomiaoVirtual\xiaomiao
conda activate xiaomiao
pip install -r requirements.txt
```

### nanobot 命令不存在

确认已经在 `nanobot` 目录执行源码安装：

```powershell
cd F:\xiaomiaoVirtual\nanobot
pip install -e .
```

如果仍找不到命令，使用当前 Python 重新安装，或确认 Python Scripts 目录已加入 `PATH`。

### nanobot WebUI 无法连接

WebUI 需要 `nanobot gateway` 同时运行。请确认已经在另一个终端启动：

```powershell
cd F:\xiaomiaoVirtual\nanobot
conda activate xiaomiao
nanobot gateway --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

## 推荐日常启动命令

终端一：

```powershell
cd F:\xiaomiaoVirtual\xiaomiao
conda activate xiaomiao
python main.py
```

终端二：

```powershell
cd F:\xiaomiaoVirtual\AuBot
pnpm dev:tamagotchi
```

可选终端三（nanobot CLI 或 gateway）：

```powershell
cd F:\xiaomiaoVirtual\nanobot
conda activate xiaomiao
nanobot agent --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

或：

```powershell
cd F:\xiaomiaoVirtual\nanobot
conda activate xiaomiao
nanobot gateway --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
```

可选终端四（nanobot WebUI）：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\nanobot\webui
bun run dev
```
