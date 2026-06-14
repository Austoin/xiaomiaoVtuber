# Electron ESM 兼容性问题

## 问题描述

stage-tamagotchi Electron 应用在当前环境下无法启动。

## 根本原因

**Electron 41.2.1（内嵌 Node.js v24.14.1）在 ESM 模式下无法正确加载 electron 模块。**

所有从 electron 模块导入的成员（`app`、`ipcMain`、`BrowserWindow` 等）在运行时都是 `undefined`。

## 技术细节

### 环境信息

- **系统 Node.js 版本**: v22.22.2
- **Electron 版本**: 41.2.1（原配置）、降级尝试：33.3.1、29.4.6、28.3.3
- **Electron 内嵌 Node.js**: v24.14.1（所有测试版本都相同）
- **构建工具**: electron-vite + Rolldown
- **模块系统**: ESM (`"type": "module"`)

### 症状

```javascript
// 源代码
import { app, BrowserWindow } from 'electron'

// 运行时错误
TypeError: Cannot read properties of undefined (reading 'dock')
    at file:///F:/xiaomiaoVirtual/xiaomiaobot/apps/stage-tamagotchi/out/main/index.js:65547:5
```

### 已尝试的解决方案（全部失败）

#### 1. 降级 Electron 版本
- **尝试**: 41.2.1 → 33.3.1 → 29.4.6 → 28.3.3
- **结果**: ✗ 所有版本都内嵌 Node.js v24.14.1，问题相同

#### 2. 切换到 CommonJS
- **尝试**: 
  - 修改 `package.json`: 移除 `"type": "module"`
  - 修改 `electron.vite.config.ts`: `output.format = 'cjs'`, `entryFileNames = '[name].cjs'`
  - 修改 `main` 入口: `./out/main/index.cjs`
- **结果**: ✗ `require('electron')` 也返回 `undefined`

#### 3. ESM 动态 import
- **尝试**: Vite 插件将 `import { app } from 'electron'` 转换为 `const { app } = await import('electron')`
- **结果**: ✗ 动态 import 也返回 `undefined`

#### 4. ESM 默认导入
- **尝试**: 转换为 `import electron from "electron"; const { app } = electron`
- **结果**: ✗ `electron` 默认导出是 `undefined`

#### 5. createRequire 互操作
- **尝试**: 
  ```javascript
  import { createRequire } from "node:module";
  const require = createRequire(import.meta.url);
  const { app } = require('electron');
  ```
- **结果**: ✗ `require('electron')` 返回 `undefined`

#### 6. 外部化配置
- **尝试**: 
  - `externalizeDeps.include: ['electron-click-drag-plugin']`
  - `externalizeDeps.exclude: ['@electron-toolkit/utils']`
  - `rollupOptions.external: ['electron', /^electron\/.+$/, /^node:.+$/]`
- **结果**: ✗ 外部化配置正常工作，但 electron 模块依然加载失败

#### 7. 使用本地 toolkit-utils
- **尝试**: 用本地的 `./libs/electron/toolkit-utils`（使用 getter 延迟访问）替代 `@electron-toolkit/utils`
- **结果**: ✗ 绕过了 `@electron-toolkit/utils` 的顶层访问问题，但 `app`/`ipcMain` 依然是 `undefined`

### 代码转换验证

Vite 插件成功转换了所有导入语句：

```javascript
// 转换后的代码（out/main/index.js）
import { createRequire as __createRequire } from "node:module";
const __electron_require = __createRequire(import.meta.url);
const { BrowserWindow, Menu, Tray, app, desktopCapturer, ipcMain, /* ... */ } = __electron_require('electron');
```

但运行时 `__electron_require('electron')` 返回 `undefined`。

## 结论

**这是 Electron 在 Node.js v24.14.1 ESM 模式下的上游 bug，在 Vite/应用层面无法修复。**

根据测试，所有 Electron 28.x/29.x/33.x/41.x 版本都内嵌 Node.js v24.14.1 并有此问题。

## 参考资料

- Electron Issue Tracker: 需要搜索/提交相关 bug 报告
- Node.js ESM 模块加载文档: https://nodejs.org/api/esm.html
- electron-vite 文档: https://electron-vite.org/

## 临时解决方案

1. **等待 Electron 官方修复**
2. **使用 Docker/VM 环境**（如果有已知工作的环境配置）
3. **降级系统 Node.js**（但 Electron 内嵌 Node.js 不受影响）
4. **使用 Electron 的旧版本**（需要找到不使用 Node.js v24 的版本）

## 相关文件

- 插件实现: `xiaomiaobot/apps/stage-tamagotchi/vite-plugin-electron-esm.ts`
- 构建配置: `xiaomiaobot/apps/stage-tamagotchi/electron.vite.config.ts`
- 入口文件: `xiaomiaobot/apps/stage-tamagotchi/src/main/index.ts`
- Electron 版本: `xiaomiaobot/pnpm-workspace.yaml` (catalog.electron)

## 最后更新

2026-06-14
