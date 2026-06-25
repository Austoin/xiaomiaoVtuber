"""
xiaomiao 模块缓存配置

从全局缓存配置导入,保持向后兼容
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 从全局配置导入
from cache_config import (
    CACHE_ROOT,
    XIAOMIAO_RUNTIME as RUNTIME_DIR,
    SUPER_USER_FILE,
    MANAGE_USER_FILE,
    SISTERS_FILE,
    JHQ_FILE,
    PROGRAMMERS_FILE,
    TIMING_MESSAGE_FILE,
    BLACKLIST_FILE,
    QQ_WORKSPACE as QQ_WORKSPACE_CACHE,
    BRIDGE_EVENTS_CACHE,
    ensure_all_cache_dirs as ensure_cache_dirs,
    get_cache_path,
)

__all__ = [
    "CACHE_ROOT",
    "RUNTIME_DIR",
    "SUPER_USER_FILE",
    "MANAGE_USER_FILE",
    "SISTERS_FILE",
    "JHQ_FILE",
    "PROGRAMMERS_FILE",
    "TIMING_MESSAGE_FILE",
    "BLACKLIST_FILE",
    "QQ_WORKSPACE_CACHE",
    "BRIDGE_EVENTS_CACHE",
    "ensure_cache_dirs",
    "get_cache_path",
]

