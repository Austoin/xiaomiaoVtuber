@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   🎭 xiaomiaoVirtual 监控面板启动器
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 或激活 conda 环境
    pause
    exit /b 1
)

:: 检查端口 8888 是否被占用
netstat -ano | findstr ":8888" >nul
if not errorlevel 1 (
    echo ⚠️  警告: 端口 8888 已被占用
    echo.
    set /p CONTINUE="是否继续？(Y/N): "
    if /i "!CONTINUE!" neq "Y" (
        echo 已取消启动
        pause
        exit /b 0
    )
)

echo 📊 步骤 1/3: 安装依赖...
pip install aiohttp >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告: aiohttp 安装失败，尝试继续...
) else (
    echo ✓ 依赖安装完成
)

echo.
echo 📡 步骤 2/3: 启动监控 API...
echo    地址: http://127.0.0.1:8888
echo    端点: http://127.0.0.1:8888/api/status
echo.

:: 在新窗口启动 API
start "xiaomiaoVirtual 监控 API" /min python monitor-api.py

:: 等待 API 启动
timeout /t 2 /nobreak >nul

echo ✓ 监控 API 已启动
echo.
echo 🌐 步骤 3/3: 打开监控面板...

:: 打开浏览器
start "" "monitor-dashboard-enhanced.html"

echo ✓ 监控面板已打开
echo.
echo ========================================
echo   🎉 监控面板启动完成！
echo ========================================
echo.
echo 📖 使用说明:
echo    - 监控面板会自动检查服务状态
echo    - 点击"刷新状态"手动更新
echo    - 点击"开启自动刷新"每 5 秒自动检查
echo    - 连接线会根据依赖服务状态改变颜色
echo.
echo 💡 提示:
echo    - 绿色 = 运行正常
echo    - 黄色 = 需要注意
echo    - 红色 = 服务停止
echo.
echo ⚠️  关闭此窗口将停止监控 API
echo.
pause
