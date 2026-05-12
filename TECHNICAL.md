# xiaomiaoVirtual 技术文档

## 1. 项目定位

`xiaomiaoVirtual` 是一个 QQ 机器人与 Vtuber 桌面角色联动项目。当前由两个子系统组成：

1. `xiaomiao`：Python QQ 机器人，负责 QQ 消息、命令、人设、模型调用、图片能力、群管理和本地桥接。
2. `AuBot`：Project AIRI 风格的 Electron/Vue Vtuber 工程，负责桌面角色、Live2D/VRM、字幕、TTS 和口型同步。

当前项目已经打通最小闭环：QQ 消息进入机器人，AI 回复被桌面端读取，并驱动 Vtuber 的字幕、语音和 Live2D 口型。

## 2. 总体架构

```text
[QQ 用户]
    ↓
[NapCat / OneBot]
    ↓ WebSocket :5004
[xiaomiao Python Bot]
    ↓
[OpenAI-compatible LLM]
    ↓
[desktop_bridge.py HTTP :5519]
    ↓
[AuBot stage-tamagotchi]
    ↓
[字幕 / 聊天历史 / TTS / Live2D LipSync]
```

## 3. xiaomiao 子系统

`xiaomiao` 是 QQ 机器人主体，核心入口是 `xiaomiao/main.py`。

主要职责：

- 连接 NapCat 的 OneBot WebSocket。
- 监听群消息、入群、邀请等 QQ 事件。
- 解析命令前缀和 `@机器人` 消息。
- 根据用户角色选择人设提示词。
- 调用 OpenAI 兼容模型接口生成回复。
- 支持图片识别、图片获取、名言图片、系统状态和群管理。
- 启动本地桌面桥接服务供 AuBot 消费。

关键文件：

```text
xiaomiao/
├── main.py              # QQ 机器人主入口
├── desktop_bridge.py    # 本地 OpenAI 兼容桥接服务
├── GoogleAI.py          # OpenAI SDK 兼容模型封装
├── SearchOnline.py      # 备用 OpenAI 对话封装
├── prerequisites.py     # 人设和角色选择
├── Quote.py             # 名言图片生成
├── config.json          # 主配置
├── requirements.txt     # Python 依赖
└── runtime/             # 权限、角色、定时消息和黑名单配置
```

## 4. AuBot 子系统

`AuBot` 是多端 Vtuber/AIRI monorepo。当前与小喵联动的主要入口是 `apps/stage-tamagotchi`。

主要职责：

- 启动 Electron 桌面角色窗口。
- 渲染 Live2D、VRM 或 Godot stage。
- 管理聊天会话、字幕、TTS 和语音输入。
- 读取 `xiaomiao` 本地桥接状态。
- 把 QQ 机器人回复表现为桌面角色说话、字幕和口型同步。

关键目录：

```text
AuBot/
├── apps/stage-tamagotchi/         # Electron 桌面 Vtuber 入口
├── packages/stage-ui/             # 舞台、TTS、聊天、设置等核心 UI/业务
├── packages/stage-ui-live2d/      # Live2D 组件、状态和工具
├── packages/stage-ui-three/       # VRM / Three.js 渲染
├── packages/model-driver-lipsync/ # 口型同步驱动
├── packages/pipelines-audio/      # 音频流水线
└── services/                      # 其他机器人和平台适配
```

## 5. 运行链路

### 5.1 QQ 消息进入机器人

`xiaomiao/config.json` 中的 `Connection` 配置指向本机 NapCat：

```json
{
  "mode": "FWS",
  "host": "127.0.0.1",
  "port": 5004,
  "listener_host": "127.0.0.1",
  "listener_port": 5003
}
```

群消息进入后的主流程：

1. 读取用户消息文本。
2. 获取用户昵称。
3. 选择用户对应人设。
4. 判断是否为命令、快捷命令或 `@机器人` 消息。
5. 根据命令分支执行具体能力。
6. 如果是 AI 对话，调用模型接口生成回复。
7. 将回复发送回 QQ。
8. 调用 `publish_desktop_state()` 同步到桌面桥接状态。

### 5.2 模型调用

模型调用分为两个封装：

- `GoogleAI.py`：OpenAI SDK 兼容封装，支持自定义 `base_url`。
- `SearchOnline.py`：备用 OpenAI 风格对话封装。

`GoogleAI.Context` 维护用户对话历史，并通过 `client.chat.completions.create()` 调用模型。项目虽然保留 Gemini 命名，但实际可接入 DeepSeek、OpenAI 官方、Gemini OpenAI 兼容接口或第三方中转。

## 6. 桌面桥接协议

`xiaomiao/desktop_bridge.py` 默认监听：

```text
http://127.0.0.1:5519
```

提供三个接口：

```text
GET  /v1/models
GET  /v1/xiaomiao/state?user_id=<qq>
POST /v1/chat/completions
```

接口作用：

- `/v1/models`：返回当前桥接模型名称。
- `/v1/xiaomiao/state`：返回某个用户最近一次机器人回复。
- `/v1/chat/completions`：OpenAI 兼容聊天接口，让 AuBot 可主动向小喵发送文本并获得回复。

状态保存方式目前是内存全局字典：

```text
LATEST_STATE_BY_USER[user_id] = reply_text + timestamp
```

AuBot 侧的小喵桥接模块：

- `xiaomiao-bridge.ts`：读取 `/v1/xiaomiao/state`。
- `xiaomiao-bridge-chat.ts`：把桥接回复写入聊天历史。
- `xiaomiao-bridge-reaction.ts`：把桥接回复分发到字幕、聊天历史、语音和口型同步。

`stage-tamagotchi` 主舞台挂载后会初始化聊天同步、确保桥接语音 provider 可用，并每 1.5 秒轮询一次小喵桥接状态。

## 7. Vtuber 表现链路

桥接回复进入 AuBot 后，会被同步到三个表现面：

```text
bridge reply
    ├── postCaption() → 字幕窗口显示
    ├── appendBridgeAssistantReply() → 聊天历史追加 assistant 消息
    └── characterStore.emitTextOutput()
            ↓
        Stage.vue speechPipeline
            ↓
        TTS 生成音频
            ↓
        AudioContext 播放
            ↓
        Live2D LipSync 驱动嘴型
```

`Stage.vue` 是 Vtuber 表现核心：

- `speechPipeline` 负责文本到语音。
- `playbackManager` 负责音频播放队列。
- `setupLipSync()` 初始化口型同步。
- `mouthOpenSize` 传入 `Live2DScene` 驱动嘴部开合。

当前代码已经处理桥接语音绕过普通聊天 orchestrator 的问题，在音频播放边界统一初始化 analyser 和 lip sync，避免“有声音但嘴不动”。

## 8. 配置与端口

主配置文件：

```text
xiaomiao/config.json
```

关键配置：

- `Connection.host` / `Connection.port`：NapCat OneBot 地址。
- `Others.default_model`：默认模型。
- `Others.fallback_model`：主模型失败后的备用模型。
- `Others.gemini_base_url` / `Others.openai_base_url`：OpenAI 兼容 API 地址。
- `Others.bot_name`：机器人中文名。
- `Others.ROOT_User`：超级用户。
- `Others.personas`：人设提示词。

默认端口：

```text
5004  NapCat OneBot WebSocket
5003  Hyper listener port
5519  xiaomiao desktop bridge
6099  NapCat WebUI，可选
3000  NapCat HTTP API，可选
```

AuBot 常用脚本：

```text
pnpm dev:web          # Web 版
pnpm dev:tamagotchi   # Electron 桌面版
pnpm dev:docs         # 文档站
pnpm build:tamagotchi # 构建桌面版
pnpm typecheck        # 类型检查
pnpm lint             # Lint 检查
```

## 9. 工程风险

### 9.1 明文密钥

`xiaomiao/config.json` 当前承担模型配置。真实 API Key 不应保存在可提交源码配置中，应迁移到 `.env`、本机私有配置或系统环境变量。

### 9.2 主程序职责过重

`xiaomiao/main.py` 同时负责事件监听、命令解析、权限判断、模型调用、图片处理、桥接发布和系统命令。后续建议拆为 `commands/`、`services/llm.py`、`services/bridge.py`、`services/roles.py`、`services/images.py` 和 `permissions.py`。

### 9.3 桥接配置硬编码

AuBot 中桥接地址和绑定用户仍是原型硬编码：`http://127.0.0.1:5519` 和 `BOUND_XIAOMIAO_USER_ID`。这会限制多用户、多账号、多机器人实例场景。

### 9.4 桥接协议缺少鉴权

桥接服务默认只监听 `127.0.0.1`，风险较低，但本机任意进程仍可访问。如果后续开放到局域网或跨设备，应增加 token、签名或一次性配对机制。

### 9.5 系统命令能力风险

`runcommand` 类能力天然高危。当前采用危险命令黑名单，但黑名单无法覆盖所有变体。后续应改为白名单命令或移除远程系统命令执行能力。

## 10. 测试现状

已有测试集中在桥接链路：

```text
xiaomiao/test_desktop_bridge.py
AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge.test.ts
AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-chat.test.ts
AuBot/apps/stage-tamagotchi/src/renderer/pages/xiaomiao-bridge-reaction.test.ts
```

覆盖范围包括 OpenAI 兼容路由、CORS preflight、读取桥接状态、桥接回复去重、字幕/历史/语音同步，以及 Kokoro 中文语音 provider 自动选择。

## 11. 演进路线

1. 配置安全：移除源码中的真实 API Key，补充 `.env.example` 或本机配置模板。
2. 桥接配置：把桥接端口、绑定用户、模型名称变成可配置项。
3. 桥接协议：增加消息 ID、健康检查、用户绑定握手和最小鉴权机制。
4. Python 拆分：从 `main.py` 中拆出命令、权限、模型、桥接、图片和角色服务。
5. Vtuber 增强：支持 QQ 用户到桌面会话映射，并根据回复情绪驱动 Live2D 表情。

## 12. 当前结论

项目已经完成 QQ 机器人与 Vtuber 桌面角色的最小闭环。当前最大价值在于桥接链路已经跑通。下一步最重要的不是继续堆功能，而是把配置、桥接协议和 Python Bot 模块边界工程化，避免原型代码继续膨胀。
