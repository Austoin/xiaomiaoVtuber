# GitHub 配置目录

这个目录用于保存当前 `xiaomiaoVtuber` 仓库的 GitHub 配置。

GitHub 只会自动识别仓库根目录下的 `.github`。此前删除的 `AuBot/.github` 和 `nanobot/.github` 属于上游子项目资料，不会作为当前仓库的自动化配置生效。

后续可以按需要在这里添加：

- `workflows/`：GitHub Actions 自动化流程，例如测试、构建和发布。
- `ISSUE_TEMPLATE/`：Issue 表单模板。
- `PULL_REQUEST_TEMPLATE.md`：Pull Request 模板。
- `copilot-instructions.md`：GitHub Copilot 或 coding agent 的项目指令。
- `dependabot.yml`：依赖更新配置。

当前只保留说明文件，避免在未确认 CI 策略前触发不适合本项目的自动化流程。
