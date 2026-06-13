#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新文档中的链接引用"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

# 链接替换规则
LINK_REPLACEMENTS = [
    (r'操作文档\.md', 'operation-guide.md'),
    (r'运行与配置\.md', 'run-and-config.md'),
]

def fix_links_in_file(file_path):
    """修复单个文件中的链接"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = 0

        for pattern, replacement in LINK_REPLACEMENTS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                count = len(re.findall(pattern, content))
                changes_made += count
                content = new_content

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made

        return 0

    except Exception as e:
        print(f"[!] Failed: {file_path}: {e}")
        return 0

def main():
    print(f"[*] Updating doc links in: {DOCS_DIR}")

    total_files = 0
    total_changes = 0

    for md_file in DOCS_DIR.rglob("*.md"):
        changes = fix_links_in_file(md_file)
        if changes > 0:
            total_files += 1
            total_changes += changes
            print(f"[+] {md_file.relative_to(DOCS_DIR)}: {changes} links updated")

    print(f"\n[*] Summary: {total_files} files, {total_changes} links updated")

if __name__ == "__main__":
    main()
