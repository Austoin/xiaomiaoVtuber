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
