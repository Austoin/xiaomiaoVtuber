#!/usr/bin/env python3
"""
缓存目录迁移脚本

将旧的 runtime/ 和 workspace/ 目录数据迁移到新的 .cache/ 目录
"""

import shutil
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
OLD_RUNTIME = PROJECT_ROOT / "xiaomiao" / "runtime"
OLD_WORKSPACE = PROJECT_ROOT / "workspace"
NEW_CACHE = PROJECT_ROOT / ".cache"


def migrate():
    """执行迁移"""
    print("🚀 开始迁移缓存数据...")
    print(f"项目根目录: {PROJECT_ROOT}")
    print()

    migrated = []
    skipped = []

    # 1. 迁移 xiaomiao/runtime/ → .cache/xiaomiao/runtime/
    if OLD_RUNTIME.exists():
        new_runtime = NEW_CACHE / "xiaomiao" / "runtime"
        print(f"📦 迁移 runtime 数据...")
        print(f"  从: {OLD_RUNTIME}")
        print(f"  到: {new_runtime}")

        if new_runtime.exists():
            print("  ⚠️  目标已存在,跳过迁移")
            skipped.append("runtime")
        else:
            new_runtime.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(OLD_RUNTIME, new_runtime)
            print("  ✅ 迁移完成")
            migrated.append("runtime")
        print()

    # 2. 迁移 workspace/ → .cache/xiaomiao/qq_workspace/
    if OLD_WORKSPACE.exists():
        new_workspace = NEW_CACHE / "xiaomiao" / "qq_workspace"
        print(f"📦 迁移 workspace 数据...")
        print(f"  从: {OLD_WORKSPACE}")
        print(f"  到: {new_workspace}")

        if new_workspace.exists():
            print("  ⚠️  目标已存在,跳过迁移")
            skipped.append("workspace")
        else:
            new_workspace.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(OLD_WORKSPACE, new_workspace)
            print("  ✅ 迁移完成")
            migrated.append("workspace")
        print()

    # 3. 创建其他缓存目录
    print("📁 创建其他缓存目录...")
    cache_dirs = [
        NEW_CACHE / "xiaomiao" / "bridge_events",
        NEW_CACHE / "agent" / "sessions",
        NEW_CACHE / "agent" / "memory",
        NEW_CACHE / "agent" / "tools",
        NEW_CACHE / "tool" / "embeddings",
        NEW_CACHE / "tool" / "models",
    ]

    for cache_dir in cache_dirs:
        cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {cache_dir.relative_to(PROJECT_ROOT)}")
    print()

    # 4. 总结
    print("=" * 60)
    print("🎉 迁移完成!")
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

    print("📝 后续步骤:")
    print("  1. 重启项目,确认一切正常")
    print("  2. 验证数据完整性")
    print("  3. 可选: 删除旧的 xiaomiao/runtime/ 和 workspace/")
    print(f"     rm -rf {OLD_RUNTIME}")
    print(f"     rm -rf {OLD_WORKSPACE}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ 迁移失败: {e}", file=sys.stderr)
        sys.exit(1)
