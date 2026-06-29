#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存目录迁移脚本

将旧的 runtime/, workspace/, log/ 等目录数据迁移到新的 .cache/ 目录
"""

import shutil
import sys
import io
from pathlib import Path

# 设置标准输出编码为 UTF-8 (解决 Windows 下的编码问题)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 旧目录
OLD_XIAOMIAO_RUNTIME = PROJECT_ROOT / "xiaomiao" / "runtime"
OLD_WORKSPACE = PROJECT_ROOT / "workspace"
OLD_LOG = PROJECT_ROOT / "log"
OLD_NANOBOT_WORKSPACE = PROJECT_ROOT / "xiaomiaoAgent" / ".nanobot" / "workspace"

# 新目录
NEW_CACHE = PROJECT_ROOT / ".cache"
NEW_XIAOMIAO_RUNTIME = NEW_CACHE / "xiaomiao" / "runtime"
NEW_QQ_WORKSPACE = NEW_CACHE / "xiaomiao" / "qq_workspace"
NEW_LOG_ROOT = NEW_CACHE / "logs"
NEW_NANOBOT_WORKSPACE = NEW_CACHE / "agent" / "nanobot" / "workspace"


def migrate():
    """执行迁移"""
    print("=" * 70)
    print("🚀 缓存目录迁移工具")
    print("=" * 70)
    print(f"项目根目录: {PROJECT_ROOT}")
    print()

    migrated = []
    skipped = []
    errors = []

    # 1. 迁移 xiaomiao/runtime/
    if OLD_XIAOMIAO_RUNTIME.exists():
        print(f"📦 迁移 xiaomiao/runtime...")
        print(f"  从: {OLD_XIAOMIAO_RUNTIME}")
        print(f"  到: {NEW_XIAOMIAO_RUNTIME}")

        if NEW_XIAOMIAO_RUNTIME.exists():
            print("  ⚠️  目标已存在,跳过迁移")
            skipped.append("xiaomiao/runtime")
        else:
            try:
                NEW_XIAOMIAO_RUNTIME.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(OLD_XIAOMIAO_RUNTIME, NEW_XIAOMIAO_RUNTIME)
                print("  ✅ 迁移完成")
                migrated.append("xiaomiao/runtime")
            except Exception as e:
                print(f"  ❌ 迁移失败: {e}")
                errors.append(("xiaomiao/runtime", str(e)))
        print()

    # 2. 迁移 workspace/
    if OLD_WORKSPACE.exists():
        print(f"📦 迁移 workspace...")
        print(f"  从: {OLD_WORKSPACE}")
        print(f"  到: {NEW_QQ_WORKSPACE}")

        if NEW_QQ_WORKSPACE.exists():
            print("  ⚠️  目标已存在,跳过迁移")
            skipped.append("workspace")
        else:
            try:
                NEW_QQ_WORKSPACE.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(OLD_WORKSPACE, NEW_QQ_WORKSPACE)
                print("  ✅ 迁移完成")
                migrated.append("workspace")
            except Exception as e:
                print(f"  ❌ 迁移失败: {e}")
                errors.append(("workspace", str(e)))
        print()

    # 3. 迁移 log/
    if OLD_LOG.exists():
        print(f"📦 迁移 log...")
        print(f"  从: {OLD_LOG}")
        print(f"  到: {NEW_LOG_ROOT}")

        if NEW_LOG_ROOT.exists() and list(NEW_LOG_ROOT.iterdir()):
            print("  ⚠️  目标已存在,跳过迁移")
            skipped.append("log")
        else:
            try:
                NEW_LOG_ROOT.mkdir(parents=True, exist_ok=True)
                for item in OLD_LOG.iterdir():
                    dest = NEW_LOG_ROOT / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)
                print("  ✅ 迁移完成")
                migrated.append("log")
            except Exception as e:
                print(f"  ❌ 迁移失败: {e}")
                errors.append(("log", str(e)))
        print()

    # 4. 迁移 xiaomiaoAgent/.nanobot/workspace
    if OLD_NANOBOT_WORKSPACE.exists():
        print(f"📦 迁移 .nanobot/workspace...")
        print(f"  从: {OLD_NANOBOT_WORKSPACE}")
        print(f"  到: {NEW_NANOBOT_WORKSPACE}")

        if NEW_NANOBOT_WORKSPACE.exists():
            print("  ⚠️  目标已存在,跳过迁移")
            skipped.append(".nanobot/workspace")
        else:
            try:
                NEW_NANOBOT_WORKSPACE.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(OLD_NANOBOT_WORKSPACE, NEW_NANOBOT_WORKSPACE)
                print("  ✅ 迁移完成")
                migrated.append(".nanobot/workspace")
            except Exception as e:
                print(f"  ❌ 迁移失败: {e}")
                errors.append((".nanobot/workspace", str(e)))
        print()

    # 5. 创建其他缓存目录
    print("📁 创建其他缓存目录...")
    cache_dirs = [
        NEW_CACHE / "xiaomiao" / "bridge_events",
        NEW_CACHE / "agent" / "nanobot" / "sessions",
        NEW_CACHE / "agent" / "nanobot" / "memory",
        NEW_CACHE / "agent" / "tools",
        NEW_CACHE / "agent" / "skills",
        NEW_CACHE / "tool" / "embeddings",
        NEW_CACHE / "tool" / "huggingface",
        NEW_CACHE / "tool" / "models",
        NEW_CACHE / "tool" / "tts",
        NEW_CACHE / "tool" / "tmp",
        NEW_CACHE / "bot",
        NEW_CACHE / "logs" / "xiaomiao",
        NEW_CACHE / "logs" / "agent",
        NEW_CACHE / "logs" / "tool",
    ]

    for cache_dir in cache_dirs:
        cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ 已创建 {len(cache_dirs)} 个目录")
    print()

    # 6. 总结
    print("=" * 70)
    print("🎉 迁移完成!")
    print("=" * 70)
    print()

    if migrated:
        print("✅ 已迁移:")
        for item in migrated:
            print(f"  - {item}")
        print()

    if skipped:
        print("⚠️  已跳过 (目标已存在):")
        for item in skipped:
            print(f"  - {item}")
        print()

    if errors:
        print("❌ 迁移失败:")
        for item, error in errors:
            print(f"  - {item}: {error}")
        print()

    print("📝 后续步骤:")
    print("  1. 重启项目,确认一切正常")
    print("  2. 验证数据完整性")
    print("  3. 可选: 删除旧目录 (确认无误后)")
    if OLD_XIAOMIAO_RUNTIME.exists():
        print(f"     rm -rf {OLD_XIAOMIAO_RUNTIME}")
    if OLD_WORKSPACE.exists():
        print(f"     rm -rf {OLD_WORKSPACE}")
    if OLD_LOG.exists():
        print(f"     rm -rf {OLD_LOG}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ 迁移失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
