"""
缓存目录管理

统一管理项目中所有缓存和运行时数据的存储位置
"""

from pathlib import Path
import os

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 统一缓存目录
CACHE_ROOT = PROJECT_ROOT / ".cache"

# 子缓存目录
XIAOMIAO_CACHE = CACHE_ROOT / "xiaomiao"
AGENT_CACHE = CACHE_ROOT / "agent"
BOT_CACHE = CACHE_ROOT / "bot"
TOOL_CACHE = CACHE_ROOT / "tool"

# xiaomiao 相关缓存
RUNTIME_DIR = XIAOMIAO_CACHE / "runtime"
QQ_WORKSPACE_CACHE = XIAOMIAO_CACHE / "qq_workspace"
BRIDGE_EVENTS_CACHE = XIAOMIAO_CACHE / "bridge_events"

# 用户配置文件 (runtime 目录下)
SUPER_USER_FILE = RUNTIME_DIR / "Super_User.ini"
MANAGE_USER_FILE = RUNTIME_DIR / "Manage_User.ini"
SISTERS_FILE = RUNTIME_DIR / "sisters.ini"
JHQ_FILE = RUNTIME_DIR / "jhq.ini"
PROGRAMMERS_FILE = RUNTIME_DIR / "programmers.ini"
TIMING_MESSAGE_FILE = RUNTIME_DIR / "timing_message.ini"
BLACKLIST_FILE = RUNTIME_DIR / "blacklist.sr"

# Agent 相关缓存
AGENT_SESSION_CACHE = AGENT_CACHE / "sessions"
AGENT_MEMORY_CACHE = AGENT_CACHE / "memory"
AGENT_TOOLS_CACHE = AGENT_CACHE / "tools"

# 工具缓存
EMBEDDING_CACHE = TOOL_CACHE / "embeddings"
MODEL_CACHE = TOOL_CACHE / "models"


def ensure_cache_dirs():
    """确保所有缓存目录存在"""
    dirs = [
        CACHE_ROOT,
        XIAOMIAO_CACHE,
        AGENT_CACHE,
        BOT_CACHE,
        TOOL_CACHE,
        RUNTIME_DIR,
        QQ_WORKSPACE_CACHE,
        BRIDGE_EVENTS_CACHE,
        AGENT_SESSION_CACHE,
        AGENT_MEMORY_CACHE,
        AGENT_TOOLS_CACHE,
        EMBEDDING_CACHE,
        MODEL_CACHE,
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_cache_path(category: str, *parts: str) -> Path:
    """
    获取缓存路径

    Args:
        category: 类别 (xiaomiao, agent, bot, tool)
        *parts: 路径部分

    Returns:
        完整的缓存路径
    """
    category_map = {
        "xiaomiao": XIAOMIAO_CACHE,
        "agent": AGENT_CACHE,
        "bot": BOT_CACHE,
        "tool": TOOL_CACHE,
    }

    base = category_map.get(category, CACHE_ROOT)
    cache_path = base.joinpath(*parts)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    return cache_path


# 向后兼容: 如果环境变量指定了缓存目录,使用环境变量
if "XIAOMIAO_CACHE_ROOT" in os.environ:
    CACHE_ROOT = Path(os.environ["XIAOMIAO_CACHE_ROOT"])
    # 重新计算所有子目录
    XIAOMIAO_CACHE = CACHE_ROOT / "xiaomiao"
    AGENT_CACHE = CACHE_ROOT / "agent"
    BOT_CACHE = CACHE_ROOT / "bot"
    TOOL_CACHE = CACHE_ROOT / "tool"
    RUNTIME_DIR = XIAOMIAO_CACHE / "runtime"
    QQ_WORKSPACE_CACHE = XIAOMIAO_CACHE / "qq_workspace"
    BRIDGE_EVENTS_CACHE = XIAOMIAO_CACHE / "bridge_events"
