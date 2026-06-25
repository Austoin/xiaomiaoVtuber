"""
命令系统测试

测试命令基础设施的核心功能
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[2]
xiaomiao_path = project_root / "xiaomiao"
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(xiaomiao_path) not in sys.path:
    sys.path.insert(0, str(xiaomiao_path))

# 直接导入,不使用相对导入
import commands.base as cmd_base
import commands.registry as cmd_registry
import handlers.command_dispatcher as cmd_dispatcher

Command = cmd_base.Command
CommandContext = cmd_base.CommandContext
CommandResult = cmd_base.CommandResult
PermissionLevel = cmd_base.PermissionLevel
command = cmd_base.command

CommandRegistry = cmd_registry.CommandRegistry
CommandDispatcher = cmd_dispatcher.CommandDispatcher


# 测试命令上下文

def test_command_context_creation():
    """测试命令上下文创建"""
    ctx = CommandContext(
        user_id=12345,
        user_name="测试用户",
        message_id=1,
        message_text="- ping",
        chat_id="test_chat",
        chat_type="private",
        args=[],
        raw_args="",
    )

    assert ctx.user_id == 12345
    assert ctx.user_name == "测试用户"
    assert ctx.chat_type == "private"
    assert ctx.args == []


# 测试命令结果

def test_command_result_ok():
    """测试成功结果"""
    result = CommandResult.ok("成功")

    assert result.success is True
    assert result.message == "成功"
    assert result.error is None


def test_command_result_fail():
    """测试失败结果"""
    result = CommandResult.fail("失败原因")

    assert result.success is False
    assert result.error == "失败原因"


# 测试命令类

@pytest.mark.asyncio
async def test_command_execution():
    """测试命令执行"""

    async def handler(ctx: CommandContext) -> CommandResult:
        return CommandResult.ok("测试成功")

    cmd = Command(
        name="test",
        handler=handler,
        description="测试命令"
    )

    ctx = CommandContext(
        user_id=1,
        user_name="test",
        message_id=1,
        message_text="- test",
        chat_id="test",
        chat_type="private",
    )

    result = await cmd.execute(ctx)

    assert result.success is True
    assert result.message == "测试成功"


def test_command_matches():
    """测试命令匹配"""

    async def handler(ctx):
        return CommandResult.ok()

    cmd = Command(
        name="ping",
        handler=handler,
        aliases=["pong", "p"]
    )

    assert cmd.matches("ping") is True
    assert cmd.matches("pong") is True
    assert cmd.matches("p") is True
    assert cmd.matches("other") is False


# 测试命令装饰器

@pytest.mark.asyncio
async def test_command_decorator():
    """测试命令装饰器"""

    registry = CommandRegistry()

    @command(
        name="test_decorator",
        description="测试装饰器",
        auto_register=False  # 不自动注册到全局
    )
    async def test_cmd(ctx: CommandContext) -> CommandResult:
        return CommandResult.ok("装饰器测试")

    # 手动注册
    registry.register(test_cmd._command)

    # 查找命令
    cmd = registry.get("test_decorator")
    assert cmd is not None
    assert cmd.description == "测试装饰器"

    # 执行命令
    ctx = CommandContext(
        user_id=1,
        user_name="test",
        message_id=1,
        message_text="- test_decorator",
        chat_id="test",
        chat_type="private",
    )

    result = await cmd.execute(ctx)
    assert result.success is True
    assert result.message == "装饰器测试"


# 测试命令注册表

def test_registry_register_and_get():
    """测试命令注册和获取"""

    registry = CommandRegistry()

    async def handler(ctx):
        return CommandResult.ok()

    cmd = Command(name="test", handler=handler)
    registry.register(cmd)

    # 精确匹配
    found = registry.get("test")
    assert found is not None
    assert found.name == "test"

    # 别名匹配
    cmd2 = Command(name="ping", handler=handler, aliases=["pong"])
    registry.register(cmd2)

    found = registry.get("pong")
    assert found is not None
    assert found.name == "ping"


def test_registry_list_commands():
    """测试命令列表"""

    registry = CommandRegistry()

    async def handler(ctx):
        return CommandResult.ok()

    # 添加不同权限的命令
    registry.register(Command(
        name="public",
        handler=handler,
        permission=PermissionLevel.PUBLIC
    ))

    registry.register(Command(
        name="manage",
        handler=handler,
        permission=PermissionLevel.MANAGE
    ))

    registry.register(Command(
        name="root",
        handler=handler,
        permission=PermissionLevel.ROOT
    ))

    # 列出所有命令
    all_cmds = registry.list_commands()
    assert len(all_cmds) == 3

    # 只列出 PUBLIC 权限可用的
    public_cmds = registry.list_commands(permission=PermissionLevel.PUBLIC)
    assert len(public_cmds) == 1
    assert public_cmds[0].name == "public"

    # 只列出 MANAGE 权限可用的
    manage_cmds = registry.list_commands(permission=PermissionLevel.MANAGE)
    assert len(manage_cmds) == 2  # public + manage


def test_registry_cooldown():
    """测试冷却检查"""

    registry = CommandRegistry()

    async def handler(ctx):
        return CommandResult.ok()

    cmd = Command(
        name="cooldown_test",
        handler=handler,
        cooldown=5  # 5 秒冷却
    )

    user_id = 12345

    # 第一次执行,应该可以
    can_exec, remaining = registry.check_cooldown(cmd, user_id)
    assert can_exec is True
    assert remaining == 0

    # 立即再次执行,应该被冷却
    can_exec, remaining = registry.check_cooldown(cmd, user_id)
    assert can_exec is False
    assert remaining > 0


# 测试命令分发器


def test_dispatcher_is_command():
    """测试命令识别"""

    dispatcher = CommandDispatcher(prefix="- ")

    assert dispatcher.is_command("- ping") is True
    assert dispatcher.is_command("ping") is False
    assert dispatcher.is_command("") is False


def test_dispatcher_parse_command():
    """测试命令解析"""

    dispatcher = CommandDispatcher(prefix="- ")

    # 无参数命令
    name, args, raw = dispatcher.parse_command("- ping")
    assert name == "ping"
    assert args == []
    assert raw == ""

    # 有参数命令
    name, args, raw = dispatcher.parse_command("- 生图 二次元")
    assert name == "生图"
    assert args == ["二次元"]
    assert raw == "二次元"

    # 多个参数
    name, args, raw = dispatcher.parse_command("- 禁言 @用户 60")
    assert name == "禁言"
    assert args == ["@用户", "60"]
    assert raw == "@用户 60"

    # 不是命令
    name, args, raw = dispatcher.parse_command("普通消息")
    assert name is None


@pytest.mark.asyncio
async def test_dispatcher_dispatch():
    """测试命令分发"""

    dispatcher = CommandDispatcher(prefix="- ")
    registry = CommandRegistry()

    # 注册测试命令
    @command(name="test_dispatch", auto_register=False)
    async def test_cmd(ctx: CommandContext) -> CommandResult:
        return CommandResult.ok(f"收到参数: {ctx.args}")

    registry.register(test_cmd._command)

    # 临时替换全局注册表
    import xiaomiao.handlers.command_dispatcher as dispatcher_module
    original_registry = dispatcher_module.command_registry
    dispatcher_module.command_registry = registry

    try:
        # 分发命令
        result = await dispatcher.dispatch(
            user_id=12345,
            user_name="测试用户",
            message_id=1,
            message_text="- test_dispatch arg1 arg2",
            chat_id="test",
            chat_type="private",
        )

        assert result is not None
        assert result.success is True
        assert "arg1" in result.message

        # 非命令消息
        result = await dispatcher.dispatch(
            user_id=12345,
            user_name="测试用户",
            message_id=2,
            message_text="普通消息",
            chat_id="test",
            chat_type="private",
        )

        assert result is None  # 不是命令

    finally:
        # 恢复全局注册表
        dispatcher_module.command_registry = original_registry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
