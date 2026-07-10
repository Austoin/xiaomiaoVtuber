"""
xiaomiao 模块缓存配置

从全局缓存配置导入,保持向后兼容
"""

import sys
import importlib.util
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 直接加载项目根目录下的 cache_config.py (避免循环导入)
global_cache_path = PROJECT_ROOT / "cache_config.py"
spec = importlib.util.spec_from_file_location("global_cache_config", global_cache_path)
global_cache = importlib.util.module_from_spec(spec)
spec.loader.exec_module(global_cache)

# 导入全局配置
CACHE_ROOT = global_cache.CACHE_ROOT
RUNTIME_DIR = global_cache.XIAOMIAO_RUNTIME
SUPER_USER_FILE = global_cache.SUPER_USER_FILE
MANAGE_USER_FILE = global_cache.MANAGE_USER_FILE
SISTERS_FILE = global_cache.SISTERS_FILE
JHQ_FILE = global_cache.JHQ_FILE
PROGRAMMERS_FILE = global_cache.PROGRAMMERS_FILE
TIMING_MESSAGE_FILE = global_cache.TIMING_MESSAGE_FILE
BLACKLIST_FILE = global_cache.BLACKLIST_FILE
QQ_WORKSPACE_CACHE = global_cache.QQ_WORKSPACE
BRIDGE_EVENTS_CACHE = global_cache.BRIDGE_EVENTS_CACHE
QQ_TMP = global_cache.QQ_TMP
NANOBOT_CACHE = global_cache.NANOBOT_CACHE
NANOBOT_CONFIG_FILE = global_cache.NANOBOT_CONFIG_FILE
NANOBOT_WORKSPACE = global_cache.NANOBOT_WORKSPACE
NANOBOT_BRIDGE = global_cache.NANOBOT_BRIDGE
NANOBOT_CLI_HISTORY = global_cache.NANOBOT_CLI_HISTORY
ensure_cache_dirs = global_cache.ensure_all_cache_dirs
get_cache_path = global_cache.get_cache_path

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
    "QQ_TMP",
    "NANOBOT_CACHE",
    "NANOBOT_CONFIG_FILE",
    "NANOBOT_WORKSPACE",
    "NANOBOT_BRIDGE",
    "NANOBOT_CLI_HISTORY",
    "ensure_cache_dirs",
    "get_cache_path",
]

