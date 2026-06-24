"""
文本消息处理器
"""
import logging
try:
    from ..models import Message, Response
except ImportError:
    from models import Message, Response

logger = logging.getLogger(__name__)


class TextHandler:
    """文本消息处理器"""

    def __init__(self):
        self.name = "TextHandler"

    async def handle(self, message: Message) -> Response:
        """
        处理文本消息

        Args:
            message: 消息对象

        Returns:
            响应对象
        """
        if not message.has_text():
            logger.debug("消息不包含文本，跳过处理")
            return Response(text="")

        text = message.text.strip()
        logger.info(f"处理文本消息: {text[:50]}")

        # 这里可以添加具体的文本处理逻辑
        # 例如：调用 Agent、搜索、翻译等

        return Response(text=f"收到文本: {text[:100]}")

    async def handle_greeting(self, message: Message) -> Response:
        """处理问候消息"""
        greetings = ["你好", "hi", "hello", "早上好", "晚上好"]
        text_lower = message.text.lower()

        if any(g in text_lower for g in greetings):
            return Response(text=f"你好！我是小喵，有什么可以帮你的吗？")

        return Response(text="")

    async def handle_farewell(self, message: Message) -> Response:
        """处理告别消息"""
        farewells = ["再见", "拜拜", "goodbye", "bye"]
        text_lower = message.text.lower()

        if any(f in text_lower for f in farewells):
            return Response(text=f"再见！有需要随时找我~")

        return Response(text="")
