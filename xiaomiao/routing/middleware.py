"""
中间件系统 - 在消息处理前后执行的逻辑
"""
from typing import Callable, Awaitable, List
from abc import ABC, abstractmethod
import logging

try:
    from ..models import Message, Response
except ImportError:
    from models import Message, Response

logger = logging.getLogger(__name__)


class Middleware(ABC):
    """中间件基类"""

    @abstractmethod
    async def before(self, message: Message) -> bool:
        """
        消息处理前执行

        Args:
            message: 消息对象

        Returns:
            是否继续处理（True=继续，False=中断）
        """
        pass

    @abstractmethod
    async def after(self, message: Message, response: Response) -> Response:
        """
        消息处理后执行

        Args:
            message: 原始消息
            response: 响应对象

        Returns:
            修改后的响应对象
        """
        pass


class LoggingMiddleware(Middleware):
    """日志中间件"""

    async def before(self, message: Message) -> bool:
        logger.info(f"收到消息: {message.message_id} from {message.user.user_id}")
        logger.debug(f"消息内容: {message.text[:100]}")
        return True

    async def after(self, message: Message, response: Response) -> Response:
        logger.info(f"响应消息: {message.message_id}")
        logger.debug(f"响应内容: {response.text[:100]}")
        return response


class RateLimitMiddleware(Middleware):
    """频率限制中间件"""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Args:
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests: dict = {}  # user_id -> [(timestamp, ...)]

    async def before(self, message: Message) -> bool:
        from datetime import datetime, timedelta

        user_id = message.user.user_id
        now = datetime.now()

        # 清理过期记录
        if user_id in self.user_requests:
            cutoff = now - timedelta(seconds=self.window_seconds)
            self.user_requests[user_id] = [
                ts for ts in self.user_requests[user_id] if ts > cutoff
            ]

        # 检查是否超限
        if user_id in self.user_requests:
            if len(self.user_requests[user_id]) >= self.max_requests:
                logger.warning(f"用户 {user_id} 触发频率限制")
                return False

        # 记录请求
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        self.user_requests[user_id].append(now)

        return True

    async def after(self, message: Message, response: Response) -> Response:
        return response


class PermissionMiddleware(Middleware):
    """权限检查中间件"""

    def __init__(self, required_role: str = "user"):
        """
        Args:
            required_role: 所需角色 (user, admin, owner, root)
        """
        self.required_role = required_role
        self.role_levels = {
            "user": 0,
            "admin": 1,
            "owner": 2,
            "root": 3,
        }

    async def before(self, message: Message) -> bool:
        user_role = message.user.role
        required_level = self.role_levels.get(self.required_role, 0)
        user_level = self.role_levels.get(user_role, 0)

        if user_level < required_level:
            logger.warning(
                f"用户 {message.user.user_id} 权限不足: "
                f"{user_role} < {self.required_role}"
            )
            return False

        return True

    async def after(self, message: Message, response: Response) -> Response:
        return response


class MiddlewareChain:
    """中间件链"""

    def __init__(self):
        self.middlewares: List[Middleware] = []

    def use(self, middleware: Middleware) -> None:
        """添加中间件"""
        self.middlewares.append(middleware)
        logger.info(f"添加中间件: {middleware.__class__.__name__}")

    async def process(
        self,
        message: Message,
        handler: Callable[[Message], Awaitable[Response]],
    ) -> Response:
        """
        执行中间件链

        Args:
            message: 消息对象
            handler: 实际的处理器函数

        Returns:
            响应对象
        """
        # 执行 before 中间件
        for middleware in self.middlewares:
            try:
                should_continue = await middleware.before(message)
                if not should_continue:
                    logger.info(f"中间件 {middleware.__class__.__name__} 中断处理")
                    return Response(text="请求被拒绝").set_error("中间件拒绝")
            except Exception as e:
                logger.error(f"中间件 before 失败: {e}", exc_info=True)
                return Response(text="处理失败").set_error(str(e))

        # 执行实际处理器
        try:
            response = await handler(message)
        except Exception as e:
            logger.error(f"处理器执行失败: {e}", exc_info=True)
            return Response(text="处理失败").set_error(str(e))

        # 执行 after 中间件（逆序）
        for middleware in reversed(self.middlewares):
            try:
                response = await middleware.after(message, response)
            except Exception as e:
                logger.error(f"中间件 after 失败: {e}", exc_info=True)

        return response


# 全局中间件链实例
middleware_chain = MiddlewareChain()

# 默认添加日志中间件
middleware_chain.use(LoggingMiddleware())
