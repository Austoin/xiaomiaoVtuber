# Project AIRI

Project AIRI 是一个面向 AI 虚拟角色 / AI waifu 的多端应用项目，目标是让 AI 角色以 Web、桌面端、移动端和服务端能力进入真实使用场景。

## 目录

- [快速开始](#快速开始)
- [主要模块](#主要模块)
- [启动方式](#启动方式)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [项目结构](#项目结构)
- [重新建立 Git 仓库](#重新建立-git-仓库)

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
   - Server API：`pnpm -F @proj-airi/server dev`

---

## 主要模块

### `apps/stage-web`

Web 版应用，适合在浏览器中运行和调试，用于承载 AIRI 的前端交互能力。

### `apps/stage-tamagotchi`

Electron 桌面版应用，是当前桌面形态的主要入口，适合本地运行虚拟角色、桌面交互和窗口能力集成。

### `apps/stage-pocket`

移动端应用，用于承载移动场景下的 AIRI 体验。

### `apps/server`

服务端 API，负责后端接口、服务能力与部分系统级功能支持。

### `packages/*`

共享 UI、业务组件、运行时、SDK、工具模块等核心公共能力。

### `docs`

项目文档站与补充资料。

---

## 启动方式

### 方式一：启动 Web 版

```powershell
pnpm dev:web
```

适用于：

- 浏览器环境调试
- 页面与交互开发
- Web 场景预览

### 方式二：启动桌面 Electron 版

```powershell
pnpm dev:tamagotchi
```

适用于：

- 本地桌面运行
- 虚拟角色展示
- Electron 能力联调

### 方式三：启动文档站

```powershell
pnpm dev:docs
```

### 方式四：启动 Server API

```powershell
pnpm -F @proj-airi/server dev
```

Server API 默认读取：

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

Project AIRI 采用 pnpm workspace 组织多个应用与共享包，因此日常开发通常不是只运行一个目录，而是根据你的目标选择对应入口：

- 做 Web 页面：优先启动 `stage-web`
- 做桌面端能力：优先启动 `stage-tamagotchi`
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

Lint 检查：

```powershell
pnpm lint
```

自动修复 Lint：

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
AuBot/
├── apps/
│   ├── stage-web/          # Web 应用
│   ├── stage-tamagotchi/   # Electron 桌面版应用
│   ├── stage-pocket/       # 移动端应用
│   └── server/             # 服务端 API
├── packages/               # 共享 UI、业务、运行时、SDK、工具包
├── docs/                   # 文档站与补充资料
├── eslint.config.js        # Lint 配置
├── uno.config.ts           # UnoCSS 配置
├── vitest.config.ts        # 测试配置
└── package.json            # workspace 根配置
```

---

## 重新建立 Git 仓库

如果当前目录没有 `.git`，可以重新初始化仓库：

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

- 如果你是第一次接触 AIRI，建议先从 `pnpm dev:tamagotchi` 或 `pnpm dev:web` 开始
- 如果你需要了解更细的项目说明，可以继续查看 `docs/` 目录
- 如果你在多端联调，请优先确认当前修改属于 `apps/*` 还是 `packages/*`

更多补充操作可结合项目内其他文档继续查看。
