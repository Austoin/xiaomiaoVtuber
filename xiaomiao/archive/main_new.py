"""
xiaomiao 新版主入口 - 基于模块化架构

这是一个示例文件，展示如何使用新的模块化架构
原有的 main.py 保持不变，逐步迁移功能
"""
import asyncio
import logging
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入核心模块
from core import app
from models import Message, Response, User, MessageSource, MessageType
from routing.message_router import MessageRouter
from routing.middleware import MiddlewareChain, LoggingMiddleware, RateLimitMiddleware
from handlers import CommandHandler, TextHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XiaomiaoBot:
    """xiaomiao Bot 主类"""

    def __init__(self):
        """初始化 Bot"""
        # 初始化应用
        app.initialize()

        # 创建路由器
        self.router = MessageRouter()

        # 创建中间件链
        self.middleware = MiddlewareChain()
        self.middleware.use(LoggingMiddleware())
        self.middleware.use(RateLimitMiddleware(max_requests=10, window_seconds=60))

        # 创建处理器
        self.command_handler = CommandHandler(prefix="")
        self.text_handler = TextHandler()

        # 注册路由
        self._register_routes()

        logger.info(f"[OK] {app.bot_name} 初始化完成")

    def _register_routes(self):
        """注册路由规则"""

        # 1. 命令路由（最高优先级）
        @self.router.route(
            name="command",
            condition=lambda msg: msg.is_command(),
            priority=100,
            description="处理命令消息"
        )
        async def handle_command(message: Message) -> Response:
            response = await self.command_handler.handle(message)
            return response if response else Response(text="")

        # 2. 问候路由
        @self.router.route(
            name="greeting",
            condition=lambda msg: any(
                word in msg.text.lower()
                for word in ["你好", "hi", "hello"]
            ),
            priority=90,
            description="处理问候消息"
        )
        async def handle_greeting(message: Message) -> Response:
            return await self.text_handler.handle_greeting(message)

        # 3. 告别路由
        @self.router.route(
            name="farewell",
            condition=lambda msg: any(
                word in msg.text.lower()
                for word in ["再见", "拜拜", "bye"]
            ),
            priority=90,
            description="处理告别消息"
        )
        async def handle_farewell(message: Message) -> Response:
            return await self.text_handler.handle_farewell(message)

        # 4. 默认文本处理（最低优先级）
        @self.router.route(
            name="text",
            condition=lambda msg: msg.has_text(),
            priority=10,
            description="处理普通文本消息"
        )
        async def handle_text(message: Message) -> Response:
            return await self.text_handler.handle(message)

        # 5. 兜底处理器
        @self.router.set_fallback
        async def handle_fallback(message: Message) -> Response:
            return Response(text="抱歉，我不知道如何处理这条消息")

        logger.info(f"[OK] 注册了 {len(self.router.routes)} 个路由")

    async def process_message(self, message: Message) -> Response:
        """
        处理消息

        Args:
            message: 消息对象

        Returns:
            响应对象
        """
        # 通过中间件链和路由器处理消息
        async def route_handler(msg: Message) -> Response:
            return await self.router.route_message(msg)

        response = await self.middleware.process(message, route_handler)
        return response

    def list_routes(self):
        """列出所有路由"""
        print("\n[Routes] 已注册的路由:")
        for route_info in self.router.list_routes():
            print(f"  * {route_info['name']} (优先级: {route_info['priority']})")
            if route_info['description']:
                print(f"    {route_info['description']}")

    def list_commands(self):
        """列出所有命令"""
        print("\n[Commands] 可用命令:")
        for cmd in self.command_handler.list_commands():
            print(f"  * {cmd}")


async def test_bot():
    """测试 Bot"""
    bot = XiaomiaoBot()

    # 显示信息
    bot.list_routes()
    bot.list_commands()

    # 创建测试消息
    test_messages = [
        Message(
            message_id="1",
            user=User(user_id=123, nickname="测试用户"),
            source=MessageSource.PRIVATE,
            text="你好",
        ),
        Message(
            message_id="2",
            user=User(user_id=123, nickname="测试用户"),
            source=MessageSource.PRIVATE,
            text="帮助",
        ),
        Message(
            message_id="3",
            user=User(user_id=123, nickname="测试用户"),
            source=MessageSource.PRIVATE,
            text="关于",
        ),
        Message(
            message_id="4",
            user=User(user_id=123, nickname="测试用户"),
            source=MessageSource.PRIVATE,
            text="再见",
        ),
    ]

    print("\n\n[Test] 测试消息处理:")
    print("=" * 50)

    for msg in test_messages:
        print(f"\n[Input] {msg.text}")
        response = await bot.process_message(msg)
        print(f"[Output] {response.text}")

    print("\n" + "=" * 50)


def main():
    """主函数"""
    logger.info("[Start] 启动 xiaomiao Bot (新架构)")

    # 运行测试
    asyncio.run(test_bot())

    logger.info("[Done] Bot 运行完成")


if __name__ == "__main__":
    main()
