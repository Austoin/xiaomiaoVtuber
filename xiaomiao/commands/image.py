"""
图片命令模块

包含生图、大头照、读图等图片相关命令
"""

import logging
from .base import command, CommandContext, CommandResult, PermissionLevel
from ..services.image_service import image_service

logger = logging.getLogger(__name__)


@command(
    name="生图",
    description="生成随机图片",
    aliases=["pic", "图片", "生成图片"],
    cooldown=18,  # 18 秒冷却
    usage="- 生图 [类型]",
    examples=[
        "- 生图",
        "- 生图 二次元",
        "- 生图 风景",
        "- 生图 妹子",
        "- 生图 随机",
    ],
)
async def cmd_generate_image(ctx: CommandContext) -> CommandResult:
    """生图命令"""
    # 解析类型
    img_type = ctx.args[0] if ctx.args else "二次元"

    logger.info(f"生成图片: 类型={img_type}, 用户={ctx.user_id}")

    # 生成图片
    image_url = await image_service.generate(img_type)

    if image_url:
        return CommandResult(
            success=True,
            message=f"🎨 为你生成了一张 {img_type} 图片~",
            data={"image": image_url}
        )
    else:
        return CommandResult.fail("图片生成失败,请稍后重试")


@command(
    name="大头照",
    description="获取用户头像",
    aliases=["头像", "avatar"],
    usage="- 大头照 [@用户]",
    examples=[
        "- 大头照",
        "- 大头照 @张三",
    ],
)
async def cmd_avatar(ctx: CommandContext) -> CommandResult:
    """大头照命令"""
    # 获取目标用户 (如果有 @,取第一个;否则取自己)
    target_qq = ctx.at_users[0] if ctx.at_users else ctx.user_id

    logger.info(f"获取头像: QQ={target_qq}, 请求者={ctx.user_id}")

    # 获取头像 URL
    avatar_url = await image_service.get_avatar(target_qq)

    return CommandResult(
        success=True,
        message=f"📸 这是头像~",
        data={"image": avatar_url}
    )


@command(
    name="读图",
    description="切换到图片识别模式",
    aliases=["识图", "看图"],
    usage="- 读图",
)
async def cmd_read_image(ctx: CommandContext) -> CommandResult:
    """
    读图命令

    注意: 这个命令只是一个占位符
    实际的图片识别逻辑仍在 main.py 中处理
    """
    return CommandResult.ok(
        "✅ 已切换到图片识别模式\n"
        "现在发送图片给我,我会帮你识别~"
    )


# 注意: 这些命令会在模块导入时自动注册
logger.info("图片命令已加载")
