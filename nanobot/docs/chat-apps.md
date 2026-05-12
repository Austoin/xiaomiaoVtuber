# 聊天应用

把 nanobot 连接到你常用的聊天平台。若要构建自己的通道，请参考[通道插件指南](./channel-plugin-guide.md)。

| 通道 | 需要准备 |
|---------|---------------|
| **Telegram** | 从 @BotFather 获取 Bot token |
| **Discord** | Bot token + Message Content intent |
| **WhatsApp** | 扫描二维码（`nanobot channels login whatsapp`） |
| **WeChat / Weixin** | 扫描二维码（`nanobot channels login weixin`） |
| **Feishu** | App ID + App Secret |
| **DingTalk** | App Key + App Secret |
| **Slack** | Bot token + App-Level token |
| **Matrix** | Homeserver URL + Access token 或密码 |
| **Email** | IMAP/SMTP 凭据 |
| **QQ** | App ID + App Secret |
| **Wecom** | Bot ID + Bot Secret |
| **Microsoft Teams** | App ID + App Password + 公开 HTTPS 端点 |
| **Mochat** | Claw token（支持自动配置） |

<details>
<summary><b>Telegram</b>（推荐）</summary>

**1. 创建 Bot**

- 打开 Telegram，搜索 `@BotFather`。
- 发送 `/newbot`，按提示完成创建。
- 复制 token。

**2. 配置**

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

可在 Telegram 设置中找到 **User ID**，通常显示为 `@yourUserId`。复制到配置时不要包含 `@`。

**3. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Mochat（Claw IM）</b></summary>

默认使用 **Socket.IO WebSocket**，并带 HTTP polling fallback。

**1. 让 nanobot 自动配置 Mochat**

把下面消息发送给 nanobot，并将 `xxx@xxx` 替换为你的真实邮箱：

```text
Read https://raw.githubusercontent.com/HKUDS/MoChat/refs/heads/main/skills/nanobot/skill.md and register on MoChat. My Email account is xxx@xxx Bind me as your owner and DM me on MoChat.
```

nanobot 会自动注册、配置 `~/.nanobot/config.json` 并连接 Mochat。

**2. 重启 gateway**

```bash
nanobot gateway
```

如果希望手动配置，请在 `~/.nanobot/config.json` 中添加：

```json
{
  "channels": {
    "mochat": {
      "enabled": true,
      "base_url": "https://mochat.io",
      "socket_url": "https://mochat.io",
      "socket_path": "/socket.io",
      "claw_token": "claw_xxx",
      "agent_user_id": "6982abcdef",
      "sessions": ["*"],
      "panels": ["*"],
      "reply_delay_mode": "non-mention",
      "reply_delay_ms": 120000
    }
  }
}
```

请保密 `claw_token`。它只应通过 `X-Claw-Token` header 发送到你的 Mochat API 端点。

</details>

<details>
<summary><b>Discord</b></summary>

**1. 创建 Bot**

- 打开 https://discord.com/developers/applications。
- 创建 application → Bot → Add Bot。
- 复制 Bot token。

**2. 启用 intents**

- 在 Bot 设置中启用 **MESSAGE CONTENT INTENT**。
- 如需基于成员数据使用允许列表，可选启用 **SERVER MEMBERS INTENT**。

**3. 获取 User ID**

- Discord Settings → Advanced → 启用 **Developer Mode**。
- 右键头像 → **Copy User ID**。

**4. 配置**

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"],
      "allowChannels": [],
      "groupPolicy": "mention",
      "streaming": true
    }
  }
}
```

`groupPolicy` 控制群组频道中的回复方式：`"mention"` 表示仅在被 @ 时回复，`"open"` 表示回复所有消息。DM 中只要发送者在 `allowFrom` 中就会回复。

`allowChannels` 可限制 Bot 只在指定 Discord channel ID 中响应；空列表表示所有可见频道。Discord thread 会继承允许的父频道；Forum channel 允许父频道后，其所有帖子/thread 也允许。

**5. 邀请 Bot**

- OAuth2 → URL Generator。
- Scopes：`bot`。
- Bot Permissions：`Send Messages`、`Read Message History`。
- 打开生成的邀请 URL，把 Bot 加入服务器。

**6. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Matrix（Element）</b></summary>

先安装 Matrix 依赖：

```bash
pip install nanobot-ai[matrix]
```

> [!NOTE]
> Matrix 不支持 Windows。`matrix-nio[e2e]` 依赖 `python-olm`，它没有预编译 Windows wheel，并会在 `sys_platform == 'win32'` 时被 `matrix` extra 跳过。Windows 上上述命令仍可能成功，但不会安装 `matrix-nio`，启用 Matrix 通道会在启动时失败。请使用 macOS、Linux 或 WSL2。

**1. 创建或选择 Matrix 账号**

- 在你的 homeserver（例如 `matrix.org`）创建或复用账号。
- 确认可以通过 Element 登录。

**2. 获取凭据**

需要 `userId`（例如 `@nanobot:matrix.org`）和 `password`。`accessToken` 和 `deviceId` 仍因旧版兼容而支持，但为了可靠加密，推荐使用密码登录。提供 `password` 时，`accessToken` 和 `deviceId` 会被忽略。

**3. 配置**

```json
{
  "channels": {
    "matrix": {
      "enabled": true,
      "homeserver": "https://matrix.org",
      "userId": "@nanobot:matrix.org",
      "password": "mypasswordhere",
      "e2eeEnabled": true,
      "allowFrom": ["@your_user:matrix.org"],
      "groupPolicy": "open",
      "groupAllowFrom": [],
      "allowRoomMentions": false,
      "maxMediaBytes": 20971520
    }
  }
}
```

请保持持久 `matrix-store`，否则重启后会丢失加密会话状态。

| 选项 | 说明 |
|--------|-------------|
| `allowFrom` | 允许交互的 User ID。空列表拒绝所有；`["*"]` 允许所有人。 |
| `groupPolicy` | `open`（默认）、`mention` 或 `allowlist`。 |
| `groupAllowFrom` | 房间允许列表，仅在 `allowlist` 策略下使用。 |
| `allowRoomMentions` | mention 模式下接受 `@room` 提及。 |
| `e2eeEnabled` | E2EE 支持，默认 `true`。设为 `false` 可只使用明文。 |
| `maxMediaBytes` | 最大附件大小，默认 `20MB`。设为 `0` 可阻止所有媒体。 |

**4. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>WhatsApp</b></summary>

需要 **Node.js ≥18**。

**1. 关联设备**

```bash
nanobot channels login whatsapp
# 使用 WhatsApp → Settings → Linked Devices 扫描二维码
```

**2. 配置**

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

**3. 运行**（两个终端）

```bash
# Terminal 1
nanobot channels login whatsapp

# Terminal 2
nanobot gateway
```

WhatsApp bridge 更新不会自动应用到已有安装。升级 nanobot 后，请重建本地 bridge：

```bash
rm -rf ~/.nanobot/bridge && nanobot channels login whatsapp
```

</details>

<details>
<summary><b>Feishu</b></summary>

使用 **WebSocket** 长连接，无需公网 IP。

**1. 创建飞书 Bot**

- 访问[飞书开放平台](https://open.feishu.cn/app)。
- 创建新应用 → 启用 **Bot** 能力。
- 权限：添加 `im:message`（发送消息）和 `im:message.p2p_msg:readonly`（接收消息）。
- 如果启用默认流式回复，还需添加 **`cardkit:card:write`**（控制台里常显示为创建和更新卡片）。如果无法添加该权限，可在 `channels.feishu` 下设置 `"streaming": false`。
- 事件：添加 `im.message.receive_v1`，并选择 **Long Connection** 模式。
- 从 “Credentials & Basic Info” 获取 **App ID** 和 **App Secret**。
- 发布应用。

**2. 配置**

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx",
      "encryptKey": "",
      "verificationToken": "",
      "allowFrom": ["ou_YOUR_OPEN_ID"],
      "groupPolicy": "mention",
      "reactEmoji": "OnIt",
      "doneEmoji": "DONE",
      "toolHintPrefix": "🔧",
      "streaming": true,
      "domain": "feishu"
    }
  }
}
```

`streaming` 默认 `true`。如果应用没有 **`cardkit:card:write`**，请设为 `false`。`encryptKey` 和 `verificationToken` 在 Long Connection 模式下可选。

`allowFrom` 中添加你的 open_id，可在你给 Bot 发消息后的 nanobot 日志中找到；`["*"]` 允许所有用户。`groupPolicy` 可为 `"mention"` 或 `"open"`。`domain` 在中国大陆为 `"feishu"`，国际 Lark 为 `"lark"`。

**3. 运行**

```bash
nanobot gateway
```

> [!TIP]
> 飞书使用 WebSocket 接收消息，不需要 webhook 或公网 IP。

</details>

<details>
<summary><b>QQ（QQ 单聊）</b></summary>

使用 **botpy SDK** 和 WebSocket，无需公网 IP。目前仅支持**私聊消息**。

**1. 注册并创建 Bot**

- 访问 [QQ 开放平台](https://q.qq.com)，注册为个人或企业开发者。
- 创建新的 Bot 应用。
- 打开 **开发设置**，复制 **AppID** 和 **AppSecret**。

**2. 设置测试沙箱**

- 在 Bot 管理控制台中找到 **沙箱配置**。
- 在 **在消息列表配置** 下点击 **添加成员**，添加你的 QQ 号。
- 添加后，用手机 QQ 扫描 Bot 二维码，打开 Bot 资料页并点击“发消息”。

**3. 配置**

```json
{
  "channels": {
    "qq": {
      "enabled": true,
      "appId": "YOUR_APP_ID",
      "secret": "YOUR_APP_SECRET",
      "allowFrom": ["YOUR_OPENID"],
      "msgFormat": "plain"
    }
  }
}
```

`allowFrom` 中添加你的 openid，可在日志中找到；`["*"]` 表示公开访问。`msgFormat` 可选，`"plain"` 兼容性最好，`"markdown"` 适合新客户端富文本。

生产环境需要在 Bot 控制台提交审核并发布，完整流程见 [QQ Bot Docs](https://bot.q.qq.com/wiki/)。

**4. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>DingTalk（钉钉）</b></summary>

使用 **Stream Mode**，无需公网 IP。

**1. 创建钉钉 Bot**

- 访问[钉钉开放平台](https://open-dev.dingtalk.com/)。
- 创建新应用，添加 **Robot** 能力。
- 开启 **Stream Mode**。
- 添加发送消息所需权限。
- 从凭据中获取 **AppKey**（Client ID）和 **AppSecret**（Client Secret）。
- 发布应用。

**2. 配置**

```json
{
  "channels": {
    "dingtalk": {
      "enabled": true,
      "clientId": "YOUR_APP_KEY",
      "clientSecret": "YOUR_APP_SECRET",
      "allowFrom": ["YOUR_STAFF_ID"]
    }
  }
}
```

`allowFrom` 中添加你的 staff ID；`["*"]` 允许所有用户。

**3. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Slack</b></summary>

使用 **Socket Mode**，无需公开 URL。

**1. 创建 Slack App**

- 打开 [Slack API](https://api.slack.com/apps) → **Create New App** → “From scratch”。
- 填写名称并选择 workspace。

**2. 配置 App**

- **Socket Mode**：开启后生成带 `connections:write` scope 的 **App-Level Token**，复制 `xapp-...`。
- **OAuth & Permissions**：添加 bot scopes：`chat:write`、`reactions:write`、`app_mentions:read`、`files:read`、`files:write`、`channels:history`、`groups:history`、`im:history`、`mpim:history`。
- **Event Subscriptions**：开启并订阅 `message.im`、`message.channels`、`app_mention`。
- **App Home**：启用 **Messages Tab**，并允许用户从 messages tab 发送 Slash commands 和消息。
- **Install App**：安装到 workspace，复制 **Bot Token**（`xoxb-...`）。

`files:read` 用于读取用户发送的文件；`files:write` 用于发送图片、视频和其他文件。后续添加 scope 后，需要重新安装 Slack app 并重启 nanobot。

**3. 配置 nanobot**

```json
{
  "channels": {
    "slack": {
      "enabled": true,
      "botToken": "xoxb-...",
      "appToken": "xapp-...",
      "allowFrom": ["YOUR_SLACK_USER_ID"],
      "groupPolicy": "mention"
    }
  }
}
```

**4. 运行**

```bash
nanobot gateway
```

你可以直接 DM Bot，或在频道中 @ 它。

`groupPolicy` 可为 `"mention"`、`"open"` 或 `"allowlist"`。DM 默认开放，如需禁用 DM，设置 `"dm": {"enabled": false}`。

</details>

<details>
<summary><b>Email</b></summary>

给 nanobot 一个专用邮箱账号。它通过 **IMAP** 拉取新邮件，并通过 **SMTP** 回复，类似个人邮件助理。

**1. 获取凭据（以 Gmail 为例）**

- 创建专用 Gmail 账号，例如 `my-nanobot@gmail.com`。
- 启用两步验证，创建 [App Password](https://myaccount.google.com/apppasswords)。
- IMAP 和 SMTP 都使用该 app password。

**2. 配置**

```json
{
  "channels": {
    "email": {
      "enabled": true,
      "consentGranted": true,
      "imapHost": "imap.gmail.com",
      "imapPort": 993,
      "imapUsername": "my-nanobot@gmail.com",
      "imapPassword": "your-app-password",
      "smtpHost": "smtp.gmail.com",
      "smtpPort": 587,
      "smtpUsername": "my-nanobot@gmail.com",
      "smtpPassword": "your-app-password",
      "fromAddress": "my-nanobot@gmail.com",
      "allowFrom": ["your-real-email@gmail.com"],
      "allowedAttachmentTypes": ["application/pdf", "image/*"]
    }
  }
}
```

`consentGranted` 必须为 `true` 才允许访问邮箱；这是安全开关。`allowFrom` 中添加你的邮箱，`["*"]` 接受任何发件人。`autoReplyEnabled: false` 可只读/分析邮件而不自动回复。`allowedAttachmentTypes` 控制保存哪些附件 MIME 类型，默认空列表表示禁用附件保存。

**3. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>WeChat（微信 / Weixin）</b></summary>

通过 ilinkai 个人微信 API 使用 **HTTP long-poll** 和二维码登录，不需要本地微信桌面客户端。

**1. 安装微信支持**

```bash
pip install "nanobot-ai[weixin]"
```

**2. 配置**

```json
{
  "channels": {
    "weixin": {
      "enabled": true,
      "allowFrom": ["YOUR_WECHAT_USER_ID"]
    }
  }
}
```

`allowFrom` 中添加你在日志中看到的微信 sender ID；`["*"]` 允许所有用户。`token` 可选，省略时可交互式登录并由 nanobot 保存 token。`routeTag`、`stateDir`、`pollTimeout` 都是可选项。

**3. 登录**

```bash
nanobot channels login weixin
```

如需重新认证并忽略已保存 token：

```bash
nanobot channels login weixin --force
```

**4. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Wecom（企业微信）</b></summary>

这里使用 [wecom-aibot-sdk-python](https://github.com/chengyongru/wecom_aibot_sdk)，即官方 [@wecom/aibot-node-sdk](https://www.npmjs.com/package/@wecom/aibot-node-sdk) 的社区 Python 版本。它使用 **WebSocket** 长连接，无需公网 IP。

**1. 安装可选依赖**

```bash
pip install nanobot-ai[wecom]
```

**2. 创建企业微信 AI Bot**

进入企业微信管理后台 → 智能机器人 → 创建机器人 → 选择带长连接的 **API mode**，复制 Bot ID 和 Secret。

**3. 配置**

```json
{
  "channels": {
    "wecom": {
      "enabled": true,
      "botId": "your_bot_id",
      "secret": "your_bot_secret",
      "allowFrom": ["your_id"]
    }
  }
}
```

**4. 运行**

```bash
nanobot gateway
```

</details>

<details>
<summary><b>Microsoft Teams</b>（MVP，仅 DM）</summary>

支持直接消息文本收发、租户感知 OAuth 和 conversation reference 持久化。它使用公开 HTTPS webhook，而不是 WebSocket；你需要 tunnel 或反向代理。

**1. 安装可选依赖**

```bash
pip install nanobot-ai[msteams]
```

**2. 创建 Teams / Azure Bot app registration**

创建或复用 Microsoft Teams / Azure Bot app registration。将 Bot messaging endpoint 设置为以 `/api/messages` 结尾的公开 HTTPS URL。

**3. 配置**

```json
{
  "channels": {
    "msteams": {
      "enabled": true,
      "appId": "YOUR_APP_ID",
      "appPassword": "YOUR_APP_SECRET",
      "tenantId": "YOUR_TENANT_ID",
      "host": "0.0.0.0",
      "port": 3978,
      "path": "/api/messages",
      "allowFrom": ["*"],
      "replyInThread": true,
      "mentionOnlyResponse": "Hi — what can I help with?",
      "validateInboundAuth": true,
      "refTtlDays": 30,
      "pruneWebChatRefs": true,
      "pruneNonPersonalRefs": true,
      "refTouchIntervalS": 300
    }
  }
}
```

`validateInboundAuth: true` 会启用入站 Bot Framework bearer-token 校验，这是公开部署的安全默认值。只有在本地开发或严格受控测试中才设为 `false`。

`replyInThread`、`mentionOnlyResponse`、`refTtlDays`、`pruneWebChatRefs`、`pruneNonPersonalRefs` 和 `refTouchIntervalS` 控制 Teams 回复线程和 conversation reference 清理行为。

**4. 运行**

```bash
nanobot gateway
```

</details>
