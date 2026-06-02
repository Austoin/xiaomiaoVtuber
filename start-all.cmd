@echo off
chcp 65001 >nul
setlocal EnableExtensions

set "ROOT_DIR=%~dp0"
set "XIAOMIAO_DIR=%ROOT_DIR%xiaomiao"
set "AUBOT_DIR=%ROOT_DIR%AuBot"
set "NANOBOT_CONFIG=%ROOT_DIR%nanobot\.nanobot\config.json"
set "NAPCAT_DIR=%XIAOMIAO_DIR%\NapCat.Shell.Windows.OneKey\NapCat.44498.Shell"
set "LAGRANGE_EXE=%XIAOMIAO_DIR%\Lagrange.OneBot.exe"
set "QQ_ACCOUNT=3994383071"
set "PROTOCOL_WAIT_SECONDS=10"
set "CHECK_ONLY=0"

if /I "%~1"=="--check" (
    set "CHECK_ONLY=1"
)

echo ========================================
echo   XiaoMiao unified launcher
echo ========================================
echo Root: %ROOT_DIR%
echo.

if not exist "%XIAOMIAO_DIR%\main.py" (
    echo [Error] Missing xiaomiao main.py: %XIAOMIAO_DIR%\main.py
    pause
    exit /b 1
)

if not exist "%NANOBOT_CONFIG%" (
    echo [Error] Missing nanobot config: %NANOBOT_CONFIG%
    pause
    exit /b 1
)

if not exist "%AUBOT_DIR%\package.json" (
    echo [Error] Missing AuBot package.json: %AUBOT_DIR%\package.json
    pause
    exit /b 1
)

echo [1/4] Starting QQ protocol...
if exist "%NAPCAT_DIR%\napcat.quick.bat" (
    if "%CHECK_ONLY%"=="0" start "QQ Protocol - NapCat" /D "%NAPCAT_DIR%" cmd /k "call napcat.quick.bat %QQ_ACCOUNT%"
    if "%CHECK_ONLY%"=="1" (
        echo       NapCat found.
    ) else (
        echo       NapCat launched. Please finish login if it asks for QR scan.
    )
) else if exist "%LAGRANGE_EXE%" (
    if "%CHECK_ONLY%"=="0" start "QQ Protocol - Lagrange" /D "%XIAOMIAO_DIR%" cmd /k "Lagrange.OneBot.exe"
    if "%CHECK_ONLY%"=="1" (
        echo       Lagrange found.
    ) else (
        echo       Lagrange launched. Please finish login if it asks for QR scan.
    )
) else (
    echo [Error] No QQ protocol found.
    echo         Expected NapCat: %NAPCAT_DIR%\napcat.quick.bat
    echo         Expected Lagrange: %LAGRANGE_EXE%
    pause
    exit /b 1
)

echo.
echo Waiting %PROTOCOL_WAIT_SECONDS%s for QQ protocol startup...
if "%CHECK_ONLY%"=="0" timeout /t %PROTOCOL_WAIT_SECONDS% /nobreak >nul

echo [2/4] Starting nanobot Agent API...
if "%CHECK_ONLY%"=="0" start "nanobot Agent API" /D "%ROOT_DIR%" cmd /k call conda activate xiaomiao ^&^& python -m nanobot serve --config "%NANOBOT_CONFIG%"

echo [3/4] Starting xiaomiao main.py and bridge...
if "%CHECK_ONLY%"=="0" start "xiaomiao main.py" /D "%XIAOMIAO_DIR%" cmd /k call conda activate xiaomiao ^&^& python main.py

echo [4/4] Starting AuBot stage-web...
if "%CHECK_ONLY%"=="0" start "AuBot stage-web" /D "%AUBOT_DIR%" cmd /k "pnpm dev:web"

echo.
echo ========================================
if "%CHECK_ONLY%"=="1" (
    echo Check passed. No windows were started.
) else (
    echo Started launch windows.
)
echo ========================================
echo.
echo Ports:
echo   QQ OneBot WebSocket: 127.0.0.1:5004
echo   xiaomiao bridge:     127.0.0.1:5519
echo   nanobot Agent API:   127.0.0.1:8900
echo.
echo If xiaomiao exits because QQ protocol is not ready,
echo finish QQ login first, then restart the "xiaomiao main.py" window.
echo.
if "%CHECK_ONLY%"=="0" pause
