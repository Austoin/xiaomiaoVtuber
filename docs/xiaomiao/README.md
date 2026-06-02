# 小喵 XiaoMiao QQ Bot

基于 NapCat + HypeR Bot 框架的 QQ 机器人，支持 AI 对话、图片生成、群管理等功能。

## 目录

- [快速开始](#快速开始)
- [Linux 服务器部署](#linux-服务器部署)
- [配置说明](#配置说明)
- [人设修改](#人设修改)
- [API 接口配置](#api-接口配置)
- [功能命令](#功能命令)
- [文件结构](#文件结构)

---

## 快速开始

### 环境要求

- Windows 10/11
- Python 3.10+
- QQ 账号

### 安装步骤

1. **安装 Python 依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **下载 NapCat**
   - 访问 https://github.com/NapNeko/NapCatQQ/releases
   - 下载 `NapCat.Shell.Windows.OneKey.zip`
   - 解压到项目目录

3. **首次运行**
   - 运行 NapCat 安装程序完成安装
   - 扫码登录 QQ

### 启动方式

**方式一：双击启动脚本**
```
双击 start.bat
```

**方式二：手动启动**
```bash
# 1. 启动 NapCat（在 NapCat 目录下）
napcat.quick.bat <QQ号> 

也就是：
cd /d F:\xiaomiaoVirtual\xiaomiao\NapCat.Shell.Windows.OneKey\NapCat.44498.Shell
.\napcat.quick.bat 3994383071

# 2. 等待看到 "WebSocket服务: 127.0.0.1:5004" 后
# 3. 启动机器人
python main.py
```

启动成功后会先看到本地 bridge：

```text
[桌面桥接] 已启动: http://127.0.0.1:5519/v1/chat/completions
```

随后 `main.py` 会继续连接 NapCat / OneBot。如果 NapCat 未启动、端口不一致或 WebSocket 被关闭，程序会报 `WebSocketConnectionClosedException` 并退出，bridge 也会随进程结束。出现这种情况时，先修复 NapCat 登录状态和 OneBot WebSocket，再重新运行 `python main.py`。

### 与 nanobot / AuBot 联动启动

当前 QQ 群/私聊普通 AI 回复、`AuBot stage-web` 输入和桌面 bridge 都统一进入 nanobot Agent。完整联动需要按顺序启动：

1. 启动 nanobot OpenAI 兼容 API：

   ```powershell
   cd F:\xiaomiaoVirtual
   conda activate xiaomiao
   nanobot serve --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json
   ```

2. 启动 NapCat，并确认 OneBot WebSocket 是 `127.0.0.1:5004`。

3. 启动小喵：

   ```powershell
   cd F:\xiaomiaoVirtual\xiaomiao
   conda activate xiaomiao
   python main.py
   ```

4. 启动 AuBot Web 或桌面端：

   ```powershell
   cd F:\xiaomiaoVirtual\AuBot
   pnpm dev:web
   # 或
   pnpm dev:tamagotchi
   ```

联动端口：

```text
5004  NapCat OneBot WebSocket
5519  xiaomiao desktop bridge
8900  nanobot OpenAI-compatible API
```

`stage-web` 必须走 `xiaomiao` bridge。bridge 或 nanobot 不可用时，网页聊天历史会显示明确错误，不会静默回退到 AuBot provider。

---

## Linux 服务器部署

支持部署到宝塔面板 / CentOS / Ubuntu / Debian / OpenCloudOS 服务器。

### 方式一：一键部署（推荐）

#### 1. 在 Windows 上打包

双击运行 `deploy/pack.bat`，生成 `deploy/xiaomiaoVirtual.zip`

#### 2. 上传到服务器

将 `xiaomiaoVirtual.zip` 上传到宝塔的 `/www/wwwroot/` 目录

#### 3. SSH 执行部署

```bash
cd /www/wwwroot/
mkdir xiaomiaoVirtual
mv xiaomiaoVirtual.zip xiaomiaoVirtual/
cd xiaomiaoVirtual
unzip xiaomiaoVirtual.zip
chmod +x deploy/deploy.sh
bash deploy/deploy.sh
```

#### 4. 部署流程详解

**步骤 1：输入 QQ 号**

脚本会提示输入机器人 QQ 号，输入后按回车。

**步骤 2：等待自动安装**

脚本会自动安装 Python、Docker、依赖包等，需要几分钟。

**步骤 3：扫码登录 QQ**

```bash
# 查看登录二维码
docker logs -f napcat

# 或访问 WebUI（需开放 6099 端口）
http://你的服务器IP:6099
```

用手机 QQ 扫码登录，按 `Ctrl+C` 退出日志查看。

**步骤 4：启动机器人**

```bash
systemctl start xiaomiao-bot
```

**步骤 5：验证运行**

```bash
# 查看状态
systemctl status xiaomiao-bot

# 查看日志
journalctl -u xiaomiao-bot -f
```

### 方式二：手动部署

#### 1. 安装依赖

```bash
# CentOS / OpenCloudOS
yum install -y python3 python3-pip docker unzip

# Ubuntu / Debian
apt install -y python3 python3-pip docker.io unzip

# 启动 Docker
systemctl start docker && systemctl enable docker
```

#### 2. 创建 Python 环境

```bash
cd /www/wwwroot/xiaomiaoVirtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. 部署 NapCat Docker

```bash
docker run -d \
  --name napcat \
  -e ACCOUNT=你的QQ号 \
  -e WS_ENABLE=true \
  -p 3000:3000 \
  -p 5004:3001 \
  -p 6099:6099 \
  -v /www/wwwroot/xiaomiaoVirtual/napcat_data:/app/napcat/config \
  --restart always \
  mlikiowa/napcat-docker:latest
```

#### 4. 配置 NapCat

创建 `napcat_data/onebot11_你的QQ号.json`：

```json
{
    "network": {
        "websocketServers": [{
            "name": "Bot",
            "enable": true,
            "host": "0.0.0.0",
            "port": 3001,
            "messagePostFormat": "array"
        }]
    }
}
```

#### 5. 启动机器人

```bash
# 后台运行
nohup ./start.sh > logs/bot.log 2>&1 &

# 或使用 systemd
systemctl start xiaomiao-bot
```

### 常用命令

| 操作 | 命令 |
|------|------|
| 启动机器人 | `systemctl start xiaomiao-bot` |
| 停止机器人 | `systemctl stop xiaomiao-bot` |
| 重启机器人 | `systemctl restart xiaomiao-bot` |
| 查看状态 | `systemctl status xiaomiao-bot` |
| 查看日志 | `journalctl -u xiaomiao-bot -f` |
| 重启 NapCat | `docker restart napcat` |
| 查看 NapCat 日志 | `docker logs -f napcat` |
| 重新登录 QQ | `docker restart napcat && docker logs -f napcat` |

### 服务器要求

- 系统：CentOS 7+ / Ubuntu 18.04+ / Debian 10+ / OpenCloudOS
- 配置：2 核 2G 内存以上
- 软件：Docker、Python 3.10+

### 端口说明

| 端口 | 用途 | 是否需要开放 |
|------|------|-------------|
| 5004 | 机器人与 NapCat 通信 | 不需要（内网通信） |
| 6099 | NapCat WebUI | 可选（外网访问时需要） |
| 3000 | NapCat HTTP API | 可选（外网访问时需要） |

**大多数情况下不需要开放任何端口**，因为机器人和 NapCat 都在同一台服务器上通过 `127.0.0.1` 内网通信。

**需要开放端口的情况：**
- 想从外网浏览器访问 NapCat WebUI 进行配置 → 开放 6099
- 想从其他服务器调用 NapCat API → 开放 3000

**开放端口命令（如需要）：**
```bash
# 防火墙开放端口
firewall-cmd --add-port=6099/tcp --permanent
firewall-cmd --reload

# 或使用宝塔面板 -> 安全 -> 放行端口
```

### 更新已部署的机器人

当你修改了 `main.py` 或其他文件后，部署脚本仍然有效。按以下步骤更新：

#### 1. 在 Windows 上重新打包

```batch
双击 deploy/pack.bat
```

#### 2. 上传新的 zip 到服务器

通过宝塔文件管理器或 scp 命令上传

#### 3. SSH 执行更新

```bash
cd /www/wwwroot/xiaomiaoVirtual

# 停止机器人
systemctl stop xiaomiao-bot

# 备份配置
cp config.json config.json.bak

# 解压覆盖（-o 表示覆盖已有文件）
unzip -o xiaomiaoVirtual.zip

# 恢复配置
cp config.json.bak config.json

# 更新依赖（如果有新增）
source venv/bin/activate
pip install -r requirements.txt

# 重启机器人
systemctl start xiaomiao-bot
```

### 修改代码后的注意事项

| 修改类型 | 需要的操作 |
|----------|-----------|
| 修改 main.py 等现有文件 | 直接重新打包上传即可 |
| 添加新的 Python 依赖 | 更新 `requirements.txt` 后打包 |
| 添加新的文件/目录 | 修改 `deploy/pack.bat` 添加到打包列表 |
| 修改 config.json 结构 | 服务器上需手动更新配置或合并 |

#### 添加新文件到打包列表

编辑 `deploy/pack.bat`，在文件列表中添加新文件：

```batch
7z a -tzip "%OUTPUT_DIR%%ZIP_NAME%" ^
    main.py ^
    config.json ^
    ...
    新文件.py ^      REM 添加新文件
    新目录 ^         REM 添加新目录
```

---

## 配置说明

配置文件：`config.json`

本项目不使用图形化配置向导。所有设置都通过编辑配置文件完成：

- `config.json`：连接参数、模型 API、机器人名称、命令前缀、ROOT 用户等主配置
- `runtime/Super_User.ini`：超级用户列表，每行一个 QQ 号
- `runtime/Manage_User.ini`：管理员列表，每行一个 QQ 号
- `runtime/sisters.ini`：姐姐模式用户列表，每行一个 QQ 号
- `runtime/jhq.ini`：妈妈模式用户列表，每行一个 QQ 号
- `runtime/programmers.ini`：高级程序员模式用户列表，每行一个 QQ 号
- `runtime/blacklist.sr`：定时消息群发黑名单，每行一个群号
- `runtime/timing_message.ini`：定时消息，格式为 `HH:MM⊕内容`

### 图形化配置说明

图形化配置向导已删除。部署、启动和日常维护不需要安装 Qt 相关依赖，也不再提供 `SetupWizard.pyw` / `wizardWindows/` 可视化面板入口。

以下资源仍被机器人功能使用，不要作为图形化配置资源删除：

- `assets/quote/mask.png`：名言图片遮罩
- `assets/*.ttf`：名言图片字体
- `temps/`：运行时临时文件目录

```json
{
    "owner": ["QQ号"],           // 机器人主人
    "black_list": [],            // 黑名单
    "silents": [],               // 静默列表（不响应）
    "Connection": {
        "mode": "FWS",           // 连接模式：FWS(正向WebSocket) / HTTP
        "host": "127.0.0.1",     // NapCat 地址
        "port": 5004,            // NapCat 端口
        "listener_host": "127.0.0.1",  // 监听地址
        "listener_port": 5003,   // 监听端口
        "retries": 5,            // 重连次数
        "satori_token": ""       // Satori 协议 Token（可选）
    },
    "Log_level": "DEBUG",        // 日志级别：DEBUG/INFO/WARNING/ERROR
    "protocol": "OneBot",        // 协议类型
    "Others": {
        "gemini_key": "",        // 主模型 API Key
        "gemini_base_url": "",   // 主模型 API 地址（支持中转站）
        "openai_key": "",        // OpenAI API Key
        "openai_base_url": "",   // OpenAI API 地址
        "default_model": "gemini-3-flash-preview",  // 默认模型
        "fallback_model": "deepseek-v3",            // 候补模型（主模型失败时使用）
        "fallback_key": "",      // 候补模型 API Key
        "bot_name": "小喵",       // 机器人名称
        "bot_name_en": "XiaoMiao", // 机器人英文名
        "ROOT_User": [],         // 超级管理员
        "Auto_approval": [],     // 自动审批关键词
        "reminder": "- "         // 命令前缀
    },
    "uin": 0                     // 机器人 QQ 号（自动填充）
}
```

### 权限配置

| 文件 | 说明 |
|------|------|
| `runtime/Super_User.ini` | 超级用户（每行一个QQ号） |
| `runtime/Manage_User.ini` | 管理用户 |
| `runtime/sisters.ini` | 姐姐模式用户 |
| `runtime/jhq.ini` | 妈妈模式用户（血小板） |
| `runtime/programmers.ini` | 高级程序员模式用户 |
| `runtime/blacklist.sr` | 黑名单 |

---

## 人设修改

人设配置文件：`prerequisites.py`

### 四种角色模式

1. **女朋友模式**
   - 函数：`girl_friend()`
   - 特点：温柔可爱、会撒娇、傲娇

2. **姐姐模式**
   - 函数：`sister()`
   - 特点：温柔能干、照顾妹妹
   - 触发：用户发送 `- 做我姐姐吧`

3. **妈妈模式**（巨核细胞）
   - 函数：`mother()`
   - 特点：耐心可靠、慈爱
   - 触发：用户发送 `- 做我mm吧`

4. **高级程序员模式**（默认）
   - 函数：`senior_programmer()`
   - 特点：资深工程师风格，擅长架构设计、代码审查、性能优化、调试定位和测试设计
   - 触发：默认启用，或用户发送 `- 程序员`

### 切换到高级程序员模式

高级程序员模式是默认人格。也可以通过发送 `- 程序员` 切换回来，或直接把 QQ 号写入 `runtime/programmers.ini`：

```text
你的QQ号
```

保存后重启 `python main.py` 生效。若同一 QQ 同时存在于 `runtime/programmers.ini` 和 `runtime/sisters.ini` / `runtime/jhq.ini`，优先使用高级程序员模式。

高级程序员的人设文本在 `config.json` 的 `Others.personas.senior_programmer` 中修改。

### 修改人设示例

编辑 `prerequisites.py`：

```python
class prerequisite:
    def __init__(self, bot_name: str, event_user: str):
        self.bot_name = bot_name
        self.event_user = event_user
        
    def girl_friend(self) -> str:
        return f"""你叫{self.bot_name}，是一个温柔可爱的少女...
        
        # 在这里修改人设提示词
        # {self.bot_name} 会被替换为机器人名称
        # {self.event_user} 会被替换为用户昵称
        """
```

### 人设提示词要点

1. 定义角色身份和性格特点
2. 设置与用户的关系
3. 规定回答风格（口语化、简短）
4. 设置禁止事项（不承认是AI等）
5. 可使用颜文字和 Emoji

---

## API 接口配置

### AI 对话 API

在 `config.json` 的 `Others` 中配置：

```json
{
    "Others": {
        "gemini_key": "你的API密钥",
        "gemini_base_url": "https://privnode.com/v1/",
        "openai_key": "你的API密钥",
        "openai_base_url": "https://privnode.com/v1/",
        "default_model": "gemini-3-flash-preview",
        "fallback_model": "deepseek-v3",
        "fallback_key": "候补模型的API密钥"
    }
}
```

### nanobot Agent backend

普通 AI 回复主路径现在通过 `Others.nanobot_agent` 接入 nanobot：

```json
{
    "Others": {
        "nanobot_agent": {
            "enabled": true,
            "base_url": "http://127.0.0.1:8900/v1/chat/completions",
            "model": "deepseek-chat",
            "session_id": "xiaomiao-unified",
            "timeout_seconds": 30
        }
    }
}
```

字段说明：

| 配置项 | 说明 |
|--------|------|
| `enabled` | 是否启用统一 Agent backend，默认启用 |
| `base_url` | nanobot OpenAI 兼容聊天接口 |
| `model` | 可选模型名，为空时由 nanobot 默认模型决定 |
| `session_id` | 统一会话 ID，默认 `xiaomiao-unified` |
| `timeout_seconds` | 请求超时时间，默认 `30` |

命令型功能、权限管理、生图、撤回、配置类命令和 `SearchOnline(...)` 分支仍保留原逻辑。

**模型配置说明：**

| 配置项 | 说明 |
|--------|------|
| `default_model` | 默认使用的模型（如 gemini-3-flash-preview） |
| `fallback_model` | 候补模型，主模型失败时自动切换（如 deepseek-v3） |
| `fallback_key` | 候补模型使用的 API Key |

**支持的 API 提供商：**

| 提供商 | 说明 |
|--------|------|
| OpenAI 官方 | `https://api.openai.com/v1/` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| 第三方中转 | 如 `https://privnode.com/v1/` |

### 图片生成 API

代码中使用的第三方 API（无需配置）：

| API | 用途 |
|-----|------|
| `imgapi.cn` | 壁纸生成（二次元、风景、妹子、随机） |

### 切换 AI 模式

| 命令 | 模式 | 说明 |
|------|------|------|
| `- 读图` | Pixmap | 默认模型 + 多模态（支持图片理解） |
| `- 默认4` | Net | 使用候补模型（deepseek-v3） |
| `- 默认3.5` | Normal | 使用候补模型（deepseek-v3） |

---

## 功能命令

命令前缀默认为 `- `（可在 config.json 中修改 `reminder`）

### 基础命令

| 命令 | 功能 |
|------|------|
| `ping` | 测试机器人是否在线 |
| `- 帮助` | 查看帮助信息 |
| `- 关于` | 查看机器人信息 |

### AI 对话

| 命令 | 功能 |
|------|------|
| `- <问题>` | AI 对话（使用默认模型 gemini-3-flash-preview） |
| `@小喵 <问题>` | AI 对话（@机器人方式） |
| `- 读图` | 切换到图片识别模式（默认） |
| `- 默认4` | 切换到候补模型模式 |
| `- 默认3.5` | 切换到候补模型模式 |

### 图片功能

| 命令 | 功能 |
|------|------|
| `- 生图` | 随机二次元壁纸（默认） |
| `- 生图 二次元` | 二次元/动漫壁纸 |
| `- 生图 风景` | 自然风景壁纸 |
| `- 生图 妹子` | 真人美女壁纸 |
| `- 生图 随机` | 随机类型壁纸 |
| `- 大头照 @用户` | 获取用户头像 |

### 角色切换

| 命令 | 功能 |
|------|------|
| `- 当我女朋友` | 切换到女朋友模式 |
| `- 做我姐姐吧` | 切换到姐姐模式 |
| `- 做我mm吧` | 切换到妈妈模式 |

### 群管理（需要管理员权限）

| 命令 | 功能 |
|------|------|
| `- 禁言 @用户 秒数` | 禁言用户 |
| `- 解禁 @用户` | 解除禁言 |
| `- 踢出 @用户` | 踢出用户 |
| `撤回`（引用消息） | 撤回消息 |

### 系统命令（需要管理员权限）

| 命令 | 功能 |
|------|------|
| `- 重启` | 重启机器人 |
| `- 感知` | 查看系统状态 |
| `- 注销` | 清空对话上下文 |
| `- 核验 <QQ号>` | 查询用户信息 |
| `- runcommand <命令>` | 执行系统命令 |

### 其他功能

| 命令 | 功能 |
|------|------|
| `- 名言`（引用消息） | 生成名言图片 |
| `- 修改 HH:MM 内容` | 设置定时消息 |
| `- enc解密 <密文>` | Base64 解密 |

---

## 文件结构

```
XiaoMiao_QQ_bot/
├── main.py                 # 主程序入口，包含所有消息处理逻辑
├── config.json             # 机器人配置文件
├── prerequisites.py        # AI 人设提示词配置
├── start.bat               # Windows 启动脚本
├── requirements.txt        # Python 依赖列表
├── GoogleAI.py             # Gemini AI 封装（OpenAI 兼容层）
├── SearchOnline.py         # OpenAI 对话封装
├── Quote.py                # 名言图片生成模块
│
├── runtime/                # 运行配置文件目录
│   ├── Super_User.ini      # 超级用户列表（每行一个QQ号）
│   ├── Manage_User.ini     # 管理用户列表
│   ├── sisters.ini         # 姐姐模式用户列表
│   ├── jhq.ini             # 妈妈模式用户列表
│   ├── programmers.ini     # 高级程序员模式用户列表
│   ├── blacklist.sr        # 定时消息黑名单
│   └── timing_message.ini  # 定时消息配置
│
├── assets/                 # 资源文件目录
│   ├── *.ttf               # 字体文件（名言图片用）
│   ├── dict.txt            # 词典文件
│   └── quote/mask.png      # 名言图片遮罩
├── temps/                  # 临时文件目录
│
└── NapCat.Shell.Windows.OneKey/  # NapCat QQ 协议框架
```

### 核心文件说明

| 文件 | 作用 |
|------|------|
| `main.py` | 主程序，处理所有 QQ 消息事件、命令解析、AI 对话、图片生成等 |
| `GoogleAI.py` | 封装 Gemini API，通过 OpenAI 兼容接口调用，支持多模态（图片理解） |
| `SearchOnline.py` | 封装 OpenAI API，用于候补模型调用 |
| `prerequisites.py` | 定义角色系统提示词（女朋友/姐姐/妈妈/高级程序员模式） |
| `Quote.py` | 生成名言图片，将消息渲染为带头像的图片 |
| `config.json` | 存储 API Key、模型配置、连接参数等 |

---

## 生图功能详解

### 支持的生图类型

使用 `imgapi.cn` API（国内可访问），返回 1920x1080 高清壁纸。

| 命令 | 类型 | 说明 |
|------|------|------|
| `- 生图` | 二次元 | 默认，动漫壁纸 |
| `- 生图 二次元` | 二次元 | 动漫/ACG 壁纸 |
| `- 生图 风景` | 风景 | 自然风景壁纸 |
| `- 生图 妹子` | 妹子 | 真人美女壁纸 |
| `- 生图 随机` | 随机 | 随机类型壁纸 |

### 用户头像

| 命令 | 说明 |
|------|------|
| `- 大头照 @用户` | 获取指定用户的 QQ 头像（640x640） |

### 生图冷却时间

- 每个用户 18 秒冷却时间
- 管理员（Super_User/ROOT_User/Manage_User）无冷却限制

---

## 图片识别功能

### 支持的图片类型

| 类型 | 说明 | 支持状态 |
|------|------|---------|
| 普通图片 | QQ 发送的图片 | 支持 |
| 商城表情包 | QQ 商城购买的表情 | 支持 |
| 系统表情 | QQ 内置表情 | 不支持（无图片数据） |

### 使用方式

1. 发送图片/表情包 + 问题：`- 这是什么`
2. 引用包含图片的消息 + 问题：`- 描述一下这张图`

### 技术实现

- 使用 Gemini 多模态 API（gemini-3-flash-preview）
- 图片通过 base64 编码发送给 API
- 支持 JPEG、PNG、GIF 格式

---

## NapCat 配置

NapCat 配置文件位置：
```
NapCat.Shell.Windows.OneKey/NapCat.44498.Shell/versions/9.9.26-44498/resources/app/napcat/config/onebot11_<QQ号>.json
```

WebSocket 服务器配置示例：
```json
{
  "network": {
    "websocketServers": [
      {
        "name": "Bot",
        "enable": true,
        "host": "127.0.0.1",
        "port": 5004,
        "token": "",
        "heartInterval": 5000
      }
    ]
  }
}
```

---

## 常见问题

### 1. 机器人无响应

- 检查 NapCat 是否显示 `WebSocket服务: 127.0.0.1:5004`
- 检查 Python 程序是否正常运行
- 确认 `config.json` 中的端口与 NapCat 配置一致

如果控制台先输出 bridge 地址后报 `WebSocketConnectionClosedException`，说明本地 bridge 已启动过，但 `Listener.run()` 连接 OneBot 失败。修复 NapCat 后重新运行即可。

### 2. API 调用失败

- 检查 API Key 是否正确
- 检查 API 地址是否可访问
- 查看控制台错误信息

### 3. nanobot Agent 调用失败

- 检查 `nanobot serve --config F:\xiaomiaoVirtual\nanobot\.nanobot\config.json` 是否正在运行
- 检查 `http://127.0.0.1:8900/health`
- 检查 `Others.nanobot_agent.base_url` 是否指向 `http://127.0.0.1:8900/v1/chat/completions`
- 如果返回 HTTP 502，查看错误内容；当前实现会显式暴露 nanobot HTTP 错误、空回复和超时

### 4. 权限不足

- 将 QQ 号添加到 `runtime/Super_User.ini` 或 `runtime/Manage_User.ini`
- 确保机器人在群内有管理员权限（群管理功能）

---

## 私聊功能

机器人支持私聊，可用命令：

| 命令 | 功能 |
|------|------|
| `ping` | 测试在线 |
| `- 帮助` | 查看帮助 |
| `- 关于` | 机器人信息 |
| `- <问题>` | AI 对话 |
| `- 生图` | 生成二次元壁纸 |
| `- 生图 风景` | 生成风景壁纸 |
| `- 大头照` | 获取头像 |
| `- 当我女朋友` | 切换角色 |
| `- 做我姐姐吧` | 切换角色 |
| `- 做我mm吧` | 切换角色 |
| `- 程序员` | 切换到高级程序员模式 |

---

## 协作与问题反馈

### 解压后协作

`deploy/xiaomiaoVirtual.zip` 会包含重新初始化后的 `.git/` 目录。协作者解压后可以直接查看 Git 状态：

```bash
unzip xiaomiaoVirtual.zip -d xiaomiaoVirtual
cd xiaomiaoVirtual
git status
```

建议每个改动单独创建分支：

```bash
git switch -c feature/你的功能名
```

修改完成后提交：

```bash
git add .
git commit -m "说明你的修改"
```

如果没有远程仓库，可以把变更打成 bundle 发回：

```bash
git bundle create my-change.bundle main..feature/你的功能名
```

如果使用 GitHub / Gitee，协作者可以推送分支后提交 Pull Request。

### 反馈问题时请提供

```text
1. 运行系统：Windows / Linux，以及版本
2. Python 环境：conda 环境名、Python 版本
3. 启动方式：start.bat / 手动启动 / systemd
4. 触发命令：例如 - 程序员
5. 期望结果：你原本希望发生什么
6. 实际结果：实际发生了什么
7. 关键日志：NapCat 窗口日志和 python main.py 报错
8. 配置片段：隐藏 API Key 后的 config.json 相关字段
```

---

## 开发信息

- 框架：HypeR Bot + NapCat
- 协议：OneBot 11
- AI：Gemini / DeepSeek（支持 OpenAI 兼容接口）

---

Made by SR Studio | 2019-2025
