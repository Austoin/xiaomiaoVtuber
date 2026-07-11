---
name: xiaomiao-cache-refactor-fix-2026-07-10
description: 缓存目录迁移到 .cache/ 时 paths.py 的 NameError 修复要点，避免再犯
metadata: 
  node_type: memory
  type: project
  originSessionId: 286da7ec-9147-4a0c-a000-cbd787ac23f9
---

2026-07-10/11 的工作批次把 nanobot 运行态从 `~/.nanobot/*` 迁到项目根 `.cache/agent/nanobot/*`。引入的 [xiaomiaoAgent/nanobot/config/paths.py](xiaomiaoAgent/nanobot/config/paths.py) 调用了 `get_default_nanobot_root()` 但只定义了 `_default_nanobot_root()`（下划线前缀），导致 `schema.py` 类定义时即 `NameError`，整个 xiaomiaoAgent 无法 import（serve / TUI / 全部测试 collection 都崩）。提交 9373958 修复，一并把 `get_media_dir/cron/logs` 改回跟随 `get_config_path().parent` 以保留多实例隔离、匹配 test_config_paths 期望。

**Why:** 重构动了默认根位置和函数命名，但少跨改一处调用名，且类定义时即求值的字段 `workspace: str = str(get_workspace_path())` 让 import 阶段就暴露错误——这是"在类字段默认值里调用会建目录的函数"的设计脆性。

**How to apply:** 改 `paths.py` 类路径函数时，全文件搜 `get_default_nanobot_root` 与 `_default_nanobot_root` 是否一致；改完先 `uv run python -c "import nanobot.config.schema"` 再跑测试，不要只信 collection 通过。后续涉及缓存路径的工作见 [[pending-followups-2026-07-11]]。
