"""
命令分发器

解析用户输入,匹配命令,执行命令
"""

import re
import logging
from typing import Optional
from .base import CommandContext, CommandResult
from .registry import command_registry

logger = logging.getLogger(__name__)


class CommandDispatcher:
    """命令分发器"""

    def __init__(self, prefix: str = "- "):
        """
        初始化命令分发器

        Args:
            prefix: 命令前缀,默认为 "- "
        """
        self.prefix = prefix

    def is_command(self, text: str) -> bool:
        """
        检查是否为命令

        Args:
            text: 消息文本

        Returns:
            是否为命令
        """
        return text.startswith(self.prefix)

    def parse_command(self, text: str) -> tuple[Optional[str], list[str], str]:
        """
        解析命令

        Args:
            text: 消息文本

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

    def build_context(
        self,
        user_id: int,
        user_name: str,
        message_id: int,
        message_text: str,
        chat_id: str,
        chat_type: str,
        args: list[str],
        raw_args: str,
        **kwargs
    ) -> CommandContext:
        """
        构建命令上下文

        Args:
            user_id: 用户 ID
            user_name: 用户名
            message_id: 消息 ID
            message_text: 消息文本
            chat_id: 聊天 ID
            chat_type: 聊天类型
            args: 参数列表
            raw_args: 原始参数
            **kwargs: 其他参数

        Returns:
            命令上下文
        """
        return CommandContext(
            user_id=user_id,
            user_name=user_name,
            message_id=message_id,
            message_text=message_text,
            chat_id=chat_id,
            chat_type=chat_type,
            args=args,
            raw_args=raw_args,
            reply_to=kwargs.get('reply_to'),
            at_users=kwargs.get('at_users', []),
            images=kwargs.get('images', []),
            extra=kwargs.get('extra', {}),
        )

    async def dispatch(
        self,
        user_id: int,
        user_name: str,
        message_id: int,
        message_text: str,
        chat_id: str,
        chat_type: str,
        **kwargs
    ) -> Optional[CommandResult]:
        """
        分发命令

        Args:
            user_id: 用户 ID
            user_name: 用户名
            message_id: 消息 ID
            message_text: 消息文本
            chat_id: 聊天 ID
            chat_type: 聊天类型 ('group' | 'private')
            **kwargs: 其他参数 (reply_to, at_users, images, extra)

        Returns:
            命令执行结果,如果不是命令则返回 None
        """
        # 解析命令
        cmd_name, args, raw_args = self.parse_command(message_text)

        if cmd_name is None:
            return None

        logger.info(f"解析命令: {cmd_name}, 参数: {args}")

        # 查找命令
        command = command_registry.get(cmd_name)

        if command is None:
            logger.warning(f"未知命令: {cmd_name}")
            return CommandResult.fail(f"未知命令: {cmd_name}\n发送 '- 帮助' 查看可用命令")

        # 构建上下文
        ctx = self.build_context(
            user_id=user_id,
            user_name=user_name,
            message_id=message_id,
            message_text=message_text,
            chat_id=chat_id,
            chat_type=chat_type,
            args=args,
            raw_args=raw_args,
            **kwargs
        )

        # 权限检查
        can_exec, error = await command_registry.can_execute(command, ctx)
        if not can_exec:
            logger.warning(f"命令 {cmd_name} 权限检查失败: {error}")
            return CommandResult.fail(error)

        # 执行命令
        try:
            logger.info(f"执行命令: {cmd_name}, 用户: {user_id}")
            result = await command.execute(ctx)
            logger.info(f"命令 {cmd_name} 执行{'成功' if result.success else '失败'}")
            return result
        except Exception as e:
            logger.error(f"命令 {cmd_name} 执行异常: {e}", exc_info=True)
            return CommandResult.fail(f"命令执行失败: {str(e)}")


# 全局命令分发器
command_dispatcher = CommandDispatcher()
