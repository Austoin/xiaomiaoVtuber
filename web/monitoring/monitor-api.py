"""
xiaomiaoVirtual 服务监控 - 后端服务
提供服务状态检查的 API
"""
import asyncio
import aiohttp
from aiohttp import web
import json
from datetime import datetime

# 服务配置
SERVICES = [
    {
        "id": "napcat",
        "name": "NapCat (QQ协议)",
        "port": "5004",
        "check_url": "http://127.0.0.1:5004",
        "method": "tcp"
    },
    {
        "id": "agent-api",
        "name": "xiaomiaoAgent API",
        "port": "8900",
        "check_url": "http://127.0.0.1:8900/health",
        "method": "http"
    },
    {
        "id": "xiaomiao-bridge",
        "name": "小喵桌面桥接",
        "port": "5519",
        "check_url": "http://127.0.0.1:5519",
        "method": "tcp"
    },
    {
        "id": "stage-web",
        "name": "xiaomiaobot Web界面",
        "port": "5175",
        "check_url": "http://127.0.0.1:5175",
        "method": "http"
    }
]

async def check_tcp_port(host, port, timeout=2):
    """检查 TCP 端口是否开放"""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def check_http_url(url, timeout=2):
    """检查 HTTP URL 是否可访问"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                return resp.status in [200, 201, 204]
    except:
        return False

async def check_service_status(service):
    """检查单个服务状态"""
    try:
        if service["method"] == "http":
            is_running = await check_http_url(service["check_url"])
        else:
            host = "127.0.0.1"
            port = int(service["port"])
            is_running = await check_tcp_port(host, port)

        return {
            "id": service["id"],
            "name": service["name"],
            "port": service["port"],
            "status": "running" if is_running else "stopped",
            "checked_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "id": service["id"],
            "name": service["name"],
            "port": service["port"],
            "status": "error",
            "error": str(e),
            "checked_at": datetime.now().isoformat()
        }

async def check_all_services(request):
    """检查所有服务状态"""
    tasks = [check_service_status(service) for service in SERVICES]
    results = await asyncio.gather(*tasks)

    return web.json_response({
        "services": results,
        "timestamp": datetime.now().isoformat()
    })

async def handle_cors(request):
    """处理 CORS"""
    return web.Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

def create_app():
    app = web.Application()

    # 添加 CORS 中间件
    @web.middleware
    async def cors_middleware(request, handler):
        if request.method == "OPTIONS":
            return await handle_cors(request)

        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    app.middlewares.append(cors_middleware)

    # 路由
    app.router.add_get('/api/status', check_all_services)
    app.router.add_options('/api/status', handle_cors)

    return app

if __name__ == '__main__':
    print("🚀 启动服务监控 API...")
    print("📊 访问地址: http://127.0.0.1:8888")
    print("🔗 API 端点: http://127.0.0.1:8888/api/status")
    app = create_app()
    web.run_app(app, host='127.0.0.1', port=8888)
