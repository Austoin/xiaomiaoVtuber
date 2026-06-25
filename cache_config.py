"""
全局缓存配置

统一管理整个项目的所有缓存和运行时数据
包括 xiaomiao, xiaomiaoAgent, tool 等所有模块
"""

from pathlib import Path
import os

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
BOT_CACHE = CACHE_ROOT / "bot"
TOOL_CACHE = CACHE_ROOT / "tool"

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

# Bridge 事件
BRIDGE_EVENTS_CACHE = XIAOMIAO_CACHE / "bridge_events"
BRIDGE_EVENTS_FILE = BRIDGE_EVENTS_CACHE / "bridge_events.jsonl"

# ==================== Agent 缓存 ====================
# nanobot 缓存
NANOBOT_CACHE = AGENT_CACHE / "nanobot"
NANOBOT_WORKSPACE = NANOBOT_CACHE / "workspace"
NANOBOT_SESSIONS = NANOBOT_CACHE / "sessions"
NANOBOT_MEMORY = NANOBOT_CACHE / "memory"

# Agent 工具缓存
AGENT_TOOLS_CACHE = AGENT_CACHE / "tools"
AGENT_SKILLS_CACHE = AGENT_CACHE / "skills"

# ==================== Tool 缓存 ====================
# 嵌入向量缓存
EMBEDDING_CACHE = TOOL_CACHE / "embeddings"
HF_CACHE = TOOL_CACHE / "huggingface"

# 模型缓存
MODEL_CACHE = TOOL_CACHE / "models"

# TTS 缓存
TTS_CACHE = TOOL_CACHE / "tts"

# 临时文件
TOOL_TMP = TOOL_CACHE / "tmp"

# ==================== 日志目录 ====================
LOG_ROOT = CACHE_ROOT / "logs"
XIAOMIAO_LOG = LOG_ROOT / "xiaomiao"
AGENT_LOG = LOG_ROOT / "agent"
TOOL_LOG = LOG_ROOT / "tool"

# ==================== 向后兼容映射 ====================
# 旧路径 -> 新路径
LEGACY_PATHS = {
    "xiaomiao/runtime": XIAOMIAO_RUNTIME,
    "workspace": QQ_WORKSPACE,
    "log": LOG_ROOT,
    ".nanobot/workspace": NANOBOT_WORKSPACE,
}


def ensure_all_cache_dirs():
    """确保所有缓存目录存在"""
    dirs = [
        # 根目录
        CACHE_ROOT,
        XIAOMIAO_CACHE,
        AGENT_CACHE,
        BOT_CACHE,
        TOOL_CACHE,

        # xiaomiao
        XIAOMIAO_RUNTIME,
        QQ_WORKSPACE,
        QQ_DOWNLOADS,
        QQ_ARTIFACTS,
        QQ_TMP,
        BRIDGE_EVENTS_CACHE,

        # agent
        NANOBOT_CACHE,
        NANOBOT_WORKSPACE,
        NANOBOT_SESSIONS,
        NANOBOT_MEMORY,
        AGENT_TOOLS_CACHE,
        AGENT_SKILLS_CACHE,

        # tool
        EMBEDDING_CACHE,
        HF_CACHE,
        MODEL_CACHE,
        TTS_CACHE,
        TOOL_TMP,

        # logs
        LOG_ROOT,
        XIAOMIAO_LOG,
        AGENT_LOG,
        TOOL_LOG,
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_cache_path(category: str, *parts: str) -> Path:
    """
    获取缓存路径

    Args:
        category: 类别 (xiaomiao, agent, bot, tool, log)
        *parts: 路径部分

    Returns:
        完整的缓存路径
    """
    category_map = {
        "xiaomiao": XIAOMIAO_CACHE,
        "agent": AGENT_CACHE,
        "bot": BOT_CACHE,
        "tool": TOOL_CACHE,
        "log": LOG_ROOT,
    }

    base = category_map.get(category, CACHE_ROOT)
    cache_path = base.joinpath(*parts)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    return cache_path


def get_legacy_path(old_path: str) -> Path:
    """
    获取旧路径对应的新路径

    Args:
        old_path: 旧路径 (相对于项目根目录)

    Returns:
        新的缓存路径
    """
    return LEGACY_PATHS.get(old_path, PROJECT_ROOT / old_path)


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
    "BOT_CACHE",
    "TOOL_CACHE",

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
    "BRIDGE_EVENTS_CACHE",
    "BRIDGE_EVENTS_FILE",

    # agent
    "NANOBOT_CACHE",
    "NANOBOT_WORKSPACE",
    "NANOBOT_SESSIONS",
    "NANOBOT_MEMORY",
    "AGENT_TOOLS_CACHE",
    "AGENT_SKILLS_CACHE",

    # tool
    "EMBEDDING_CACHE",
    "HF_CACHE",
    "MODEL_CACHE",
    "TTS_CACHE",
    "TOOL_TMP",

    # logs
    "LOG_ROOT",
    "XIAOMIAO_LOG",
    "AGENT_LOG",
    "TOOL_LOG",

    # 函数
    "ensure_all_cache_dirs",
    "get_cache_path",
    "get_legacy_path",
]
