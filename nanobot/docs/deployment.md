# 部署

## Docker

> [!TIP]
> `-v ~/.nanobot:/home/nanobot/.nanobot` 会把本地配置目录挂载进容器，因此配置和工作区会在容器重启后保留。
> 容器以非 root 用户 `nanobot`（UID 1000）运行，并从 `/home/nanobot/.nanobot` 读取配置。始终把宿主机配置目录挂载到 `/home/nanobot/.nanobot`，不要挂载到 `/root/.nanobot`。
> 如果遇到 **Permission denied**，请先在宿主机修复所有权：`sudo chown -R 1000:1000 ~/.nanobot`，或传入 `--user $(id -u):$(id -g)` 以匹配宿主机 UID。Podman 用户可以改用 `--userns=keep-id`。
>
> [!IMPORTANT]
> 官方 Docker 用法目前是使用本仓库内置 `Dockerfile` 自行构建。第三方命名空间下的 Docker Hub 镜像并非由 HKUDS/nanobot 维护或验证；除非你信任发布者，否则不要把 API Key 或 Bot token 挂载进去。

### Docker Compose

```bash
docker compose run --rm nanobot-cli onboard   # 首次设置
vim ~/.nanobot/config.json                     # 添加 API Key
docker compose up -d nanobot-gateway           # 启动 gateway
```

```bash
docker compose run --rm nanobot-cli agent -m "Hello!"   # 运行 CLI
docker compose logs -f nanobot-gateway                   # 查看日志
docker compose down                                      # 停止
```

### Docker

```bash
# 构建镜像
docker build -t nanobot .

# 初始化配置（仅首次）
docker run -v ~/.nanobot:/home/nanobot/.nanobot --rm nanobot onboard

# 在宿主机编辑配置，添加 API Key
vim ~/.nanobot/config.json

# 运行 gateway（连接已启用通道，例如 Telegram/Discord/Mochat）
docker run -v ~/.nanobot:/home/nanobot/.nanobot -p 18790:18790 nanobot gateway

# 或运行单条命令
docker run -v ~/.nanobot:/home/nanobot/.nanobot --rm nanobot agent -m "Hello!"
docker run -v ~/.nanobot:/home/nanobot/.nanobot --rm nanobot status
```

## Linux Service

将 gateway 作为 systemd 用户服务运行，让它自动启动并在失败后重启。

**1. 找到 nanobot 可执行文件路径：**

```bash
which nanobot   # e.g. /home/user/.local/bin/nanobot
```

**2. 在 `~/.config/systemd/user/nanobot-gateway.service` 创建 service 文件**（如有需要，替换 `ExecStart` 路径）：

```ini
[Unit]
Description=Nanobot Gateway
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/nanobot gateway
Restart=always
RestartSec=10
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=%h

[Install]
WantedBy=default.target
```

**3. 启用并启动：**

```bash
systemctl --user daemon-reload
systemctl --user enable --now nanobot-gateway
```

**常用操作：**

```bash
systemctl --user status nanobot-gateway        # 检查状态
systemctl --user restart nanobot-gateway       # 配置变更后重启
journalctl --user -u nanobot-gateway -f        # 跟随日志
```

如果编辑了 `.service` 文件本身，请在重启前运行 `systemctl --user daemon-reload`。

> **注意：** 用户服务默认只会在你登录期间运行。若要在退出登录后继续运行 gateway，请启用 lingering：
>
> ```bash
> loginctl enable-linger $USER
> ```

## macOS LaunchAgent

如果希望 `nanobot gateway` 在你登录后保持在线，同时不需要开着终端，可以使用 LaunchAgent。

**1. 获取 `nanobot` 的绝对路径：**

```bash
which nanobot   # e.g. /Users/youruser/.local/bin/nanobot
```

请在 plist 中使用这个精确路径。这样可以保留你的安装方式对应的 Python 环境。

**2. 创建 `~/Library/LaunchAgents/ai.nanobot.gateway.plist`：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>ai.nanobot.gateway</string>

  <key>ProgramArguments</key>
  <array>
    <string>/Users/youruser/.local/bin/nanobot</string>
    <string>gateway</string>
    <string>--workspace</string>
    <string>/Users/youruser/.nanobot/workspace</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/Users/youruser/.nanobot/workspace</string>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <dict>
    <key>SuccessfulExit</key>
    <false/>
  </dict>

  <key>StandardOutPath</key>
  <string>/Users/youruser/.nanobot/logs/gateway.log</string>

  <key>StandardErrorPath</key>
  <string>/Users/youruser/.nanobot/logs/gateway.error.log</string>
</dict>
</plist>
```

**3. 加载并启动：**

```bash
mkdir -p ~/Library/LaunchAgents ~/.nanobot/logs
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.nanobot.gateway.plist
launchctl enable gui/$(id -u)/ai.nanobot.gateway
launchctl kickstart -k gui/$(id -u)/ai.nanobot.gateway
```

**常用操作：**

```bash
launchctl list | grep ai.nanobot.gateway
launchctl kickstart -k gui/$(id -u)/ai.nanobot.gateway   # 重启
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.nanobot.gateway.plist
```

编辑 plist 后，请再次运行 `launchctl bootout ...` 和 `launchctl bootstrap ...`。

> **注意：** 如果启动失败并提示 “address already in use”，请先停止手动启动的 `nanobot gateway` 进程。
