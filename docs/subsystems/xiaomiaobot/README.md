# xiaomiaobot 表现层说明

`xiaomiaobot` 是 `xiaomiaoVirtual` 的 Web、桌面、移动端 Vtuber 表现层，负责把统一 Agent 回复呈现为网页聊天、桌面字幕、TTS、Live2D/VRM 和口型同步。该目录来自 AIRI monorepo，历史文档中也会出现 `AuBot`；内部包名、工作区作用域和部分目录仍保留 `@proj-airi/*` 兼容标识。

## 📚 详细文档

xiaomiaobot 的完整文档请参考：

- 🤖 [AGENTS 开发指南](../../xiaomiaobot/AGENTS.md) - 详细技术栈、架构和开发实践 (推荐)
- 📖 [VitePress 文档站](../../xiaomiaobot/docs/) - 多语言文档
  - [简体中文文档](../../xiaomiaobot/docs/content/zh-Hans/docs/)
  - [英文文档](../../xiaomiaobot/docs/content/en/docs/)
- 🎨 [UI 组件参考](../../xiaomiaobot/docs/ai/context/ui-components.md) - 组件 API
- 🏗️ [服务器架构](../../xiaomiaobot/apps/server/docs/ai-context/) - 8个详细架构文档
- 📁 [目录结构索引](struct.md) - 完整目录树

## 目录

- [快速开始](#快速开始)
- [主要模块](#主要模块)
- [服务和插件清单](#服务和插件清单)
- [启动方式](#启动方式)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [项目结构](#项目结构)
- [全结构索引](#全结构索引)
- [Git 仓库说明](#git-仓库说明)

---

## 快速开始

### 环境要求

- Node.js：建议使用当前 LTS 版本
- pnpm：项目声明版本为 `pnpm@10.33.0`
- Git：用于版本管理与远端同步

### 安装步骤

1. **启用 pnpm**

   ```powershell
   corepack enable
   corepack prepare pnpm@10.33.0 --activate
   pnpm -v
   ```

2. **安装依赖**

   ```powershell
   pnpm install
   ```

3. **根据需要启动对应端**

   - Web 应用：`pnpm dev:web`
   - Electron 桌面版：`pnpm dev:tamagotchi`
   - 文档站：`pnpm dev:docs`
   - 服务端 API：`pnpm -F @proj-airi/server dev`

---

## 主要模块

### `apps/stage-web`

Web 版应用，适合在浏览器中运行和调试，用于承载 `xiaomiaoVirtual` 的前端交互能力。当前 `stage-web` 的文本输入、移动端输入和页面级录音转文字入口都会发送到 `xiaomiao` 桥接服务。

### `apps/stage-tamagotchi`

Electron 桌面版应用，是当前桌面形态的主要入口，适合本地运行虚拟角色、桌面交互和窗口能力集成。桌面端读取 `xiaomiao` 桥接状态，并把回复同步到字幕、聊天历史、TTS 和 Live2D 口型。

### `apps/stage-pocket`

移动端应用，用于承载移动场景下的 `xiaomiaoVirtual` 体验。当前已接入第一批只读 `xiaomiao` 桥接事件同步，可把聊天、工具、确认、记忆、舞台事件合并到移动端聊天历史；后续仍需桥接绑定握手、动态地址配置和专门事件 UI。

### `apps/server`

服务端 API，负责后端接口、服务能力与部分系统级功能支持。

### `apps/component-calling`

组件调用和实时音频实验应用，用于验证组件化调用能力，当前不是 QQ 主链路。

### `apps/ui-server-auth`

服务端鉴权 UI，用于配合 `apps/server` 和 server-runtime 相关能力，当前不是 QQ 主链路。

### `packages/*`

共享 UI、业务组件、运行时、SDK、工具模块等核心公共能力。按用途大致分为：

- 舞台 UI 与布局：`stage-ui`、`stage-layouts`、`stage-pages`、`stage-shared`。
- 渲染和模型：`stage-ui-live2d`、`stage-ui-three`、`model-driver-lipsync`、`model-driver-mediapipe`。
- 语音和音频：`audio`、`pipelines-audio`、`audio-pipelines-transcribe`。
- 插件和服务协议：`plugin-sdk`、`plugin-sdk-tamagotchi`、`plugin-protocol`、`server-runtime`、`server-sdk`、`server-schema`、`server-shared`。
- 角色、Agent 和记忆：`core-character`、`core-agent`、`memory-pgvector`。
- 基础 UI、字体和工具：`ui`、`ui-loading-screens`、`ui-transitions`、`i18n`、`font-*`、`cap-vite`、`vishot-*`。

### `services/*`

外部服务能力，包括 Computer Use MCP、Minecraft、Twitter、Satori、Discord、Telegram。它们是后续让 QQ/Agent 调用更多外部能力的主要来源，但写操作和本机控制默认需要白名单与确认。

### `plugins/*`

插件能力，包括 HomeAssistant、Bilibili、Chess、Claude Code 和 Browser Extension。当前目录已保留源码，QQ 侧仍以 Agent 工具适配为入口，不直接操作前端插件内部状态。

### `docs`

项目文档站与补充资料。

## 服务和插件清单

服务、插件、Agent 工具适配状态以 [services-and-plugins.md](services-and-plugins.md) 为准。该文档覆盖 `apps`、`services`、`plugins`、`packages`、已打通的 QQ Agent 工具，以及仍未接入 QQ 的能力边界。

---

## 启动方式

### 统一 Agent 联动前置服务

如果要联动 `xiaomiao`、QQ 和 xiaomiaoAgent，推荐从仓库根目录启动：

```powershell
cd <项目根目录>
pnpm run start:all
```

`pnpm run start:all` 会串行启动 QQ 协议端、xiaomiaoAgent API、xiaomiaoAgent 网关、xiaomiao 桥接服务、stage-web 和 xiaomiaoAgent WebUI。QQ/NapCat 登录窗口保持可见，其它服务窗口默认最小化；前一步没有通过健康检查时，后续服务不会打开。

手动启动时，先启动后端链路：

```powershell
cd <项目根目录>\xiaomiaoAgent
conda activate xiaomiao
python -m xiaomiao_agent serve --config <项目根目录>\xiaomiaoAgent\.nanobot\config.json
```

再启动 NapCat 和 `xiaomiao`：

```powershell
cd <项目根目录>\xiaomiao
conda activate xiaomiao
python main.py
```

关键端口：

```text
5004  NapCat OneBot WebSocket
5519  xiaomiao 桥接服务
8765  xiaomiaoAgent 网关
8900  xiaomiaoAgent OpenAI 兼容 API
5174  xiaomiaoAgent WebUI
5175  xiaomiaobot stage-web
```

`python main.py` 会先启动桥接服务，再连接 OneBot。如果 NapCat 未启动或 WebSocket 断开，主进程会退出，`stage-web` 也会因为 `5519` 不存在而显示桥接错误。

QQ / Web / xiaomiaoAgent WebUI 共享 `xiaomiao-unified` 会话和桥接事件。QQ 本地命令 `帮助`、`关于`、`读图` 使用精确匹配，普通问题中包含这些词时仍会进入 xiaomiaoAgent。

QQ 工具请求会经过权限网关：普通用户默认只能触发 `low_risk` 工具；ROOT/Super/`agent_tool_allowlist` 用户请求本机命令、MCP 动作或外部服务写操作时，会直接以 `trusted_confirmed` 策略执行。

### 方式一：启动 Web 版

```powershell
pnpm dev:web
```

适用于：

- 浏览器环境调试
- 页面与交互开发
- Web 场景预览
- 验证 `stage-web -> xiaomiao 桥接服务 -> xiaomiaoAgent` 链路

第一次打开 Web 版会先通过桥接服务读取主目录 `config.json`。配置完整时不会弹配置面板；配置缺失时填写中转站 URL、API Key 和模型后会同步写回主目录 `config.json`。桥接服务不可用、xiaomiaoAgent 不可用或返回空回复时，聊天历史会出现明确 error 消息，不会静默回退到 xiaomiaobot 提供方。网页消息会通过桥接事件回放，刷新页面后仍能看到三端同步记录。工具执行、记忆整理和舞台动作也会进入同一事件流。

Live2D 模型和 VRM 下载缓存集中在仓库根目录 `.cache/xiaomiaobot/`。Cubism SDK 仍由外部 `DownloadLive2DSDK()` 插件写入各 app 的 `.cache/`，后续需要替换或扩展该插件才能彻底集中。

### 方式二：启动桌面 Electron 版

```powershell
pnpm dev:tamagotchi
```

适用于：

- 本地桌面运行
- 虚拟角色展示
- Electron 能力联调
- 验证 `xiaomiao 桥接状态 -> 桌面字幕 / 聊天历史 / TTS / Live2D` 表现链路

### 方式三：启动文档站

```powershell
pnpm dev:docs
```

### 方式四：启动服务端 API

```powershell
pnpm -F @proj-airi/server dev
```

服务端 API 默认读取：

```text
apps/server/.env.local
```

---

## 配置说明

### 服务端配置

当你需要运行 `apps/server` 时，主要配置文件为：

```text
apps/server/.env.local
```

该文件通常用于配置：

- 网关地址
- 模型服务相关参数
- 服务端运行所需环境变量

### 多端协作说明

`xiaomiaobot` 采用 pnpm 工作区组织多个应用与共享包，因此日常开发通常不是只运行一个目录，而是根据你的目标选择对应入口：

- 做 Web 页面：优先启动 `stage-web`；如果要测聊天输入，必须同时启动 `xiaomiao` bridge 和 xiaomiaoAgent API
- 做桌面端能力：优先启动 `stage-tamagotchi`；如果要测小喵回复表现，必须同时启动 `xiaomiao`
- 做后端接口：优先启动 `server`
- 做共享组件或业务逻辑：在 `packages/*` 中修改并联调

---

## 常用命令

### 构建命令

构建 Web 版：

```powershell
pnpm build:web
```

构建桌面 Electron 版：

```powershell
pnpm build:tamagotchi
```

构建全部应用和包：

```powershell
pnpm build
```

### 质量检查

类型检查：

```powershell
pnpm typecheck
```

代码规范检查：

```powershell
pnpm lint
```

自动修复代码规范问题：

```powershell
pnpm lint:fix
```

运行测试：

```powershell
pnpm test:run
```

---

## 项目结构

```text
xiaomiaobot/
├── apps/
│   ├── stage-web/           # Web 应用
│   ├── stage-tamagotchi/    # Electron 桌面版应用
│   ├── stage-pocket/        # 移动端应用
│   ├── server/              # 服务端 API
│   ├── component-calling/   # 组件调用和实时音频实验
│   └── ui-server-auth/      # 服务端鉴权 UI
├── packages/                # 共享 UI、业务、运行时、SDK、工具包
├── services/                # Computer Use、Minecraft、Twitter 等服务
├── plugins/                 # HomeAssistant、Bilibili、Chess 等插件
├── integrations/            # VSCode 等外部集成
├── engines/                 # Godot 等引擎实验
├── nix/                     # Nix 打包配置
├── docs/                    # 文档站与补充资料
├── eslint.config.js         # 代码规范配置
├── uno.config.ts            # UnoCSS 配置
├── vitest.config.ts         # 测试配置
└── package.json             # 工作区根配置
```

与小喵联动相关的关键文件：

```text
xiaomiaobot/
├── apps/stage-web/src/pages/index.vue
├── packages/stage-layouts/src/xiaomiao-bridge.ts
├── packages/stage-layouts/src/components/Widgets/ChatArea.vue
└── packages/stage-layouts/src/components/Layouts/MobileInteractiveArea.vue
```

`xiaomiao-bridge.ts` 固定请求 `http://127.0.0.1:5519/v1/chat/completions`。该 bridge 再转发到 xiaomiaoAgent 的 `http://127.0.0.1:8900/v1/chat/completions`。消息同步事件读取同一个 bridge 的 `/v1/xiaomiao/events`，用于 Web、桌面和 QQ 侧的统一消息历史。

---

## 全结构索引

[struct.md](struct.md) 是 `xiaomiaobot` 的全目录和全文件作用索引，适合查找具体文件、包、服务、插件和上游保留目录。日常运行和联动说明优先看本文；需要定位细节时再查结构索引。

---

## Git 仓库说明

`xiaomiaobot` 现在作为 `xiaomiaoVirtual` 仓库的子目录管理，不需要在该目录下重新初始化 `.git`。如果你单独抽出 `xiaomiaobot` 做上游开发，才需要重新初始化仓库：

```powershell
git init
git branch -M main
git add .
git commit -m "chore: initialize repository"
```

绑定远端并上传：

```powershell
git remote add origin https://github.com/<你的账号>/<你的仓库>.git
git push -u origin main
```

---

## 补充说明

- 如果你是第一次接触 `xiaomiaoVirtual`，建议先从 `pnpm dev:tamagotchi` 或 `pnpm dev:web` 开始
- 如果你需要了解更细的项目说明，可以继续查看 `docs/` 目录
- 如果你在多端联调，请优先确认当前修改属于 `apps/*` 还是 `packages/*`

更多补充操作可结合项目内其他文档继续查看。
