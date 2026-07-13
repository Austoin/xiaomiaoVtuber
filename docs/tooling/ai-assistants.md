# AI 辅助工具配置

项目不再在 `xiaomiaobot/` 内保留零散 AI 工具目录，例如 `.gemini/`。AI 协作约定统一记录在文档中。

## Gemini Code Assist

原 `xiaomiaobot/.gemini/config.yaml` 仅忽略了：

```yaml
ignore_patterns:
  - packages/i18n/src/**
```

原 `xiaomiaobot/.gemini/styleguide.md` 的核心规则是：

- 给代码修改建议时使用 GitHub suggestion block。
- 多方案建议时分别给出独立 suggestion block。

示例：

````markdown
```suggestion
// suggested code
```
````

## Agent Skills

`xiaomiaobot/.agents/` 当前仍保留，因为它包含项目专用的 agent skill 知识库，例如：

- Vue / VueUse 最佳实践
- pnpm workspace 使用
- UnoCSS
- xsai
- agent-browser / electron 浏览器自动化

这些内容不是运行时代码，但对 AI 协作仍有价值。后续如果继续瘦身，建议将其迁移到：

```text
docs/archive/ai-agents/xiaomiaobot-agents/
```

迁移前不要直接删除 `.agents/`，避免丢失项目特定协作上下文。
