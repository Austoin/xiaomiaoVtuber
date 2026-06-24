"""
命令处理器
"""
import logging
from typing import Dict, Callable, Awaitable, Optional
try:
    from ..models import Message, Response
except ImportError:
    from models import Message, Response

logger = logging.getLogger(__name__)


class CommandHandler:
    """命令处理器"""

    def __init__(self, prefix: str = ""):
        """
        Args:
            prefix: 命令前缀，例如 "/" 或 ""（无前缀）
        """
        self.prefix = prefix
        self.commands: Dict[str, Callable[[Message, str], Awaitable[Response]]] = {}
        self._register_default_commands()

    def _register_default_commands(self):
        """注册默认命令"""
        self.register("帮助", self.cmd_help)
        self.register("help", self.cmd_help)
        self.register("关于", self.cmd_about)
        self.register("about", self.cmd_about)
        self.register("状态", self.cmd_status)
        self.register("status", self.cmd_status)

    def register(
        self,
        command: str,
        handler: Callable[[Message, str], Awaitable[Response]]
    ):
        """
        注册命令处理器

        Args:
            command: 命令名称
            handler: 处理函数，接收 (message, args) 返回 Response
        """
        self.commands[command] = handler
        logger.info(f"注册命令: {command}")

    async def handle(self, message: Message) -> Optional[Response]:
        """
        处理命令消息

        Args:
            message: 消息对象

        Returns:
            响应对象，如果不是命令则返回 None
        """
        cmd_tuple = message.extract_command(self.prefix)
        if cmd_tuple is None:
            return None

        command, args = cmd_tuple
        logger.info(f"处理命令: {command} (参数: {args})")

        # 查找命令处理器
        handler = self.commands.get(command)
        if handler is None:
            logger.debug(f"未知命令: {command}")
            return Response(text=f"未知命令: {command}\n发送\"帮助\"查看可用命令")

        try:
            response = await handler(message, args)
            return response
        except Exception as e:
            logger.error(f"命令 {command} 执行失败: {e}", exc_info=True)
            return Response(text=f"命令执行失败: {str(e)}")

    async def cmd_help(self, message: Message, args: str) -> Response:
        """帮助命令"""
        help_text = "📖 可用命令列表：\n\n"

        # 按字母顺序列出命令
        for cmd in sorted(self.commands.keys()):
            help_text += f"• {self.prefix}{cmd}\n"

        help_text += "\n发送命令获取更多信息"
        return Response(text=help_text)

    async def cmd_about(self, message: Message, args: str) -> Response:
        """关于命令"""
        about_text = (
            "🎭 xiaomiaoVirtual\n\n"
            "版本: 2.0\n"
            "一个基于 AI 的智能助手\n\n"
            "功能:\n"
            "• 智能对话\n"
            "• 文件处理\n"
            "• 图片理解\n"
            "• 工具调用\n"
        )
        return Response(text=about_text)

    async def cmd_status(self, message: Message, args: str) -> Response:
        """状态命令"""
        import psutil
        import platform

        # 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        status_text = (
            "📊 系统状态\n\n"
            f"平台: {platform.system()} {platform.release()}\n"
            f"CPU: {cpu_percent}%\n"
            f"内存: {memory_percent}%\n"
            f"运行中: ✅"
        )

        return Response(text=status_text)

    def list_commands(self) -> list[str]:
        """列出所有命令"""
        return sorted(self.commands.keys())
