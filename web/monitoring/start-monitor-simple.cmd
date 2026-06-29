@echo off
chcp 65001 >nul
cls
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

echo.
echo Starting xiaomiaoVirtual Monitor Dashboard...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install aiohttp >nul 2>&1

echo [2/3] Starting monitor API on port 8888...
start "Monitor API" /min python "%SCRIPT_DIR%monitor-api.py"

timeout /t 2 /nobreak >nul

echo [3/3] Opening dashboard in browser...
start "" "%SCRIPT_DIR%monitor-dashboard-enhanced.html"

echo.
echo Dashboard started successfully!
echo.
echo Usage:
echo   - Auto refresh: Click "Auto Refresh" button
echo   - Manual refresh: Click "Refresh" button
echo   - Status colors: Green=Running, Yellow=Warning, Red=Stopped
echo.
echo Close this window to stop the monitor API
echo.
pause
popd
