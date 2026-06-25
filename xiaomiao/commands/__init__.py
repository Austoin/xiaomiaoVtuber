"""
命令系统初始化

导入所有命令模块,完成自动注册
"""

# 导入基础设施
from .base import (
    Command,
    CommandContext,
    CommandResult,
    PermissionLevel,
    command,
    public_command,
    manage_command,
    admin_command,
    root_command,
)
from .registry import command_registry

# 导入命令模块(导入时会自动注册)
from . import basic  # noqa: F401

# TODO: 逐步添加其他命令模块
# from . import ai  # noqa: F401
# from . import agent  # noqa: F401
# from . import image  # noqa: F401
# from . import persona  # noqa: F401
# from . import admin  # noqa: F401
# from . import system  # noqa: F401


__all__ = [
    # 基础设施
    'Command',
    'CommandContext',
    'CommandResult',
    'PermissionLevel',
    'command',
    'public_command',
    'manage_command',
    'admin_command',
    'root_command',
    'command_registry',

    # 命令模块
    'basic',
]


def get_registered_commands_count() -> int:
    """获取已注册命令数量"""
    return len(command_registry._commands)


def list_all_commands() -> list[str]:
    """列出所有已注册命令名"""
    return sorted(command_registry._commands.keys())
