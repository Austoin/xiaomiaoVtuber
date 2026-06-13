#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复文档中的硬编码路径
将 F:\\xiaomiaoVirtual 和 f:\\xiaomiaoVirtual 替换为 <项目根目录>
"""

import os
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

# 路径替换映射
PATH_REPLACEMENTS = [
    (r'F:\\xiaomiaoVirtual', r'<项目根目录>'),
    (r'f:\\xiaomiaoVirtual', r'<项目根目录>'),
    (r'F:/xiaomiaoVirtual', r'<项目根目录>'),
    (r'f:/xiaomiaoVirtual', r'<项目根目录>'),
]

def fix_paths_in_file(file_path):
    """修复单个文件中的路径"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = 0

        # 应用所有替换规则
        for pattern, replacement in PATH_REPLACEMENTS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes_made += content.count(pattern.replace('\\\\', '\\'))
                content = new_content

        # 只有内容变化时才写入
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made

        return 0

    except Exception as e:
        print(f"[!] Failed to process {file_path}: {e}")
        return 0

def main():
    """批量处理所有文档"""
    print(f"[*] Scanning docs directory: {DOCS_DIR}")

    total_files = 0
    total_changes = 0
    modified_files = []

    # 遍历所有 Markdown 文件
    for md_file in DOCS_DIR.rglob("*.md"):
        changes = fix_paths_in_file(md_file)
        if changes > 0:
            total_files += 1
            total_changes += changes
            modified_files.append((md_file.relative_to(DOCS_DIR), changes))
            print(f"[+] {md_file.relative_to(DOCS_DIR)}: {changes} replacements")

    print("\n" + "="*60)
    print(f"Summary:")
    print(f"   - Modified files: {total_files}")
    print(f"   - Total replacements: {total_changes}")
    print("="*60)

    if modified_files:
        print("\nModified files:")
        for file_path, count in modified_files:
            print(f"  - {file_path} ({count} changes)")

if __name__ == "__main__":
    main()
