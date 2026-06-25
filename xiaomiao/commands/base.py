"""
命令系统基类和装饰器

这是 xiaomiao 重构的第一步:实现命令系统基础设施
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Any, Awaitable
from enum import Enum


class PermissionLevel(Enum):
    """权限级别"""
    PUBLIC = 0        # 所有人
    USER = 1          # 注册用户
    MANAGE = 2        # 管理员
    SUPER = 3         # 超级管理员
    ROOT = 4          # ROOT


@dataclass
class CommandContext:
    """
    命令上下文

    包含执行命令所需的所有信息
    """
    # 用户信息
    user_id: int
    user_name: str

    # 消息信息
    message_id: int
    message_text: str
    chat_id: str
    chat_type: str  # 'group' | 'private'

    # 参数
    args: List[str] = field(default_factory=list)
    raw_args: str = ""

    # 引用消息
    reply_to: Optional[Any] = None

    # At 列表
    at_users: List[int] = field(default_factory=list)

    # 图片列表
    images: List[str] = field(default_factory=list)

    # 扩展数据
    extra: dict = field(default_factory=dict)


@dataclass
class CommandResult:
    """
    命令执行结果

    统一的命令返回格式
    """
    success: bool
    message: str = ""
    data: Any = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, message: str = "", data: Any = None) -> "CommandResult":
        """创建成功结果"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, error: str) -> "CommandResult":
        """创建失败结果"""
        return cls(success=False, error=error)


class Command:
    """
    命令类

    封装命令的元数据和执行逻辑
    """

    def __init__(
        self,
        name: str,
        handler: Callable[[CommandContext], Awaitable[CommandResult]],
        description: str = "",
        aliases: List[str] = None,
        permission: PermissionLevel = PermissionLevel.PUBLIC,
        cooldown: int = 0,  # 冷却时间(秒)
        usage: str = "",
        examples: List[str] = None,
    ):
        self.name = name
        self.handler = handler
        self.description = description
        self.aliases = aliases or []
        self.permission = permission
        self.cooldown = cooldown
        self.usage = usage or f"- {name}"
        self.examples = examples or []

    async def execute(self, ctx: CommandContext) -> CommandResult:
        """
        执行命令

        Args:
            ctx: 命令上下文

        Returns:
            命令执行结果
        """
        try:
            return await self.handler(ctx)
        except Exception as e:
            return CommandResult.fail(f"命令执行失败: {str(e)}")

    def matches(self, input_name: str) -> bool:
        """
        检查是否匹配命令名

        Args:
            input_name: 输入的命令名

        Returns:
            是否匹配
        """
        return input_name == self.name or input_name in self.aliases


def command(
    name: str,
    description: str = "",
    aliases: List[str] = None,
    permission: PermissionLevel = PermissionLevel.PUBLIC,
    cooldown: int = 0,
    usage: str = "",
    examples: List[str] = None,
    auto_register: bool = True,
):
    """
    命令装饰器

    使用示例:
        @command(name="ping", description="测试在线")
        async def cmd_ping(ctx: CommandContext) -> CommandResult:
            return CommandResult.ok("pong!")

    Args:
        name: 命令名
        description: 命令描述
        aliases: 命令别名
        permission: 权限要求
        cooldown: 冷却时间(秒)
        usage: 使用说明
        examples: 使用示例
        auto_register: 是否自动注册到全局注册表
    """
    def decorator(func: Callable[[CommandContext], Awaitable[CommandResult]]):
        cmd = Command(
            name=name,
            handler=func,
            description=description,
            aliases=aliases,
            permission=permission,
            cooldown=cooldown,
            usage=usage,
            examples=examples,
        )

        # 自动注册
        if auto_register:
            from .registry import command_registry
            command_registry.register(cmd)

        # 保留原函数
        func._command = cmd
        return func

    return decorator


# 便捷装饰器

def public_command(name: str, **kwargs):
    """公开命令装饰器"""
    return command(name=name, permission=PermissionLevel.PUBLIC, **kwargs)


def manage_command(name: str, **kwargs):
    """管理命令装饰器"""
    return command(name=name, permission=PermissionLevel.MANAGE, **kwargs)


def admin_command(name: str, **kwargs):
    """管理员命令装饰器"""
    return command(name=name, permission=PermissionLevel.SUPER, **kwargs)


def root_command(name: str, **kwargs):
    """ROOT 命令装饰器"""
    return command(name=name, permission=PermissionLevel.ROOT, **kwargs)
