# 编辑器本地设置

项目不再在 `xiaomiaobot/` 内保留具体编辑器目录，例如 `.vscode/`、`.zed/`、`.cursor/`。这些目录属于开发者本地环境，可按个人工具自行生成。

## 通用约定

- 使用项目 ESLint 作为主要格式化与修复入口。
- 不启用 Prettier 作为默认格式化器。
- TypeScript SDK 优先使用工作区内的 `node_modules/typescript/lib`。
- 建议关闭不必要的自动导入，避免生成不稳定引用。

## VSCode 建议插件

原 `xiaomiaobot/.vscode/extensions.json` 推荐过以下插件类型：

- Vue / Volar
- ESLint
- UnoCSS
- i18n Ally
- Vitest
- YAML / dotenv / Markdown 辅助
- Code Spell Checker
- EditorConfig

## Zed 设置要点

原 `xiaomiaobot/.zed/settings.json` 主要做了两件事：

- 对 TypeScript、JavaScript、Vue、JSON、YAML、TOML 启用保存时 ESLint 修复。
- 在编辑器诊断里弱化样式类规则，例如缩进、空格、引号、分号、换行和排序类规则。

这些设置不影响项目构建；需要时可在个人编辑器配置中恢复。

## Cursor 自定义命令

原 `xiaomiaobot/.cursor/commands/deslop.md` 是一个本地代码清理提示词，作用是检查分支 diff 并移除明显 AI 生成痕迹，例如：

- 不符合项目风格的冗余注释。
- 不必要的防御式 `try/catch`。
- 为绕过类型错误而使用的 `any`。
- 与当前文件风格不一致的写法。

这类提示词不属于运行时能力，统一不放在项目源码目录内。

## 本地缓存与生成文件

以下文件/目录属于本地缓存或构建生成物，不应进入仓库：

- `.turbo/`：Turborepo 构建缓存，可随时删除。
- `.eslintcache`：ESLint 缓存，可随时删除。
- `node_modules/`：包管理器安装结果，不提交。
- `*.tsbuildinfo`：TypeScript 增量编译缓存，由 `tsc` / `vue-tsc` 自动生成。
- `typed-router.d.ts`：部分应用的路由类型生成文件，已按路径忽略。
- `public/assets/`：部分应用的构建/同步产物，已按路径忽略。

如果这些文件被重新生成，直接保留在本地即可；需要彻底清理时可删除后重新运行对应安装、构建或类型检查命令。
