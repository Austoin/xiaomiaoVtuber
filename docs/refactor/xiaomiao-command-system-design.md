# xiaomiao 命令系统设计

## 目标

设计一个灵活、可扩展、易测试的命令系统,替代当前 main.py 中的命令处理逻辑。

## 核心概念

### 1. 命令 (Command)

命令是用户输入到机器人执行的映射。每个命令:
- 有唯一的名称和别名
- 有权限要求
- 有参数定义
- 有执行逻辑

### 2. 命令注册表 (CommandRegistry)

命令注册表负责:
- 注册命令
- 查找命令
- 权限验证
- 参数解析

### 3. 命令分发器 (CommandDispatcher)

命令分发器负责:
- 解析用户输入
- 匹配命令
- 调用命令执行器
- 处理异常

## 架构设计

```python
# commands/base.py

from dataclasses import dataclass
from typing import Callable, List, Optional, Any
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
    """命令上下文"""
    # 用户信息
    user_id: int
    user_name: str
    
    # 消息信息
    message_id: int
    message_text: str
    chat_id: str
    chat_type: str  # 'group' | 'private'
    
    # 参数
    args: List[str]
    raw_args: str
    
    # 引用消息
    reply_to: Optional[Any] = None
    
    # At 列表
    at_users: List[int] = None
    
    # 图片列表
    images: List[str] = None


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    message: str = ""
    data: Any = None
    error: Optional[str] = None


class Command:
    """命令基类"""
    
    def __init__(
        self,
        name: str,
        handler: Callable,
        description: str = "",
        aliases: List[str] = None,
        permission: PermissionLevel = PermissionLevel.PUBLIC,
        cooldown: int = 0,  # 冷却时间(秒)
        usage: str = "",
    ):
        self.name = name
        self.handler = handler
        self.description = description
        self.aliases = aliases or []
        self.permission = permission
        self.cooldown = cooldown
        self.usage = usage
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """执行命令"""
        try:
            return await self.handler(ctx)
        except Exception as e:
            return CommandResult(
                success=False,
                error=str(e)
            )
    
    def matches(self, input_name: str) -> bool:
        """检查是否匹配命令名"""
        return input_name == self.name or input_name in self.aliases


# 命令装饰器
def command(
    name: str,
    description: str = "",
    aliases: List[str] = None,
    permission: PermissionLevel = PermissionLevel.PUBLIC,
    cooldown: int = 0,
    usage: str = "",
):
    """命令装饰器"""
    def decorator(func):
        cmd = Command(
            name=name,
            handler=func,
            description=description,
            aliases=aliases,
            permission=permission,
            cooldown=cooldown,
            usage=usage,
        )
        # 自动注册到全局注册表
        from .registry import command_registry
        command_registry.register(cmd)
        return func
    return decorator
```

```python
# commands/registry.py

from typing import Dict, List, Optional
from .base import Command, PermissionLevel, CommandContext
from ..services.permission_service import permission_service
from ..utils.cooldown import CooldownManager


class CommandRegistry:
    """命令注册表"""
    
    def __init__(self):
        self._commands: Dict[str, Command] = {}
        self._cooldown_manager = CooldownManager()
    
    def register(self, command: Command) -> None:
        """注册命令"""
        self._commands[command.name] = command
    
    def unregister(self, name: str) -> None:
        """注销命令"""
        if name in self._commands:
            del self._commands[name]
    
    def get(self, name: str) -> Optional[Command]:
        """获取命令"""
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
        """列出命令"""
        commands = list(self._commands.values())
        
        if permission is not None:
            commands = [
                cmd for cmd in commands
                if cmd.permission.value <= permission.value
            ]
        
        return commands
    
    async def can_execute(
        self,
        command: Command,
        ctx: CommandContext
    ) -> tuple[bool, Optional[str]]:
        """检查是否可以执行命令"""
        # 权限检查
        user_permission = await permission_service.get_user_permission(
            ctx.user_id
        )
        
        if command.permission.value > user_permission.value:
            return False, "权限不足"
        
        # 冷却检查
        if command.cooldown > 0:
            remaining = self._cooldown_manager.check(
                f"{command.name}:{ctx.user_id}",
                command.cooldown
            )
            if remaining > 0:
                return False, f"冷却中,请等待 {remaining} 秒"
        
        return True, None


# 全局命令注册表
command_registry = CommandRegistry()
```

```python
# handlers/command_dispatcher.py

import re
from typing import Optional
from ..commands.base import CommandContext, CommandResult
from ..commands.registry import command_registry
from ..models.message import Message


class CommandDispatcher:
    """命令分发器"""
    
    def __init__(self, prefix: str = "- "):
        self.prefix = prefix
    
    def is_command(self, text: str) -> bool:
        """检查是否为命令"""
        return text.startswith(self.prefix)
    
    def parse_command(self, text: str) -> tuple[Optional[str], list[str], str]:
        """
        解析命令
        
        Returns:
            (命令名, 参数列表, 原始参数)
        """
        if not self.is_command(text):
            return None, [], ""
        
        # 移除前缀
        text = text[len(self.prefix):].strip()
        
        if not text:
            return None, [], ""
        
        # 分割命令和参数
        parts = text.split(maxsplit=1)
        command_name = parts[0]
        raw_args = parts[1] if len(parts) > 1 else ""
        
        # 解析参数
        args = re.split(r'\s+', raw_args.strip()) if raw_args else []
        
        return command_name, args, raw_args
    
    async def dispatch(self, message: Message) -> Optional[CommandResult]:
        """
        分发命令
        
        Args:
            message: 消息对象
        
        Returns:
            命令执行结果,如果不是命令则返回 None
        """
        # 解析命令
        cmd_name, args, raw_args = self.parse_command(message.text)
        
        if cmd_name is None:
            return None
        
        # 查找命令
        command = command_registry.get(cmd_name)
        
        if command is None:
            return CommandResult(
                success=False,
                error=f"未知命令: {cmd_name}"
            )
        
        # 构建上下文
        ctx = CommandContext(
            user_id=message.user_id,
            user_name=message.user_name,
            message_id=message.message_id,
            message_text=message.text,
            chat_id=message.chat_id,
            chat_type=message.chat_type,
            args=args,
            raw_args=raw_args,
            reply_to=message.reply_to,
            at_users=message.at_users,
            images=message.images,
        )
        
        # 权限检查
        can_exec, error = await command_registry.can_execute(command, ctx)
        if not can_exec:
            return CommandResult(
                success=False,
                error=error
            )
        
        # 执行命令
        result = await command.execute(ctx)
        
        return result


# 全局命令分发器
command_dispatcher = CommandDispatcher()
```

## 使用示例

### 基础命令

```python
# commands/basic.py

from .base import command, CommandContext, CommandResult, PermissionLevel


@command(
    name="ping",
    description="测试机器人是否在线",
    aliases=["pong"],
)
async def cmd_ping(ctx: CommandContext) -> CommandResult:
    """ping 命令"""
    return CommandResult(
        success=True,
        message="pong! 🏓"
    )


@command(
    name="帮助",
    description="查看帮助信息",
    aliases=["help", "?"],
)
async def cmd_help(ctx: CommandContext) -> CommandResult:
    """帮助命令"""
    from .registry import command_registry
    
    # 获取用户可用命令
    user_perm = await permission_service.get_user_permission(ctx.user_id)
    commands = command_registry.list_commands(permission=user_perm)
    
    # 构建帮助信息
    lines = ["📖 可用命令:"]
    for cmd in commands:
        usage = cmd.usage or f"- {cmd.name}"
        lines.append(f"  {usage}")
        if cmd.description:
            lines.append(f"    {cmd.description}")
    
    return CommandResult(
        success=True,
        message="\n".join(lines)
    )


@command(
    name="关于",
    description="查看机器人信息",
    aliases=["about", "info"],
)
async def cmd_about(ctx: CommandContext) -> CommandResult:
    """关于命令"""
    from ..core.app import app
    
    return CommandResult(
        success=True,
        message=f"{app.bot_name} v{app.version}\n"
                f"一个基于 NapCat 的 QQ 机器人"
    )
```

### 带权限的命令

```python
# commands/admin.py

from .base import command, CommandContext, CommandResult, PermissionLevel


@command(
    name="禁言",
    description="禁言用户",
    permission=PermissionLevel.MANAGE,
    usage="- 禁言 @用户 秒数",
)
async def cmd_mute(ctx: CommandContext) -> CommandResult:
    """禁言命令"""
    if ctx.chat_type != "group":
        return CommandResult(
            success=False,
            error="此命令只能在群聊中使用"
        )
    
    if not ctx.at_users:
        return CommandResult(
            success=False,
            error="请 @ 要禁言的用户"
        )
    
    if len(ctx.args) < 2:
        return CommandResult(
            success=False,
            error="请指定禁言时间(秒)"
        )
    
    target_user = ctx.at_users[0]
    duration = int(ctx.args[1])
    
    # 调用 QQ API 禁言
    # ... 实现逻辑
    
    return CommandResult(
        success=True,
        message=f"已禁言用户 {target_user} {duration} 秒"
    )
```

### 带冷却的命令

```python
# commands/image.py

from .base import command, CommandContext, CommandResult
from ..services.image_service import image_service


@command(
    name="生图",
    description="生成随机图片",
    aliases=["pic", "图片"],
    cooldown=18,  # 18 秒冷却
    usage="- 生图 [类型]",
)
async def cmd_generate_image(ctx: CommandContext) -> CommandResult:
    """生图命令"""
    # 解析类型
    img_type = ctx.args[0] if ctx.args else "二次元"
    
    # 生成图片
    image_url = await image_service.generate(img_type)
    
    if image_url:
        return CommandResult(
            success=True,
            data={"image": image_url}
        )
    else:
        return CommandResult(
            success=False,
            error="图片生成失败"
        )
```

## 集成到现有系统

```python
# handlers/message_handler.py

from ..commands.dispatcher import command_dispatcher
from ..models.message import Message


async def handle_message(message: Message):
    """处理消息"""
    
    # 尝试作为命令处理
    result = await command_dispatcher.dispatch(message)
    
    if result is not None:
        # 是命令
        if result.success:
            # 发送成功响应
            await send_message(message.chat_id, result.message, result.data)
        else:
            # 发送错误响应
            await send_message(message.chat_id, f"❌ {result.error}")
        return
    
    # 不是命令,走其他处理流程(如 AI 对话)
    await handle_ai_message(message)
```

## 测试

```python
# tests/test_commands.py

import pytest
from xiaomiao.commands.base import CommandContext, PermissionLevel
from xiaomiao.commands.basic import cmd_ping, cmd_help


@pytest.mark.asyncio
async def test_ping_command():
    """测试 ping 命令"""
    ctx = CommandContext(
        user_id=12345,
        user_name="测试用户",
        message_id=1,
        message_text="ping",
        chat_id="test",
        chat_type="private",
        args=[],
        raw_args="",
    )
    
    result = await cmd_ping(ctx)
    
    assert result.success is True
    assert "pong" in result.message


@pytest.mark.asyncio
async def test_help_command():
    """测试帮助命令"""
    ctx = CommandContext(
        user_id=12345,
        user_name="测试用户",
        message_id=1,
        message_text="帮助",
        chat_id="test",
        chat_type="private",
        args=[],
        raw_args="",
    )
    
    result = await cmd_help(ctx)
    
    assert result.success is True
    assert "可用命令" in result.message
```

## 优势

1. **模块化**: 每个命令独立文件,职责清晰
2. **可扩展**: 通过装饰器轻松添加新命令
3. **可测试**: 纯函数,易于单元测试
4. **统一管理**: 权限、冷却、参数解析统一处理
5. **类型安全**: 使用 dataclass 和类型注解
6. **向后兼容**: 可与现有系统并存,逐步迁移

## 迁移路径

1. 实现命令系统基础设施
2. 迁移简单命令(ping, 帮助, 关于)
3. 验证基础功能
4. 逐步迁移复杂命令
5. 废弃旧代码
