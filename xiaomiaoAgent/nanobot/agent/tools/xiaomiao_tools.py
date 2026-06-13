"""
nanobot 工具注册

将 tool/xiaomiao 下的专属工具注册到 nanobot 工具系统。
这个文件会被 xiaomiaoAgent 在启动时自动加载。
"""

from pathlib import Path
import sys

# 添加 tool 目录到 Python path
TOOL_DIR = Path(__file__).parents[2] / "tool"
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))


def register_xiaomiao_tools():
    """注册 xiaomiao 专属工具到 nanobot"""
    try:
        from tool.xiaomiao.last30days import Last30DaysTool

        # 检查工具是否可用
        available, msg = Last30DaysTool.check_available()
        if available:
            # 注册到工具系统
            # 这里会被 nanobot 的工具加载器自动发现
            return True
        else:
            import logging
            logging.warning(f"Last30Days 工具不可用: {msg}")
            return False
    except Exception as e:
        import logging
        logging.warning(f"注册 xiaomiao 工具失败: {e}")
        return False


# 自动注册
register_xiaomiao_tools()
