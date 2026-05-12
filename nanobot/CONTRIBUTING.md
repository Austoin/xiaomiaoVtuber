## 分支策略

我们使用双分支模型，在稳定性和探索之间取得平衡：

| 分支 | 目的 | 稳定性 |
|--------|---------|-----------|
| `main` | 稳定发布 | 可用于生产 |
| `nightly` | 实验性功能 | 可能包含 bug 或破坏性变更 |

### 应该提交到哪个分支？

**如果 PR 包含以下内容，请提交到 `nightly`：**

- 新功能或新能力。
- 可能影响现有行为的重构。
- API 或配置变更。

**如果 PR 包含以下内容，请提交到 `main`：**

- 不改变行为的 bug 修复。
- 文档改进。
- 不影响功能的小调整。

**如果不确定，请提交到 `nightly`。** 将稳定想法从 `nightly` 移到 `main`，比在稳定分支落入高风险变更后再撤回更容易。

### 开始工作

修改前，请同步目标分支，并基于它创建主题分支。
稳定 bug 修复和纯文档变更应从最新 `main` 开始。
实验性工作应从最新 `nightly` 开始。

```bash
git fetch upstream
git switch main
git pull --ff-only upstream main
git switch -c your-topic-branch
```

如果你的 checkout 使用不同的远端名，请用你主要的 HKUDS/nanobot remote 替换 `upstream`。

不要把无关本地变更混入主题分支。如果你的 checkout 已经有进行中的工作，请使用单独 worktree，或先完成当前工作再创建新分支。

### nightly 如何合并到 main？

我们不会整体合并 `nightly` 分支。稳定功能会从 `nightly` **cherry-pick** 到单独 PR，再合入 `main`：

```text
nightly  ──┬── feature A（稳定） ──► PR ──► main
           ├── feature B（测试中）
           └── feature C（稳定） ──► PR ──► main
```

这通常大约 **每周一次**，但具体时间取决于功能何时足够稳定。

### 快速总结

| 你的变更 | 目标分支 |
|-------------|---------------|
| 新功能 | `nightly` |
| Bug 修复 | `main` |
| 文档 | `main` |
| 重构 | `nightly` |
| 不确定 | `nightly` |

## 开发环境

保持安装流程平淡而可靠。目标是让你尽快进入代码：

```bash
# 克隆仓库
git clone https://github.com/HKUDS/nanobot.git
cd nanobot

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# Lint 代码
ruff check nanobot/

# 格式化代码
ruff format nanobot/
```

## 贡献许可

提交贡献即表示你确认自己有权提交这些内容，并同意它们以项目的 MIT License 授权。

## 代码风格

我们关心的不只是通过 lint。我们希望 nanobot 保持小巧、平静、可读。

贡献时，请尽量让代码具备以下特质：

- 简单：优先选择能解决真实问题的最小变更。
- 清晰：为下一位读者优化，而不是为了炫技。
- 解耦：保持边界清楚，避免不必要的新抽象。
- 诚实：不隐藏复杂性，也不制造额外复杂性。
- 耐久：选择易维护、易测试、易扩展的方案。

实际约定：

- 行宽：100 字符（`ruff`）。
- 目标版本：Python 3.11+。
- Lint：`ruff`，启用规则 E、F、I、N、W（忽略 E501）。
- 异步：全项目使用 `asyncio`；pytest 使用 `asyncio_mode = "auto"`。
- 优先写可读代码，而不是魔法代码。
- 优先提交聚焦补丁，而不是大范围重写。
- 如果引入新抽象，它必须明确降低复杂度，而不是把复杂度换个地方。

## 修改 CI Workflow

如果你的 PR 修改 `.github/workflows/`，请让 CI 保持在 GitHub Actions 免费额度内：

- 只使用标准 GitHub 托管 runner（`ubuntu-latest`、`windows-latest`）。
- 避免 macOS runner、大规格 runner（`*-cores`、`*-xlarge`、`*-gpu`）和 self-hosted runner。
- 避免上传大体积 artifact 或使用很长的保留时间。
- 避免付费 Marketplace action。