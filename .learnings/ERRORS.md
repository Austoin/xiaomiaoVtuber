# 错误记录

## [ERR-20260512-001] apply_patch_empty_payload

**Logged**: 2026-05-12T00:00:00+08:00
**Priority**: low
**Status**: pending
**Area**: docs

### Summary
翻译文档过程中误调用了空参数 `apply_patch`，导致工具执行被中止。

### Error
```text
Tool execution aborted
```

### Context
- 操作：调用 `apply_patch`。
- 输入：空 JSON 对象 `{}`。
- 影响：没有修改文件，但浪费了一次工具调用。

### Suggested Fix
调用 `apply_patch` 前必须确认 `patchText` 非空，并包含完整 `*** Begin Patch` / `*** End Patch` 块。

### Metadata
- Reproducible: yes
- Related Files: nanobot/SECURITY.md
- See Also: 再次发生于继续翻译 `nanobot/SECURITY.md` 前，原因仍是误发空 `apply_patch` 参数。

---

## [ERR-20260513-001] conda_run_unicode_help

**Logged**: 2026-05-13T00:00:00+08:00
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
在 Windows 上通过 `conda run -n xiaomiao nanobot --help` 检查 CLI 时，conda 输出包含 GBK 无法编码字符，触发 `UnicodeEncodeError` 并进入错误报告提示。

### Error
```text
UnicodeEncodeError: 'gbk' codec can't encode character '\ufffd'
```

### Context
- 命令：`conda run -n xiaomiao nanobot --help`
- 环境：Windows PowerShell，conda 24.11.3，`xiaomiao` 环境。
- 影响：帮助输出失败，但不代表 nanobot CLI 不可用。

### Suggested Fix
运行 conda 命令时设置 `PYTHONIOENCODING=utf-8` 和 `CONDA_NO_PLUGINS=true`，或在已激活的 conda 环境中直接运行 `nanobot`。

### Metadata
- Reproducible: yes
- Related Files: docs/STARTUP.md

---
