"""
角色命令模块

包含角色切换相关命令
"""

import logging
from .base import command, CommandContext, CommandResult
from ..services.persona_service import persona_service

logger = logging.getLogger(__name__)


@command(
    name="当我女朋友",
    description="切换到女朋友模式",
    aliases=["女朋友", "girlfriend"],
    usage="- 当我女朋友",
)
async def cmd_girlfriend(ctx: CommandContext) -> CommandResult:
    """女朋友模式命令"""
    success = persona_service.set_persona(ctx.user_id, "girlfriend")

    if success:
        return CommandResult.ok(
            "💕 好……好的啦，人家就当你的女朋友啦~\n"
            "以后要对人家好一点哦 (*ᴗ͈ˬᴗ͈)ꕤ*.ﾟ"
        )
    else:
        return CommandResult.fail("切换失败,请稍后重试")


@command(
    name="做我姐姐吧",
    description="切换到姐姐模式",
    aliases=["姐姐", "sister"],
    usage="- 做我姐姐吧",
)
async def cmd_sister(ctx: CommandContext) -> CommandResult:
    """姐姐模式命令"""
    success = persona_service.set_persona(ctx.user_id, "sister")

    if success:
        return CommandResult.ok(
            "👭 好的呢,姐姐会好好照顾你的~\n"
            "有什么事情都可以跟姐姐说哦 ♡"
        )
    else:
        return CommandResult.fail("切换失败,请稍后重试")


@command(
    name="做我mm吧",
    description="切换到妈妈模式",
    aliases=["妈妈", "mother"],
    usage="- 做我mm吧",
)
async def cmd_mother(ctx: CommandContext) -> CommandResult:
    """妈妈模式命令"""
    success = persona_service.set_persona(ctx.user_id, "mother")

    if success:
        return CommandResult.ok(
            "🌸 好的孩子,妈妈会一直陪着你的~\n"
            "要记得按时吃饭休息哦 ♡"
        )
    else:
        return CommandResult.fail("切换失败,请稍后重试")


@command(
    name="程序员",
    description="切换到高级程序员模式",
    aliases=["programmer", "工程师"],
    usage="- 程序员",
)
async def cmd_programmer(ctx: CommandContext) -> CommandResult:
    """程序员模式命令"""
    success = persona_service.set_persona(ctx.user_id, "programmer")

    if success:
        return CommandResult.ok(
            "💻 已切换到高级程序员模式\n"
            "我将以资深工程师的视角为你提供帮助"
        )
    else:
        return CommandResult.fail("切换失败,请稍后重试")


# 注意: 这些命令会在模块导入时自动注册
logger.info("角色命令已加载")
