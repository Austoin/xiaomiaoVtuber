# xiaomiaobot

基于 pnpm workspace 的多端交互项目，包含 Web、Pocket、Electron、插件、服务和共享 SDK。

本文同时作为本目录的项目入口和文件维护说明。依赖、缓存、编译结果、模型和二进制资源按生成来源统一说明，业务目录与 workspace 包按职责说明。

## 1. 项目定位

`xiaomiaobot` 是一个以 pnpm workspace 管理的 TypeScript monorepo，主要技术栈为 Vue 3、Vite、Pinia、UnoCSS、Electron、Capacitor、Vitest 与 Turbo。它同时提供浏览器端、桌面端、移动端、插件、服务和共享 SDK。

本文档解释项目中需要开发者理解和维护的目录；`node_modules`、`.turbo`、`.cache`、`dist`、`out`、模型文件和第三方二进制只按类别说明，不逐个展开。

“所有文件和目录”在本文中的口径是：根文件逐项说明，一级业务目录逐项说明，workspace 包逐项说明，应用内部按职责说明；依赖、缓存、编译结果、模型和二进制资源按生成来源统一说明。当前工作区包含大量依赖文件，机械列出每个依赖文件既不能帮助维护，也会很快失效。

## 2. 运行关系

```text
apps/stage-web       ─┐
apps/stage-pocket    ─┼─> packages/stage-ui / stage-shared / server-sdk
apps/stage-tamagotchi┘
                              │
                              ├─> packages/core-agent / core-character
                              ├─> packages/stage-ui-live2d / stage-ui-three
                              ├─> packages/plugin-sdk / plugin-protocol
                              └─> services / integrations / plugins
```

主要入口：

- `apps/stage-web/src/main.ts`：浏览器端 Vue 应用入口。
- `apps/stage-pocket/src/main.ts`：Capacitor 移动端入口。
- `apps/stage-tamagotchi/src/main/index.ts`：Electron 主进程入口；负责窗口、IPC、更新、插件和本地服务。
- 各应用的 `src/`：页面、组件、路由、状态和平台适配。
- `packages/stage-ui/src/`：共享舞台 UI 与业务状态的核心实现。

## 3. 根目录文件

| 文件 | 作用 |
|---|---|
| `.editorconfig` | 统一缩进、换行和字符集。 |
| `.gitattributes` | Git 行尾、二进制和 diff 行为配置。 |
| `.prototools` | Proto 工具链的 dotnet 插件来源配置。 |
| `.tool-versions` | asdf/mise 兼容的 Node.js 版本锁定（当前为 24.13.0）。 |
| `AGENTS.md` | 项目协作、代码质量和自动化代理规则。 |
| `bump.config.ts` | 版本号和发布版本递增配置。 |
| `CLAUDE.md` | 极简的辅助代理说明入口。 |
| `crowdin.yml` | Crowdin 多语言翻译同步配置。 |
| `cspell.config.yaml` | 拼写检查词典和忽略规则。 |
| `default.nix`、`flake.nix`、`flake.lock` | Nix 开发环境与可复现依赖锁定。 |
| `eslint.config.js` | ESLint flat config，包含 TypeScript/Vue 等规则。 |
| `knip.json` | 未使用文件、导出和依赖检查配置。 |
| `package.json` | workspace 脚本、依赖和发布元数据；`test:run` 实际执行 `vitest run`。 |
| `pnpm-lock.yaml` | pnpm 精确依赖锁。 |
| `pnpm-workspace.yaml` | apps、packages、plugins、services、docs、engines、integrations 的 workspace 范围、catalog、override 与 patch。 |
| `posthog.config.ts` | PostHog 分析配置。 |
| `skills-lock.json` | 项目技能包版本锁定。 |
| `sponsorkit.config.js` | 赞助者徽标/数据生成配置。 |
| `tsconfig.json` | TypeScript 根配置和项目引用。 |
| `turbo.json` | Turbo 任务依赖、缓存和输出声明。 |
| `uno.config.ts` | UnoCSS 主题、快捷方式和预设。 |
| `vite-env.d.ts` | Vite 环境变量类型声明。 |
| `vitest.config.ts` | Vitest 多项目配置，当前注册多个应用和包的测试项目。 |

## 4. 一级目录

### `.agents/skills`

项目内可复用的代理技能、提示词和自动化说明。修改技能时应同步检查技能锁文件及其引用。

### `.turbo`

Turbo 本地缓存。删除后可重新生成，不属于业务源码。

### `apps`

- `stage-web`：桌面/浏览器优先的 Web 舞台，含 `src`、`public`、Vite 配置和构建输出。
- `stage-pocket`：Capacitor 移动应用；`android`、`ios` 是原生工程，`resources` 是平台资源，`src` 是共享前端入口。
- `stage-tamagotchi`：Electron 桌面应用；`src/main` 为主进程，`src/renderer` 为渲染器，`resources` 为打包资源，`scripts` 为构建辅助。
- 根目录 `../.cache/xiaomiaobot`：模型和图片下载缓存，由三个 Vite/Electron 构建入口共享，避免各应用重复保存同一批资源。
- 根目录 `../.cache/turbo/xiaomiaobot`：Turborepo 任务缓存，由 `turbo.json` 的 `cacheDir` 统一配置。
- 根目录 `../.cache/eslint/xiaomiaobot/.eslintcache`：ESLint 持久化缓存；`lint`、`lint:fix` 和 `nano-staged` 共用此路径。
- 项目内旧 `.cache`、`.turbo`：历史缓存位置，可以安全删除；新构建不应再向这些目录写入共享缓存。
- `dist`、`build`、`out`、`node_modules`：分别是构建产物和安装依赖。前三者可重建，`node_modules` 可通过 `pnpm install --frozen-lockfile` 重建。

三个应用根目录中的通用文件职责：

- `package.json`：应用级脚本和依赖。
- `tsconfig.json`：应用 TypeScript 配置。
- `uno.config.ts`：应用样式主题和快捷规则。
- `vite-env.d.ts`：Vite 环境类型。
- `vite.config.ts`、`electron.vite.config.ts`：Web/移动或 Electron 构建配置。
- `vitest.config.ts`：应用测试配置。
- `index.html`：Web 或移动端 HTML 入口。
- `capacitor.config.ts`：移动端应用 ID、Web 输出和原生插件配置。
- `electron-builder.config.ts`、`dev-app-update.yml`：桌面打包和开发更新配置。
- `ai.moeru.airi.desktop`、`ai.moeru.airi.flatpak.yml`：Linux desktop/Flatpak 分发元数据。
- `netlify.toml`、`wrangler.toml`：Web 站点在 Netlify/Cloudflare 的部署配置。
- `stage-tamagotchi/src/main`、`preload`、`renderer`、`shared`：Electron 主进程、预加载桥、渲染进程和共享契约。

### `bucket`

Scoop bucket 清单，目前包含 `airi.json`，用于在 Windows 上分发或安装 AIRI 相关工具。它不是运行时业务代码。

### `docs`

VitePress 文档站。`content/en`、`content/ja`、`content/zh-Hans` 分别存放英文、日文和简体中文内容；`public` 存放静态资源。新增文档应同步导航、语言版本和链接。

### `engines/stage-tamagotchi-godot`

Godot/C# 原生舞台实验引擎。用于探索高性能场景、动画和设备能力；与 Electron/Vue 舞台通过约定接口衔接。生成的构建目录不应提交。

### `integrations/vscode`

- `vscode-airi`：VS Code 扩展，面向编辑器命令、面板和开发者体验。
- `airi-plugin-vscode`：AIRI 侧插件，实现与 VS Code 扩展通信的插件端能力。

### `nix`

Nix 辅助表达式、开发 shell 和打包脚本，保证跨机器环境一致。

### `node_modules`

pnpm 安装的依赖链接和包内容；由 lockfile 决定，不直接修改。

### `packages`

共享库集合。每个包通常包含 `src`、`package.json`、测试和构建配置：

| 包 | 职责 |
|---|---|
| `audio` | 音频编码、解码、波形和通用处理。 |
| `audio-pipelines-transcribe` | 语音转文字管线及其适配。 |
| `cap-vite` | 启动 Vite 与 Capacitor live reload 的命令行工具。 |
| `ccc` | 配置、转换和导出相关工具；具体能力以其 `src` 和导出 API 为准。 |
| `core-agent` | 与 xiaomiaoAgent 对接的客户端协议、消息、会话和运行时 hook。 |
| `core-character` | 角色文本分段、情绪、延迟、TTS 流式编排。 |
| `drizzle-duckdb-wasm` | Drizzle ORM 与 DuckDB WASM 的适配。 |
| `duckdb-wasm` | 浏览器/Worker 中的 DuckDB WASM 封装。 |
| `electron-eventa` | Electron IPC 的 Eventa 合约和类型。 |
| `electron-screen-capture` | 桌面屏幕捕获能力。 |
| `electron-vueuse` | Electron 场景下的 VueUse 风格 composable。 |
| `font-*`（四个包） | ChillRoundM、CJK 全濑体、Departure Mono、小赖字体的 CSS 与字体资源。 |
| `i18n` | 多语言 locale、翻译加载和格式化工具。 |
| `memory-pgvector` | 基于 pgvector 的记忆存取适配。 |
| `model-driver-lipsync` | 口型同步模型驱动接口和实现。 |
| `model-driver-mediapipe` | MediaPipe 动捕实验模块；受独立 `AGENTS.md` 约束。 |
| `pipelines-audio` | 采集、VAD、编码、流式传输等音频编排。 |
| `plugin-protocol` | 插件事件定义和共享 WebSocket 类型。 |
| `plugin-sdk` | 插件开发 SDK、生命周期和能力封装。 |
| `plugin-sdk-tamagotchi` | Tamagotchi 插件专用 DX 辅助。 |
| `scenarios-stage-tamagotchi-browser` | 浏览器截图场景的 Vite/Vue 应用。 |
| `scenarios-stage-tamagotchi-electron` | Electron 原始截图场景。 |
| `server-runtime` | 不同运行环境下的服务端运行时。 |
| `server-sdk` | 连接 AIRI 服务组件的客户端 SDK。 |
| `server-sdk-shared` | server-sdk 与服务端共享的事件和类型。 |
| `server-shared` | 服务端共享类型、工具和常量。 |
| `stage-layouts` | 舞台布局组件和布局数据。 |
| `stage-pages` | 可复用舞台页面。 |
| `stage-shared` | 舞台跨应用共享状态、类型和工具。 |
| `stage-ui` | 舞台核心 UI、组件、composable、store、worker、数据库和服务。 |
| `stage-ui-live2d` | Live2D 场景、模型加载和状态管理。 |
| `stage-ui-three` | Three.js 3D 场景组件。 |
| `stream-kit` | 队列、流、背压和流式工具。 |
| `ui` | 通用 UI 组件。 |
| `ui-loading-screens` | 加载屏幕和占位界面。 |
| `ui-transitions` | 页面和元素过渡动画。 |
| `unocss-preset-fonts` | 非 Google/FontSource 字体的 UnoCSS 预设。 |
| `vishot-runner-browser` | Vishot 浏览器截图执行器。 |
| `vishot-runner-electron` | 基于 Playwright 的 Electron 截图执行器。 |
| `vishot-runtime` | 截图运行时合约和 Vue 绑定。 |
| `vite-plugin-warpdrive` | 将大体积构建资源重写并上传到对象存储的 Vite 插件。 |

`stage-ui/src` 内部可按以下职责理解：`assets` 静态资源，`components` 组件，`composables` 组合式逻辑，`constants` 常量，`database` 数据库，`libs` 第三方封装，`services` 外部服务，`stores` Pinia 状态，`tools` 工具调用，`types` 类型，`utils` 纯工具，`workers` Worker 任务。

### `patches`

pnpm patch 文件，当前针对 MediaPipe、xsai、pixi-live2d 等依赖。升级依赖前必须重新验证补丁是否仍可应用。

### `plugins`

- `airi-plugin-bilibili-laplace`：Bilibili/Laplace 相关扩展。
- `airi-plugin-homeassistant`：Home Assistant 智能家居扩展。
- `airi-plugin-web-extension`：浏览器扩展桥接和网页能力。

插件通常由协议包定义事件，由 SDK 暴露开发 API，再在宿主应用注册。

### `scripts`

`list-module-loc.mjs` 用于统计模块代码行数；其他脚本负责发布、构建或维护任务。运行脚本前先阅读参数和输出目录。

### `services`

- `minecraft`：Minecraft 服务集成或桥接。
- `twitter-services`：Twitter/X 相关服务接口。

服务目录一般包含独立运行时、API 和部署配置，应通过 `server-*` 包与前端解耦。

## 5. 测试、构建与常用命令

```powershell
# 在本项目目录执行
pnpm install
pnpm test:run
pnpm lint
pnpm typecheck
pnpm build

# 只测试 xiaomiaobot（仓库根目录不提供此脚本）
pnpm --dir .\xiaomiaobot test:run
```

`test:run` 的脚本定义在 `xiaomiaobot/package.json`，因此直接在仓库根目录执行会提示找不到脚本；必须切换到 `xiaomiaobot` 或使用 `pnpm --dir`。

ESLint 缓存统一写入仓库根目录的 `../.cache/eslint/xiaomiaobot/.eslintcache`。普通检查、自动修复和提交钩子共用同一路径，不应再在 `xiaomiaobot/` 内生成 `.eslintcache`。

`lint` 同时运行 oxlint 和 ESLint；`.wxt` 浏览器扩展生成目录、`tasks/assets/wasm` 上游 WASM 资源会被两套检查器忽略，避免对生成代码和二进制伴生 JavaScript 进行无意义格式化。当前 ESLint 仍有历史 `errorMessageFrom` 迁移警告，但没有阻断性错误。

`turbo.json` 的通用 `build` 任务依赖 `^build`，保证 workspace 依赖先构建；输出同时覆盖 `dist/**` 和 Electron 的 `out/**`，避免干净环境下出现“依赖导出尚未生成”的解析错误，也避免 Electron 产物无法被 Turbo 缓存。

Vitest 配置按应用和共享包拆分项目。新增包测试时，应在 `vitest.config.ts` 注册或复用现有项目，避免测试被静默跳过。

## 6. 配置与安全

- 环境变量、服务地址、OAuth 和分析配置应放在本地环境文件或受控密钥系统。
- 不要把 API key、token、账号、二维码、Electron 用户数据提交到 Git。
- `dist`、`build`、`out`、项目内旧 `.cache`、项目内旧 `.turbo` 和测试快照属于可再生文件；出现污染时可清理并重建。根目录 `.cache/xiaomiaobot` 保存共享下载资源，删除后会重新下载，离线环境应保留。
- `model-driver-mediapipe` 等实验包可能依赖本地模型和平台权限，CI 中应提供明确的跳过条件或模拟实现。

## 7. 本轮整理记录

- 删除无引用的 `airi-targets.json`、`rustfmt.toml`，以及两个 0 字节平台占位 `index.ts`；有独立语义或仍被引用的图片、模型和平台资源均保留。
- 清理 `pnpm-workspace.yaml` 中未被 workspace `package.json` 使用的 catalog 项，保留 `ignoredBuiltDependencies` 中仍有安装行为意义的条目。
- 将 Artistry fenced JSON 提取从易产生超线性回溯的正则改为线性 `indexOf` 解析，并配套回归测试。
- 统一文档、缓存和生成目录说明；构建产物与第三方二进制不应手工纳入源码修改。

## 8. 扩展建议

1. 新功能优先放入独立 `packages/*`，应用只负责组合和平台适配。
2. 通过 `server-sdk-shared`、`plugin-protocol` 固化跨进程/跨端契约，避免复制字符串事件名。
3. 为新包提供单元测试、类型入口和最小 README，并在 Turbo/Vitest 中注册。
4. 将平台差异限制在 `apps/*` 或专用 driver 包中，保持 `stage-ui` 可复用。
5. 升级依赖时同时检查 `pnpm-lock.yaml`、`patches/`、构建产物和端到端截图。
