#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重命名中文文档为英文"""

import os
import sys
from pathlib import Path

# 确保 UTF-8 编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

PROJECT_ROOT = Path(__file__).parent.parent

# 重命名映射 - 使用原始字符串
RENAMES = [
    (r"docs\00-quick-start\运行与配置.md", r"docs\00-quick-start\run-and-config.md"),
    (r"docs\03-subsystems\xiaomiaobot\操作文档.md", r"docs\03-subsystems\xiaomiaobot\operation-guide.md"),
]

def main():
    for old_path, new_path in RENAMES:
        old_file = PROJECT_ROOT / old_path
        new_file = PROJECT_ROOT / new_path

        if old_file.exists():
            if new_file.exists():
                print(f"[!] Target already exists, skipping: {new_path}")
            else:
                old_file.rename(new_file)
                print(f"[+] Renamed: {old_path} -> {new_path}")
        else:
            print(f"[!] Source not found: {old_path}")

if __name__ == "__main__":
    main()
