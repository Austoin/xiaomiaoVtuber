import os
import json
from pathlib import Path

# 分析项目结构
structure = {
    'xiaomiao': {
        'modules': [],
        'files': []
    },
    'xiaomiaoAgent': {
        'modules': [],
        'files': []
    },
    'xiaomiaobot': {
        'modules': [],
        'files': []
    }
}

# 扫描 xiaomiao
for f in Path('xiaomiao').glob('*.py'):
    structure['xiaomiao']['files'].append(f.name)

# 扫描 xiaomiaoAgent
for f in Path('xiaomiaoAgent').rglob('*.py'):
    if '.nanobot' not in str(f):
        structure['xiaomiaoAgent']['files'].append(str(f.relative_to('xiaomiaoAgent')))

# 扫描 xiaomiaobot
for f in Path('xiaomiaobot').glob('apps/*/package.json'):
    structure['xiaomiaobot']['modules'].append(str(f.parent.name))

print(json.dumps(structure, indent=2, ensure_ascii=False))
