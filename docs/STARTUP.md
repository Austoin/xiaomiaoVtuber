# xiaomiaoVirtual 启动指南

本文说明如何在本机启动 `xiaomiaoVirtual` 的三个核心部分，并跑通网页、桌面端和 QQ 普通 AI 回复的统一 Agent 链路：

1. `xiaomiao`：QQ Bot 主体。
2. `xiaomiaobot`：Vtuber Web / 桌面端。
3. `xiaomiaoAgent`：独立 Agent 框架，内部 Python 包名仍是 `nanobot`，可提供 CLI、gateway、OpenAI 兼容 API 和 WebUI。

推荐直接使用根目录 `start-all.cmd`。它会打开必要的独立终端，并按真实健康状态串行启动；新启动的终端默认最小化，前一个服务未就绪时，不会打开后续终端。

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

`xiaomiaobot` 使用 `pnpm@10.33.0`：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot
corepack enable
corepack prepare pnpm@10.33.0 --activate
pnpm install
```

### xiaomiaoAgent Python / Bun 环境

`xiaomiaoAgent` 代码包以用户可见品牌 `xiaomiaoAgent` 运行，内部 Python 包名仍是 `nanobot`。首次运行时，在 `xiaomiaoAgent` 目录从源码安装：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\xiaomiaoAgent
pip install -e .
```

如果需要运行 `xiaomiaoAgent` WebUI，还需要 Node / npm。当前 WebUI 使用 Vite，可直接通过 `npm run dev` 启动。

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

进入 `webui` 安装前端依赖：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\xiaomiaoAgent\webui
npm install
```

如果依赖已安装，可以跳过该步骤。

### 本地配置

运行前确认以下本地配置存在且正确：

- `config.json`：主目录统一模型配置，供 Web、QQ 和 Agent 共用。
- `xiaomiao/config.json`：QQ Bot、OneBot、人设和本地命令配置。
- `xiaomiaobot/**/.env`：如使用相关服务，保留本地环境变量文件。

这些文件已被根 `.gitignore` 忽略，不应提交到仓库。

主目录 `config.json` 用于控制统一 Agent backend 和第三方 OpenAI-compatible 中转站。推荐本地配置形态如下，真实配置以你的本机文件为准：

```json
{
  "nanobot_agent": {
    "enabled": true,
    "base_url": "http://127.0.0.1:8900/v1/chat/completions",
    "model": "",
    "session_id": "xiaomiao-unified",
    "timeout_seconds": 30
  },
  "nanobot": {
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

`nanobot.model` 是最终生效模型。`nanobot_agent.model` 默认留空，避免 `xiaomiao` 请求时覆盖 `nanobot.model`。

## 完整联动启动顺序

完整链路如下：

```text
stage-web 输入
    ↓
xiaomiao bridge :5519
    ↓
xiaomiaoAgent API :8900
    ↓
xiaomiaoAgent Tools / Memory / Session
    ↓
stage-web 聊天历史

QQ 群/私聊普通 AI 回复
    ↓
xiaomiao main.py
    ↓
agent_backend.py
    ↓
xiaomiaoAgent API :8900
    ↓
QQ 回复 + bridge state

xiaomiaoAgent WebUI
    ↓
xiaomiaoAgent gateway :8765
    ↓
chat_id=xiaomiao-unified / session api:xiaomiao-unified
    ↓
xiaomiao bridge events :5519
```

可以直接使用根目录 `start-all.cmd` 一键启动：

```powershell
cd F:\xiaomiaoVirtual
start-all.cmd
```

只检查依赖路径、端口占用和 HTTP / WebSocket 健康状态，不启动窗口：

```powershell
start-all.cmd --check
```

脚本启动顺序固定为：

```text
1. QQ 协议端：127.0.0.1:5004
2. xiaomiaoAgent OpenAI 兼容 API：127.0.0.1:8900
3. xiaomiaoAgent gateway：127.0.0.1:8765
4. xiaomiao main.py / bridge：127.0.0.1:5519
5. xiaomiaobot stage-web：http://127.0.0.1:5175
6. xiaomiaoAgent WebUI：http://127.0.0.1:5174
```

每一步都会先检查端口是否已被占用。QQ 协议端是例外：如果 `5004` 已经监听，脚本会明确复用现有 QQ/NapCat 进程并继续，以保留本地登录缓存。其他服务不会跳过旧进程：端口已占用时会显示 PID 并停止，因为脚本无法把旧进程重新挂到新的独立终端；端口未占用时才打开对应独立终端并等待健康检查通过。新启动的终端默认最小化，可从任务栏点开查看日志。如果在超时时间内没有就绪，脚本会停止，后续终端不会打开。

`start-all.cmd --check` 不启动窗口，只报告当前端口 PID 和健康状态。它会检查 `8900/health`、`8765` 的 WebUI bootstrap + session API + WebSocket 握手、`5519/v1/xiaomiao/status`、`main.py` 进程到 QQ OneBot `5004` 的连接、两个 Vite 页面，以及 QQ OneBot 端口。

脚本会设置 `NO_PROXY=127.0.0.1,localhost,::1` 和 `no_proxy=127.0.0.1,localhost,::1`。如果系统环境里有 `HTTP_PROXY` 或 `HTTPS_PROXY`，这一步可以避免 `main.py` 连接 NapCat 时被本地代理转到 `127.0.0.1:7897`。

QQ 本地命令 `帮助`、`关于`、`读图` 使用精确匹配。只有 `- 帮助`、`- 关于`、`- 读图` 会触发本地命令；`- 帮我写关于 agent 的知识`、`- 读图总结这张图片` 会作为普通 AI 请求进入 xiaomiaoAgent。

手动启动时需要同时打开 5 到 6 个终端。

### 终端一：启动 xiaomiaoAgent OpenAI 兼容 API

```powershell
cd F:\xiaomiaoVirtual
conda activate xiaomiao
python -m xiaomiao_agent serve --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

验证：

```text
http://127.0.0.1:8900/health
```

### 终端二：启动 NapCat

启动 NapCat 后，确认 OneBot WebSocket 监听在：

```text
127.0.0.1:5004
```

如果使用本地一键包，可以按 `docs/xiaomiao/README.md` 中的 NapCat 启动方式执行。

### 终端三：启动 xiaomiao

```powershell
cd F:\xiaomiaoVirtual\xiaomiao
conda activate xiaomiao
python main.py
```

看到下面输出表示本地 bridge 已先启动：

```text
[桌面桥接] 已启动: http://127.0.0.1:5519/v1/chat/completions
```

注意：`main.py` 会在启动 bridge 后继续执行 `Listener.run()` 连接 OneBot。如果 NapCat 未启动、端口不一致或 WebSocket 被关闭，会出现 `WebSocketConnectionClosedException`，此时主进程退出，bridge 也会随进程结束。这是完整 QQ 联动入口的预期依赖关系，不是 nanobot 或 stage-web 本身报错。

如果手动启动且系统设置了 `HTTP_PROXY` / `HTTPS_PROXY`，请先在当前终端设置本地代理绕过：

```powershell
set NO_PROXY=127.0.0.1,localhost,::1
set no_proxy=127.0.0.1,localhost,::1
```

### 终端四：启动 xiaomiaobot Web 或桌面端

Web 版：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot\apps\stage-web
pnpm exec vite --host 127.0.0.1 --port 5175
```

浏览器打开 Vite 输出的地址，通常是：

```text
http://127.0.0.1:5175/
```

Electron 桌面端：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot
pnpm dev:tamagotchi
```

第一次打开 `stage-web` 时会先通过 bridge 读取主目录 `config.json`。如果配置完整，不会弹配置面板；如果缺少中转站 URL、API Key 或模型，再按面板提示填写并同步写回主目录 `config.json`。

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

如果只看到 bridge 启动行，随后出现 OneBot WebSocket 断开错误，说明 NapCat 侧未保持连接。请先修正 NapCat 登录状态和 `xiaomiao/config.json` 的 `Connection.host` / `Connection.port`，再重新运行。

### 方式二：使用脚本启动

如果本地存在 NapCat 一键包，可直接运行：

```powershell
start.bat
```

脚本会尝试启动 NapCat，然后再启动：

```powershell
python main.py
```

## 启动 xiaomiaobot Web / 桌面端

新开一个 PowerShell 窗口，进入 `xiaomiaobot`：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot
```

启动 Web 版：

```powershell
cd apps\stage-web
pnpm exec vite --host 127.0.0.1 --port 5175
```

`stage-web` 的文本输入、移动端输入和页面级录音转文字入口都会发送到 `xiaomiao` bridge。bridge 不可用时，聊天历史中会出现明确 error 消息，不会静默回退到 xiaomiaobot provider。

启动桌面端：

```powershell
pnpm dev:tamagotchi
```

该命令会启动 `apps/stage-tamagotchi` 的 Electron 开发模式。桌面端会读取 `xiaomiao` bridge state，将回复同步到字幕、聊天历史、TTS 和 Live2D 口型。

## 启动 xiaomiaoAgent

`xiaomiaoAgent` 当前可作为独立子系统运行，不要求 `xiaomiao` 或 `xiaomiaobot` 已启动。

### 1. 初始化配置和工作区

进入 `xiaomiaoAgent` 目录：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
```

初始化项目内配置和工作区：

```powershell
conda activate xiaomiao（你自己的环境）
xiaomiao onboard `
  --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json `
  --workspace F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\workspace

如果只写 xiaomiao onboard，就是默认配置路径
```

当前项目已执行过该命令，并生成：

```text
F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\workspace\
```

`xiaomiaoAgent/.nanobot/` 已加入根 `.gitignore`，用于避免本地 API Key、会话、记忆和运行时状态被提交。

### 2. 配置模型 Provider

优先编辑主目录统一配置：

```text
F:\xiaomiaoVirtual\config.json
```

最小第三方 OpenAI-compatible 中转站示例：

```json
{
  "nanobot": {
    "provider": "custom",
    "model": "deepseek/deepseek-chat",
    "providers": {
      "custom": {
        "apiKey": "你的中转站密钥",
        "baseUrl": "https://你的中转站地址/v1"
      }
    }
  },
  "nanobot_agent": {
    "enabled": true,
    "base_url": "http://127.0.0.1:8900/v1/chat/completions",
    "model": "",
    "session_id": "xiaomiao-unified",
    "timeout_seconds": 30
  }
}
```

`xiaomiaoAgent/.nanobot/config.json` 仍保留 Agent 工作区、channel 和 runtime 配置；启动时会自动向上查找主目录 `config.json`，并用其中的 `nanobot` 段覆盖 provider 和模型。也可以用 `XIAOMIAO_UNIFIED_CONFIG` 指向自定义统一配置文件。

不要把真实 API Key 写入可提交源码文件。主目录 `config.json` 属于本机私有配置，仓库只保留 `config.example.json`。

确认 `agents.defaults.workspace` 指向项目内工作区：

```json
{
  "agents": {
    "defaults": {
      "workspace": "F:\\xiaomiaoVirtual\\xiaomiaoAgent\\.nanobot\\workspace"
    }
  }
}
```

### 3. CLI 交互运行

启动交互聊天：

```powershell
conda activate xiaomiao
xiaomiao agent --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

直接发送一条消息：

```powershell
conda activate xiaomiao
xiaomiao agent -m "你好" --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

查看状态：

```powershell
xiaomiao status
```

注意：`status` 当前不支持 `--config` 参数，只显示默认状态信息。需要使用项目内配置时，请对 `agent`、`gateway` 或 `serve` 指定 `--config`。

### 4. 启动 gateway

如果需要聊天通道、WebSocket 或 WebUI 接入，启动 gateway：

```powershell
conda activate xiaomiao
python -m xiaomiao_agent gateway --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json

如果是默认配置路径，就不用加 --config 后面的内容
```

### 5. 启动 WebUI

WebUI 需要同时运行 `xiaomiaoAgent gateway`。另开一个 PowerShell 窗口，并确保处于 `xiaomiao` conda 环境：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\xiaomiaoAgent\webui
npm run dev -- --host 127.0.0.1 --port 5174
```

当前联动链路需要使用 OpenAI 兼容 API，运行：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\xiaomiaoAgent
python -m xiaomiao_agent serve --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

如果 `xiaomiao` 命令来自源码安装，通常不需要重复执行 `pip install "nanobot-ai[api]"`；缺少 API extra 时再安装。旧 `nanobot` 命令入口仍保留兼容。

## 默认端口

```text
NapCat OneBot WebSocket: 127.0.0.1:5004
xiaomiao 桌面桥接服务: 127.0.0.1:5519
xiaomiaoAgent gateway 默认端口: 127.0.0.1:8765
xiaomiaoAgent OpenAI 兼容 API 默认端口: 127.0.0.1:8900
xiaomiaoAgent WebUI 默认端口: 127.0.0.1:5174
xiaomiaobot stage-web 默认端口: 127.0.0.1:5175
```

`xiaomiaobot` 桌面端会读取 `xiaomiao` 的本地桥接接口，将 Bot 回复同步到：

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
Ran 20 tests
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

### 验证 xiaomiaoAgent

初始化并配置模型后，运行：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
conda activate xiaomiao
python -m xiaomiao_agent serve --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

然后访问：

```text
http://127.0.0.1:8900/health
```

也可以请求 OpenAI 兼容聊天接口：

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8900/v1/chat/completions `
  -Method Post `
  -ContentType 'application/json' `
  -Body '{"messages":[{"role":"user","content":"你好，用一句话回复我。"}],"session_id":"xiaomiao-unified"}'
```

如果需要验证 gateway，可另行运行：

```powershell
conda activate xiaomiao
python -m xiaomiao_agent gateway --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

再检查日志中是否出现 gateway 启动和通道加载信息。

## 常见问题

### NapCat 连接失败

检查 NapCat 是否已登录，并确认 OneBot WebSocket 端口是：

```text
127.0.0.1:5004
```

同时检查 `xiaomiao/config.json` 中的连接配置是否指向该地址。

如果控制台先输出了：

```text
[桌面桥接] 已启动: http://127.0.0.1:5519/v1/chat/completions
```

随后报：

```text
WebSocketConnectionClosedException: Connection to remote host was lost.
```

说明 `python main.py` 已启动 bridge，但后续连接 OneBot 失败。先启动或修复 NapCat，再重新运行 `python main.py`。

### xiaomiaobot 无法同步小喵回复

先确认 `xiaomiao serve` 和 `xiaomiao` 都已启动，并检查桥接状态接口：

```text
http://127.0.0.1:5519/v1/xiaomiao/status
```

如果接口不可访问，优先检查 `python main.py` 是否仍在运行。如果接口可访问但聊天返回 error，再检查 `http://127.0.0.1:8900/health`。

### stage-web 发送后出现 bridge 错误

`stage-web` 当前必须走 `xiaomiao` bridge。常见原因：

- `python main.py` 因 NapCat 连接失败退出，导致 `5519` 不存在。
- `xiaomiao serve` 未启动，导致 bridge callback 返回 HTTP 502。
- `nanobot_agent.base_url` 与实际 xiaomiaoAgent API 地址不一致。
- xiaomiaoAgent 模型回复超过 `timeout_seconds`。

该路径不会静默回退到 xiaomiaobot provider，错误会显示在聊天历史中。

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

### xiaomiao 命令不存在

确认已经在 `xiaomiaoAgent` 目录执行源码安装：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
pip install -e .
```

如果仍找不到命令，使用当前 Python 重新安装，或确认 Python Scripts 目录已加入 `PATH`。

### xiaomiaoAgent WebUI 无法连接

WebUI 需要 `xiaomiao gateway` 同时运行。请确认已经在另一个终端启动：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
conda activate xiaomiao
python -m xiaomiao_agent gateway --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

## 推荐日常启动命令

终端一：

```powershell
cd F:\xiaomiaoVirtual
conda activate xiaomiao
python -m xiaomiao_agent serve --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

终端二：启动 NapCat，确认 OneBot WebSocket 是 `127.0.0.1:5004`。

终端三：

```powershell
cd F:\xiaomiaoVirtual\xiaomiao
conda activate xiaomiao
python main.py
```

终端四，Web 版：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot\apps\stage-web
pnpm exec vite --host 127.0.0.1 --port 5175
```

或终端四，桌面端：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaobot
pnpm dev:tamagotchi
```

可选终端三（xiaomiaoAgent CLI 或 gateway）：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
conda activate xiaomiao
xiaomiao agent --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

或：

```powershell
cd F:\xiaomiaoVirtual\xiaomiaoAgent
conda activate xiaomiao
python -m xiaomiao_agent gateway --config F:\xiaomiaoVirtual\xiaomiaoAgent\.nanobot\config.json
```

可选终端四（xiaomiaoAgent WebUI）：

```powershell
conda activate xiaomiao
cd F:\xiaomiaoVirtual\xiaomiaoAgent\webui
npm run dev -- --host 127.0.0.1 --port 5174
```
