✅ 安装完成。

**📍 安装位置**

- 仓库位置：`C:\Users\liu'zhi'gui\.understand-anything\repo`
- 通用插件根链接：`C:\Users\liu'zhi'gui\.understand-anything-plugin`
- Codex skills 目录：`C:\Users\liu'zhi'gui\.agents\skills`

已安装 8 个 Codex skills：

```text
understand
understand-chat
understand-dashboard
understand-diff
understand-domain
understand-explain
understand-knowledge
understand-onboard
```

**🧪 验证结果**

- `repo` 存在。
- `.understand-anything-plugin` 是 junction，指向真实插件目录。
- `understand` 等 skills 都已链接到 `.agents\skills`。
- 已读取 `SKILL.md`，确认可用。

**🛠️ 怎么用**

重启 Codex 后生效。

在项目里可以这样用：

```text
/understand --language zh
```

它会分析当前项目，并在项目下生成：

```text
.understand-anything/knowledge-graph.json
```

之后可以继续用：

```text
/understand-chat 解释这个项目的整体架构
/understand-explain xiaomiao/main.py
/understand-diff
/understand-dashboard
```

简言之：先跑 `/understand` 建图，再用 `/understand-chat`、`/understand-explain` 等命令基于知识图提问或分析。
