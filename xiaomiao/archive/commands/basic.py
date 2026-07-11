"""
基础命令模块

包含 ping, 帮助, 关于等基础命令
这是第一批迁移的命令,用于验证命令系统可行性
"""

import logging
from .base import command, CommandContext, CommandResult, PermissionLevel
from .registry import command_registry

logger = logging.getLogger(__name__)


@command(
    name="ping",
    description="测试机器人是否在线",
    aliases=["pong"],
    usage="ping",
)
async def cmd_ping(ctx: CommandContext) -> CommandResult:
    """ping 命令"""
    return CommandResult.ok("pong! 🏓")


@command(
    name="帮助",
    description="查看帮助信息",
    aliases=["help", "?"],
    usage="- 帮助",
)
async def cmd_help(ctx: CommandContext) -> CommandResult:
    """帮助命令"""
    help_text = command_registry.get_help_text(ctx.user_id)
    return CommandResult.ok(help_text)


@command(
    name="关于",
    description="查看机器人信息",
    aliases=["about", "info"],
    usage="- 关于",
)
async def cmd_about(ctx: CommandContext) -> CommandResult:
    """关于命令"""
    try:
        from ..core.app import app
        bot_name = app.bot_name
        version = app.version
    except Exception:
        bot_name = "小喵"
        version = "2.0"

    import platform
    import time

    # 获取运行时间
    try:
        from ..main import second_start
        uptime = int(time.time() - second_start)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        uptime_str = f"{hours} 小时 {minutes} 分钟"
    except Exception:
        uptime_str = "未知"

    message = (
        f"🤖 {bot_name} v{version}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📱 基于 NapCat + HypeR Bot\n"
        f"💡 AI 对话 + 图片生成 + 群管理\n"
        f"⏱️ 运行时间: {uptime_str}\n"
        f"🖥️ 系统: {platform.system()} {platform.release()}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"发送 '- 帮助' 查看可用命令"
    )

    return CommandResult.ok(message)


# 注意: 这些命令会在模块导入时自动注册
# 只需在 main.py 中导入这个模块即可
logger.info("基础命令已加载")
