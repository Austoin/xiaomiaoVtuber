"""
消息路由器 - 根据消息类型和内容路由到不同的处理器
"""
from typing import Callable, Optional, List, Dict, Any, Awaitable
from dataclasses import dataclass
import re
import logging

try:
    from ..models import Message, Response, MessageSource
except ImportError:
    from models import Message, Response, MessageSource

logger = logging.getLogger(__name__)


@dataclass
class Route:
    """路由规则"""
    name: str
    handler: Callable[[Message], Awaitable[Response]]
    condition: Optional[Callable[[Message], bool]] = None
    priority: int = 0
    description: str = ""


class MessageRouter:
    """消息路由器"""

    def __init__(self):
        self.routes: List[Route] = []
        self.fallback_handler: Optional[Callable[[Message], Awaitable[Response]]] = None

    def add_route(
        self,
        name: str,
        handler: Callable[[Message], Awaitable[Response]],
        condition: Optional[Callable[[Message], bool]] = None,
        priority: int = 0,
        description: str = "",
    ) -> None:
        """
        添加路由规则

        Args:
            name: 路由名称
            handler: 处理器函数
            condition: 匹配条件函数
            priority: 优先级（数字越大优先级越高）
            description: 描述
        """
        route = Route(
            name=name,
            handler=handler,
            condition=condition,
            priority=priority,
            description=description,
        )
        self.routes.append(route)
        # 按优先级排序
        self.routes.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"添加路由: {name} (优先级: {priority})")

    def route(
        self,
        name: str,
        condition: Optional[Callable[[Message], bool]] = None,
        priority: int = 0,
        description: str = "",
    ):
        """
        路由装饰器

        Example:
            @router.route("greeting", condition=lambda msg: msg.text.startswith("你好"))
            async def handle_greeting(message: Message) -> Response:
                return Response(text="你好！")
        """
        def decorator(handler: Callable[[Message], Awaitable[Response]]):
            self.add_route(name, handler, condition, priority, description)
            return handler
        return decorator

    def command(
        self,
        command: str,
        prefix: str = "",
        priority: int = 100,
        description: str = "",
    ):
        """
        命令路由装饰器

        Args:
            command: 命令名称
            prefix: 命令前缀
            priority: 优先级
            description: 描述

        Example:
            @router.command("帮助")
            async def handle_help(message: Message) -> Response:
                return Response(text="帮助信息...")
        """
        def condition(msg: Message) -> bool:
            cmd_tuple = msg.extract_command(prefix)
            if cmd_tuple is None:
                return False
            cmd, _ = cmd_tuple
            return cmd == command

        return self.route(
            name=f"command:{command}",
            condition=condition,
            priority=priority,
            description=description or f"处理 {command} 命令",
        )

    def pattern(
        self,
        pattern: str,
        priority: int = 50,
        description: str = "",
    ):
        """
        正则表达式路由装饰器

        Example:
            @router.pattern(r"搜索\s+(.+)")
            async def handle_search(message: Message) -> Response:
                query = re.search(r"搜索\s+(.+)", message.text).group(1)
                return Response(text=f"搜索: {query}")
        """
        compiled = re.compile(pattern)

        def condition(msg: Message) -> bool:
            return bool(compiled.search(msg.text))

        return self.route(
            name=f"pattern:{pattern}",
            condition=condition,
            priority=priority,
            description=description or f"匹配模式: {pattern}",
        )

    def source(
        self,
        source: MessageSource,
        priority: int = 10,
        description: str = "",
    ):
        """
        按消息来源路由

        Example:
            @router.source(MessageSource.GROUP)
            async def handle_group(message: Message) -> Response:
                return Response(text="群消息处理")
        """
        def condition(msg: Message) -> bool:
            return msg.source == source

        return self.route(
            name=f"source:{source.value}",
            condition=condition,
            priority=priority,
            description=description or f"处理 {source.value} 消息",
        )

    def set_fallback(self, handler: Callable[[Message], Awaitable[Response]]) -> None:
        """设置默认处理器（当没有路由匹配时使用）"""
        self.fallback_handler = handler
        logger.info("设置默认处理器")

    async def route_message(self, message: Message) -> Response:
        """
        路由消息到对应的处理器

        Args:
            message: 消息对象

        Returns:
            响应对象
        """
        logger.debug(f"路由消息: {message.message_id} from {message.user.user_id}")

        # 遍历路由规则
        for route in self.routes:
            try:
                # 检查条件
                if route.condition is None or route.condition(message):
                    logger.info(f"匹配路由: {route.name}")
                    response = await route.handler(message)
                    return response
            except Exception as e:
                logger.error(f"路由 {route.name} 处理失败: {e}", exc_info=True)
                # 继续尝试下一个路由
                continue

        # 没有匹配的路由，使用默认处理器
        if self.fallback_handler:
            logger.info("使用默认处理器")
            return await self.fallback_handler(message)

        # 没有默认处理器，返回空响应
        logger.warning("没有匹配的路由和默认处理器")
        return Response(text="抱歉，我不知道如何处理这条消息")

    def list_routes(self) -> List[Dict[str, Any]]:
        """列出所有路由"""
        return [
            {
                "name": route.name,
                "priority": route.priority,
                "description": route.description,
            }
            for route in self.routes
        ]


# 全局路由器实例
router = MessageRouter()
