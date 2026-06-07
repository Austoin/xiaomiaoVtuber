# 开发与维护指南

本文说明日常改动、文档维护、测试验证和运行态清理的建议流程。

## 推荐工作顺序

1. 先阅读相关子系统文档。
2. 用 `rg` 查找真实入口和调用链。
3. 小批量修改，每批控制在清晰范围内。
4. 跑与修改范围匹配的最小验证。
5. 最后跑 `git diff --check`。

## 常用定位命令

查文件：

```powershell
rg --files
```

查文本：

```powershell
rg -n "关键词" xiaomiao xiaomiaoAgent xiaomiaobot docs
```

查看当前变更：

```powershell
git status --short
git diff --stat
```

## 文档维护规则

- `docs/README.md` 是总入口，新文档要补链接。
- `docs/运行与配置.md` 保持短，只放最短可执行流程。
- `docs/STARTUP.md` 保持详细，放完整启动和排错。
- 子系统文档放在对应目录，如 `docs/xiaomiao/`、`docs/xiaomiaoAgent/`、`docs/xiaomiaobot/`。
- 技术字段、命令、路径、配置键、函数名保持原文，不强行翻译。
- 运行态文件、缓存、下载资源不写成“需要提交”。

## 修改范围与验证

| 修改范围 | 建议验证 |
|----------|----------|
| 只改文档 | `git diff --check` |
| 根脚本 | `setup-env.cmd --check`、`start-all.cmd --check` |
| `xiaomiao/` | `python -m pytest --basetmp .pytest-tmp-xiaomiao-verify test\xiaomiao` |
| `xiaomiaoAgent/` | 相关 pytest 或 [verification.md](verification.md) 中的 Agent 矩阵 |
| `xiaomiaobot` bridge / stage | 指定 Vitest bridge 测试 |
| 跨子系统 | 运行 [verification.md](verification.md) 最小完整矩阵 |

## 运行态和缓存

这些内容通常不应提交：

- `workspace/downloads/**`
- `workspace/artifacts/**`
- `workspace/tmp/**`
- `xiaomiao/runtime/bridge_events.jsonl`
- `xiaomiaoAgent/.nanobot/**`
- `xiaomiaobot/.cache/**`
- `xiaomiaobot/services/satori-bot/data/db.json`
- `.understand-anything/**`

详细规则见 [file-workspace-hygiene.md](file-workspace-hygiene.md)。

## 配置安全

- 不提交真实 API Key。
- 不提交 QQ 账号敏感凭据。
- 不把 bridge 暴露到公网。
- 本机命令、MCP 动作、外部账号动作必须通过权限和确认链路。
- QQ 上传文件和网页抓取内容都当作不可信数据处理。

## 文档覆盖检查

新增或重构功能时，至少检查：

- 是否需要更新 `docs/README.md`。
- 是否需要更新子系统 README。
- 是否需要更新 `verification.md`。
- 是否改变了 `workspace/` 或运行态边界。
- 是否改变了 QQ 指令、权限或确认流程。
- 是否改变了启动脚本或配置结构。

## 交付摘要建议

完成一批改动后，建议汇报：

- 改了哪些文件。
- 新增或删除了哪些能力说明。
- 哪些验证已通过。
- 哪些风险或后续缺口仍存在。

