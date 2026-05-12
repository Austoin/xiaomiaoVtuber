# 小喵 QQ 机器人 - Linux 部署指南

## 部署文件说明

| 文件 | 说明 |
|------|------|
| `xiaomiaoVirtual.zip` | 机器人完整代码包 |
| `deploy.sh` | 一键部署脚本 |
| `pack.bat` | Windows 打包脚本（开发用） |
| `README_DEPLOY.md` | 本部署文档 |

### deploy.sh 脚本功能

`deploy.sh` 是一键部署脚本，自动完成以下所有步骤：

1. **系统检测** - 自动识别 CentOS/Ubuntu/OpenCloudOS/Debian 等系统
2. **依赖安装** - 安装 Python3、pip、Docker、unzip 等必要软件
3. **目录创建** - 创建 logs、temps、napcat_data 等目录
4. **项目解压** - 解压 xiaomiaoVirtual.zip
5. **Python 环境** - 创建虚拟环境并安装 requirements.txt 依赖
6. **NapCat 部署** - 拉取 Docker 镜像并创建容器
7. **NapCat 配置** - 自动生成 WebSocket 配置文件
8. **机器人配置** - 更新 config.json 连接参数
9. **脚本生成** - 创建 start.sh、stop.sh、restart.sh
10. **服务注册** - 创建 systemd 服务实现开机自启

---

## 快速部署

### 方式一：一键部署脚本（推荐）

1. **上传文件到服务器**
   ```bash
   # 在宝塔文件管理器中上传 xiaomiaoVirtual.zip 到 /www/wwwroot/
   # 或使用 scp 命令
   scp xiaomiaoVirtual.zip root@你的服务器IP:/www/wwwroot/
   ```

2. **解压并运行部署脚本**
   ```bash
   cd /www/wwwroot/
   mkdir xiaomiaoVirtual
   mv xiaomiaoVirtual.zip xiaomiaoVirtual/
   cd xiaomiaoVirtual
   unzip xiaomiaoVirtual.zip
   chmod +x deploy/deploy.sh
   bash deploy/deploy.sh
   ```

3. **按提示输入 QQ 号，等待部署完成**

4. **扫码登录**
   ```bash
   # 查看登录二维码
   docker logs -f napcat
   
   # 或访问 WebUI
   http://你的服务器IP:6099
   ```

5. **启动机器人**
   ```bash
   systemctl start xiaomiao-bot
   ```

---

### 方式二：手动部署（完整步骤）

以下是在 OpenCloudOS 9 上完整部署的详细步骤，同样适用于 CentOS、RHEL、Fedora 等系统。

#### 1. 安装系统依赖

```bash
# RHEL/CentOS/OpenCloudOS 系列
dnf install -y python3 python3-pip docker unzip wget curl

# 安装 Python 虚拟环境支持
# 注意：RHEL 系列使用 python3-virtualenv，不是 python3-venv
dnf install -y python3-virtualenv

# Ubuntu/Debian 系列
apt install -y python3 python3-pip python3-venv docker.io unzip wget curl

# 启动并启用 Docker
systemctl start docker
systemctl enable docker
```

#### 2. 上传并解压项目

```bash
cd /www/wwwroot/
mkdir -p xiaomiaoVirtual
cd xiaomiaoVirtual

# 上传 xiaomiaoVirtual.zip 后解压
unzip xiaomiaoVirtual.zip

# 创建必要目录
mkdir -p logs temps napcat_data
```

#### 3. 创建 Python 虚拟环境

```bash
cd /www/wwwroot/xiaomiaoVirtual

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip（可选）
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

#### 4. 部署 NapCat Docker

```bash
# 创建数据目录
mkdir -p /www/wwwroot/xiaomiaoVirtual/napcat_data

# 拉取镜像
docker pull mlikiowa/napcat-docker:latest

# 运行容器（将 你的QQ号 替换为实际号码）
docker run -d \
  --name napcat \
  -e ACCOUNT=你的QQ号 \
  -e WS_ENABLE=true \
  -p 3001:3000 \
  -p 5004:3001 \
  -p 6099:6099 \
  -v /www/wwwroot/xiaomiaoVirtual/napcat_data:/app/napcat/config \
  --restart always \
  mlikiowa/napcat-docker:latest
```

**端口说明**：
| 主机端口 | 容器端口 | 用途 |
|---------|---------|------|
| 3001 | 3000 | NapCat HTTP 接口 |
| 5004 | 3001 | WebSocket 服务（机器人连接用） |
| 6099 | 6099 | NapCat WebUI |

> **注意**：如果端口 3000 被占用（如 openwebui），可以改用其他端口如 3001。

#### 5. 扫码登录 QQ

```bash
# 查看登录二维码
docker logs -f napcat

# 按 Ctrl+C 退出日志查看
```

或者访问 WebUI：`http://你的服务器IP:6099`

#### 6. 配置 NapCat WebSocket

登录成功后，需要配置 WebSocket 服务器。创建或更新配置文件：

```bash
cat > /www/wwwroot/xiaomiaoVirtual/napcat_data/onebot11_你的QQ号.json << 'EOF'
{
  "network": {
    "httpServers": [],
    "httpSseServers": [],
    "httpClients": [],
    "websocketServers": [
      {
        "name": "Bot",
        "enable": true,
        "host": "0.0.0.0",
        "port": 3001,
        "token": "",
        "heartInterval": 30000,
        "enableForcePushEvent": true,
        "debug": false,
        "messagePostFormat": "array"
      }
    ],
    "websocketClients": [],
    "plugins": []
  },
  "musicSignUrl": "",
  "enableLocalFile2Url": true,
  "parseMultMsg": true,
  "imageDownloadProxy": ""
}
EOF

# 重启 NapCat 使配置生效
docker restart napcat
```

> **重要**：将 `你的QQ号` 替换为实际的 QQ 号码，如 `onebot11_123456789.json`

#### 7. 确认机器人配置

检查 `config.json` 中的连接配置：

```json
{
    "Connection": {
        "mode": "FWS",
        "host": "127.0.0.1",
        "port": 5004
    }
}
```

确保 `port` 与 Docker 映射的 WebSocket 端口一致（默认 5004）。

#### 8. 创建 Systemd 服务

```bash
cat > /etc/systemd/system/xiaomiao-bot.service << 'EOF'
[Unit]
Description=XiaoMiao QQ Bot
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/www/wwwroot/xiaomiaoVirtual
ExecStart=/www/wwwroot/xiaomiaoVirtual/venv/bin/python /www/wwwroot/xiaomiaoVirtual/main.py
ExecStop=/bin/kill -SIGTERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重载 systemd 配置
systemctl daemon-reload

# 启用开机自启
systemctl enable xiaomiao-bot
```

#### 9. 启动机器人

```bash
# 启动服务
systemctl start xiaomiao-bot

# 查看状态
systemctl status xiaomiao-bot

# 查看日志
journalctl -u xiaomiao-bot -f
```

---

## 常用命令

### 机器人管理

```bash
# 启动
systemctl start xiaomiao-bot

# 停止
systemctl stop xiaomiao-bot

# 重启
systemctl restart xiaomiao-bot

# 查看状态
systemctl status xiaomiao-bot

# 查看实时日志
journalctl -u xiaomiao-bot -f

# 查看最近 100 行日志
journalctl -u xiaomiao-bot -n 100 --no-pager
```

### NapCat 管理

```bash
# 查看日志（含登录二维码）
docker logs -f napcat

# 查看最近日志
docker logs napcat --tail 100

# 重启
docker restart napcat

# 停止
docker stop napcat

# 启动
docker start napcat

# 删除容器（需要重新创建）
docker rm -f napcat

# 查看容器状态
docker ps -a | grep napcat
```

---

## 常见问题排查

### 1. python3-venv 安装失败（RHEL/CentOS/OpenCloudOS）

**错误信息**：
```
No match for argument: python3-venv
Error: Unable to find a match: python3-venv
```

**解决方案**：RHEL 系列系统使用不同的包名
```bash
# 使用 python3-virtualenv 代替
dnf install -y python3-virtualenv
```

### 2. Docker 端口冲突

**错误信息**：
```
Bind for 0.0.0.0:3000 failed: port is already allocated
```

**解决方案**：
```bash
# 查看占用端口的容器
docker ps

# 方案1：停止占用端口的容器
docker stop <容器名>

# 方案2：使用其他端口重新创建 napcat
docker rm -f napcat
docker run -d \
  --name napcat \
  -e ACCOUNT=你的QQ号 \
  -e WS_ENABLE=true \
  -p 3001:3000 \
  -p 5004:3001 \
  -p 6099:6099 \
  -v /www/wwwroot/xiaomiaoVirtual/napcat_data:/app/napcat/config \
  --restart always \
  mlikiowa/napcat-docker:latest
```

### 3. 机器人无法连接 NapCat（ConnectionResetError）

**错误信息**：
```
ConnectionResetError: [Errno 104] Connection reset by peer
```

**原因**：NapCat 的 WebSocket 服务器未配置或未启动

**排查步骤**：
```bash
# 1. 检查 NapCat 是否运行
docker ps | grep napcat

# 2. 检查 QQ 是否已登录
docker logs napcat --tail 30

# 3. 检查 WebSocket 配置
cat /www/wwwroot/xiaomiaoVirtual/napcat_data/onebot11_你的QQ号.json

# 4. 确认 websocketServers 不为空数组
# 如果为空，需要按照上面步骤 6 创建配置
```

**解决方案**：确保 `onebot11_你的QQ号.json` 中的 `websocketServers` 配置正确，然后重启 NapCat：
```bash
docker restart napcat
sleep 5
systemctl restart xiaomiao-bot
```

### 4. systemd 服务不存在

**错误信息**：
```
Failed to start xiaomiao-bot.service: Unit xiaomiao-bot.service not found.
```

**解决方案**：按照上面步骤 8 创建 systemd 服务文件。

### 5. 虚拟环境不存在

**错误信息**：
```
-bash: venv/bin/activate: No such file or directory
```

**解决方案**：
```bash
cd /www/wwwroot/xiaomiaoVirtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 单独安装问题依赖
pip install pillow
pip install google-generativeai==0.7.2
```

### 7. 防火墙问题

```bash
# 开放端口（如果需要外网访问 WebUI）
firewall-cmd --add-port=6099/tcp --permanent
firewall-cmd --add-port=5004/tcp --permanent
firewall-cmd --reload

# 或使用 iptables
iptables -A INPUT -p tcp --dport 6099 -j ACCEPT
iptables -A INPUT -p tcp --dport 5004 -j ACCEPT
```

---

## 目录结构

```
/www/wwwroot/xiaomiaoVirtual/
├── main.py              # 主程序
├── config.json          # 机器人配置文件
├── requirements.txt     # Python 依赖
├── venv/                # Python 虚拟环境
├── logs/                # 日志目录
├── temps/               # 临时文件
├── napcat_data/         # NapCat 配置和数据
│   ├── onebot11_QQ号.json  # WebSocket 配置
│   ├── napcat_QQ号.json    # NapCat 基础配置
│   └── webui.json          # WebUI 配置
├── deploy/              # 部署相关文件
│   ├── deploy.sh        # 一键部署脚本
│   └── README_DEPLOY.md # 本文档
├── start.sh             # 启动脚本
├── stop.sh              # 停止脚本
└── restart.sh           # 重启脚本
```

---

## 更新机器人

```bash
cd /www/wwwroot/xiaomiaoVirtual

# 停止机器人
systemctl stop xiaomiao-bot

# 备份配置
cp config.json config.json.bak
cp -r napcat_data napcat_data.bak

# 上传新文件并解压
unzip -o xiaomiaoVirtual_new.zip

# 恢复配置
cp config.json.bak config.json

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 启动机器人
systemctl start xiaomiao-bot
```

---

## 完全卸载

```bash
# 停止并删除服务
systemctl stop xiaomiao-bot
systemctl disable xiaomiao-bot
rm /etc/systemd/system/xiaomiao-bot.service
systemctl daemon-reload

# 删除 NapCat 容器
docker rm -f napcat

# 删除项目目录（谨慎操作）
rm -rf /www/wwwroot/xiaomiaoVirtual
```

---

## 系统兼容性

| 系统 | 包管理器 | Python venv 包名 | 测试状态 |
|------|---------|-----------------|---------|
| OpenCloudOS 9 | dnf | python3-virtualenv | 已验证 |
| CentOS 8/9 | dnf | python3-virtualenv | 兼容 |
| RHEL 8/9 | dnf | python3-virtualenv | 兼容 |
| Fedora | dnf | python3-virtualenv | 兼容 |
| Ubuntu 20.04+ | apt | python3-venv | 兼容 |
| Debian 11+ | apt | python3-venv | 兼容 |
