"""
命令注册表

管理所有已注册的命令,提供查找和权限验证功能
"""

import logging
from typing import Dict, List, Optional
from .base import Command, PermissionLevel, CommandContext

logger = logging.getLogger(__name__)


class CommandRegistry:
    """命令注册表"""

    def __init__(self):
        self._commands: Dict[str, Command] = {}
        self._last_execution: Dict[str, float] = {}  # 冷却管理

    def register(self, command: Command) -> None:
        """
        注册命令

        Args:
            command: 命令对象
        """
        if command.name in self._commands:
            logger.warning(f"命令 {command.name} 已存在,将被覆盖")

        self._commands[command.name] = command
        logger.info(f"注册命令: {command.name}")

    def unregister(self, name: str) -> None:
        """
        注销命令

        Args:
            name: 命令名
        """
        if name in self._commands:
            del self._commands[name]
            logger.info(f"注销命令: {name}")

    def get(self, name: str) -> Optional[Command]:
        """
        获取命令

        Args:
            name: 命令名或别名

        Returns:
            命令对象,如果不存在则返回 None
        """
        # 精确匹配
        if name in self._commands:
            return self._commands[name]

        # 别名匹配
        for cmd in self._commands.values():
            if cmd.matches(name):
                return cmd

        return None

    def list_commands(
        self,
        permission: Optional[PermissionLevel] = None
    ) -> List[Command]:
        """
        列出命令

        Args:
            permission: 权限级别,只返回该权限可用的命令

        Returns:
            命令列表
        """
        commands = list(self._commands.values())

        if permission is not None:
            commands = [
                cmd for cmd in commands
                if cmd.permission.value <= permission.value
            ]

        return sorted(commands, key=lambda c: c.name)

    def get_user_permission(self, user_id: int) -> PermissionLevel:
        """
        获取用户权限级别

        Args:
            user_id: 用户 ID

        Returns:
            权限级别
        """
        # TODO: 从 permission_service 获取真实权限
        # 目前返回默认权限
        try:
            from ..services.permission_service import permission_service
            return permission_service.get_user_level(user_id)
        except Exception:
            return PermissionLevel.PUBLIC

    def check_cooldown(
        self,
        command: Command,
        user_id: int
    ) -> tuple[bool, int]:
        """
        检查冷却时间

        Args:
            command: 命令
            user_id: 用户 ID

        Returns:
            (是否可执行, 剩余冷却秒数)
        """
        if command.cooldown <= 0:
            return True, 0

        import time
        key = f"{command.name}:{user_id}"
        now = time.time()

        if key in self._last_execution:
            elapsed = now - self._last_execution[key]
            remaining = command.cooldown - elapsed

            if remaining > 0:
                return False, int(remaining)

        # 更新执行时间
        self._last_execution[key] = now
        return True, 0

    async def can_execute(
        self,
        command: Command,
        ctx: CommandContext
    ) -> tuple[bool, Optional[str]]:
        """
        检查是否可以执行命令

        Args:
            command: 命令
            ctx: 命令上下文

        Returns:
            (是否可执行, 错误信息)
        """
        # 权限检查
        user_permission = self.get_user_permission(ctx.user_id)

        if command.permission.value > user_permission.value:
            return False, "❌ 权限不足"

        # 冷却检查
        can_exec, remaining = self.check_cooldown(command, ctx.user_id)
        if not can_exec:
            return False, f"⏰ 冷却中,请等待 {remaining} 秒"

        return True, None

    def get_help_text(
        self,
        user_id: int,
        category: Optional[str] = None
    ) -> str:
        """
        生成帮助文本

        Args:
            user_id: 用户 ID
            category: 命令分类(可选)

        Returns:
            帮助文本
        """
        user_perm = self.get_user_permission(user_id)
        commands = self.list_commands(permission=user_perm)

        if not commands:
            return "暂无可用命令"

        lines = ["📖 可用命令列表:\n"]

        for cmd in commands:
            lines.append(f"  {cmd.usage}")
            if cmd.description:
                lines.append(f"    {cmd.description}")
            if cmd.aliases:
                lines.append(f"    别名: {', '.join(cmd.aliases)}")
            lines.append("")  # 空行

        return "\n".join(lines)


# 全局命令注册表
command_registry = CommandRegistry()
