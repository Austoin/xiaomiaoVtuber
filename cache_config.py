"""
全局缓存配置

统一管理整个项目的所有缓存和运行时数据
包括 QQ 端和 xiaomiaoAgent
"""

import os
from pathlib import Path

# ==================== 项目根目录 ====================
# cache_config.py 在项目根目录下
PROJECT_ROOT = Path(__file__).resolve().parent

# ==================== 统一缓存根目录 ====================
CACHE_ROOT = PROJECT_ROOT / ".cache"

# 支持环境变量覆盖
if "XIAOMIAO_CACHE_ROOT" in os.environ:
    CACHE_ROOT = Path(os.environ["XIAOMIAO_CACHE_ROOT"])

# ==================== 一级缓存目录 ====================
XIAOMIAO_CACHE = CACHE_ROOT / "xiaomiao"
AGENT_CACHE = CACHE_ROOT / "agent"

# ==================== xiaomiao 缓存 ====================
# 运行时配置
XIAOMIAO_RUNTIME = XIAOMIAO_CACHE / "runtime"
SUPER_USER_FILE = XIAOMIAO_RUNTIME / "Super_User.ini"
MANAGE_USER_FILE = XIAOMIAO_RUNTIME / "Manage_User.ini"
SISTERS_FILE = XIAOMIAO_RUNTIME / "sisters.ini"
JHQ_FILE = XIAOMIAO_RUNTIME / "jhq.ini"
PROGRAMMERS_FILE = XIAOMIAO_RUNTIME / "programmers.ini"
TIMING_MESSAGE_FILE = XIAOMIAO_RUNTIME / "timing_message.ini"
BLACKLIST_FILE = XIAOMIAO_RUNTIME / "blacklist.sr"

# QQ 资源
QQ_WORKSPACE = XIAOMIAO_CACHE / "qq_workspace"
QQ_DOWNLOADS = QQ_WORKSPACE / "downloads"
QQ_ARTIFACTS = QQ_WORKSPACE / "artifacts"
QQ_TMP = QQ_WORKSPACE / "tmp"

# ==================== Agent 缓存 ====================
# nanobot 缓存
NANOBOT_CACHE = AGENT_CACHE / "nanobot"
NANOBOT_CONFIG_FILE = NANOBOT_CACHE / "config.json"
NANOBOT_WORKSPACE = NANOBOT_CACHE / "workspace"
NANOBOT_SESSIONS = NANOBOT_CACHE / "sessions"
NANOBOT_MEMORY = NANOBOT_CACHE / "memory"
NANOBOT_HISTORY = NANOBOT_CACHE / "history"
NANOBOT_CLI_HISTORY = NANOBOT_HISTORY / "cli_history"
NANOBOT_MEDIA = NANOBOT_CACHE / "media"
NANOBOT_CRON = NANOBOT_CACHE / "cron"

# ==================== 日志目录 ====================
LOG_ROOT = CACHE_ROOT / "logs"
XIAOMIAO_LOG = LOG_ROOT / "xiaomiao"
AGENT_LOG = LOG_ROOT / "agent"


def ensure_all_cache_dirs():
    """确保所有缓存目录存在"""
    dirs = [
        # 根目录
        CACHE_ROOT,
        XIAOMIAO_CACHE,
        AGENT_CACHE,

        # xiaomiao
        XIAOMIAO_RUNTIME,
        QQ_WORKSPACE,
        QQ_DOWNLOADS,
        QQ_ARTIFACTS,
        QQ_TMP,

        # agent
        NANOBOT_CACHE,
        NANOBOT_CONFIG_FILE.parent,
        NANOBOT_WORKSPACE,
        NANOBOT_SESSIONS,
        NANOBOT_MEMORY,
        NANOBOT_HISTORY,
        NANOBOT_MEDIA,
        NANOBOT_CRON,

        # logs
        LOG_ROOT,
        XIAOMIAO_LOG,
        AGENT_LOG,
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_cache_path(category: str, *parts: str) -> Path:
    """
    获取缓存路径

    Args:
        category: 类别 (xiaomiao, agent, log)
        *parts: 路径部分

    Returns:
        完整的缓存路径
    """
    category_map = {
        "xiaomiao": XIAOMIAO_CACHE,
        "agent": AGENT_CACHE,
        "log": LOG_ROOT,
    }

    base = category_map.get(category, CACHE_ROOT)
    cache_path = base.joinpath(*parts)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    return cache_path


# 自动创建基本目录
ensure_all_cache_dirs()


# ==================== 导出的路径 ====================
__all__ = [
    # 根目录
    "PROJECT_ROOT",
    "CACHE_ROOT",

    # 一级目录
    "XIAOMIAO_CACHE",
    "AGENT_CACHE",

    # xiaomiao
    "XIAOMIAO_RUNTIME",
    "SUPER_USER_FILE",
    "MANAGE_USER_FILE",
    "SISTERS_FILE",
    "JHQ_FILE",
    "PROGRAMMERS_FILE",
    "TIMING_MESSAGE_FILE",
    "BLACKLIST_FILE",
    "QQ_WORKSPACE",
    "QQ_DOWNLOADS",
    "QQ_ARTIFACTS",
    "QQ_TMP",

    # agent
    "NANOBOT_CACHE",
    "NANOBOT_CONFIG_FILE",
    "NANOBOT_WORKSPACE",
    "NANOBOT_SESSIONS",
    "NANOBOT_MEMORY",
    "NANOBOT_HISTORY",
    "NANOBOT_CLI_HISTORY",
    "NANOBOT_MEDIA",
    "NANOBOT_CRON",

    # logs
    "LOG_ROOT",
    "XIAOMIAO_LOG",
    "AGENT_LOG",

    # 函数
    "ensure_all_cache_dirs",
    "get_cache_path",
]
