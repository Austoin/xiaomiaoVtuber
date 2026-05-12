# xiaomiaoVirtual 启动指南

本文说明如何在本机启动 `xiaomiaoVirtual` 的两个核心部分：

1. `xiaomiao`：QQ Bot 主体。
2. `AuBot`：Vtuber 桌面端。

推荐启动顺序：先启动 NapCat 和 `xiaomiao`，再启动 `AuBot` 桌面端。

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

## 默认端口

```text
NapCat OneBot WebSocket: 127.0.0.1:5004
xiaomiao 桌面桥接服务: 127.0.0.1:5519
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
