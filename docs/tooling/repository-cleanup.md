# 仓库目录清理说明

本页记录当前项目中容易混淆的目录类型，避免把本地工具状态、缓存或生成文件误认为业务代码。

## 已统一忽略/清理的目录

### 编辑器与 AI 辅助工具目录

以下目录不再作为 `xiaomiaobot/` 的源码结构保留：

- `.vscode/`
- `.zed/`
- `.cursor/`
- `.gemini/`

这些内容已合并说明到：

- [editor-settings.md](editor-settings.md)
- [ai-assistants.md](ai-assistants.md)

### 缓存与生成物

以下内容属于本地生成物或缓存，不应提交：

- `.turbo/`
- `.eslintcache`
- `.cache/`
- `node_modules/`
- `*.tsbuildinfo`
- `dist/`
- `build/`
- `out/`
- `.cache/pytest/`
- `.ruff_cache/`
- `__pycache__/`

## 当前保留的协作目录

### `.claude/`

根目录 `.claude/` 仍保留，因为其中包含项目记忆和待办跟踪，例如：

- `.claude/memory/MEMORY.md`
- `.claude/memory/pending-followups-2026-07-11.md`

它是项目协作上下文，不是运行时缓存。

### `xiaomiaobot/.agents/`

`xiaomiaobot/.agents/` 仍保留，因为它包含项目专用 agent skills，例如 Vue、VueUse、pnpm、UnoCSS、xsai、browser automation 等参考材料。

如果后续继续瘦身，建议迁移到：

```text
docs/archive/ai-agents/xiaomiaobot-agents/
```

迁移完成前不直接删除，避免丢失 AI 协作知识库。

## 已发现并清理的异常

- `xiaomiaobot/apps/server/tsconfig.tsbuildinfo` 曾被 Git 跟踪；这是 TypeScript 增量编译缓存，已删除并通过 `*.tsbuildinfo` 忽略。

## 判断规则

- **源码/配置**：影响构建、运行、测试或发布，应保留。
- **协作文档**：能解释项目约定、架构或 AI 协作上下文，应保留或归档。
- **编辑器私有设置**：只影响个人开发体验，优先转为文档说明后忽略。
- **缓存/生成物**：可重建、会频繁变化，不提交。
