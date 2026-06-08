@echo off
chcp 65001 >nul
setlocal EnableExtensions

set "ROOT_DIR=%~dp0"
set "XIAOMIAO_DIR=%ROOT_DIR%xiaomiao"
set "XIAOMIAOBOT_DIR=%ROOT_DIR%xiaomiaobot"
set "XIAOMIAO_AGENT_DIR=%ROOT_DIR%xiaomiaoAgent"
set "XIAOMIAO_AGENT_WEBUI_DIR=%XIAOMIAO_AGENT_DIR%\webui"
set "XIAOMIAO_AGENT_CONFIG=%XIAOMIAO_AGENT_DIR%\.nanobot\config.json"
set "XIAOMIAOBOT_STAGE_WEB_DIR=%XIAOMIAOBOT_DIR%\apps\stage-web"
set "NAPCAT_DIR=%XIAOMIAO_DIR%\NapCat.Shell.Windows.OneKey\NapCat.44498.Shell"
set "LAGRANGE_EXE=%XIAOMIAO_DIR%\Lagrange.OneBot.exe"
set "HEALTH_PS=%ROOT_DIR%scripts\start-all-health.ps1"
set "QQ_ACCOUNT=3994383071"
set "XIAOMIAOBOT_STAGE_WEB_PORT=5175"
set "WAIT_TIMEOUT_SECONDS=180"
set "QQ_WAIT_TIMEOUT_SECONDS=600"
set "CHECK_ONLY=0"
set "CHECK_FAILED=0"
set "NO_PROXY=127.0.0.1,localhost,::1"
set "no_proxy=127.0.0.1,localhost,::1"

set "CMD_AGENT_API=conda run --no-capture-output -n xiaomiao python -m xiaomiao_agent serve --config %XIAOMIAO_AGENT_CONFIG%"
set "CMD_AGENT_GATEWAY=conda run --no-capture-output -n xiaomiao python -m xiaomiao_agent gateway --config %XIAOMIAO_AGENT_CONFIG%"
set "CMD_XIAOMIAO_MAIN=conda run --no-capture-output -n xiaomiao python main.py"
set "CMD_XIAOMIAOBOT_WEB=pnpm exec vite --host 127.0.0.1 --port %XIAOMIAOBOT_STAGE_WEB_PORT%"
set "CMD_AGENT_WEBUI=npm run dev -- --host 127.0.0.1 --port 5174"

if /I "%~1"=="--check" set "CHECK_ONLY=1"

echo ========================================
echo   XiaoMiao unified launcher
echo ========================================
echo Root: %ROOT_DIR%
echo.

call :preflight
if errorlevel 1 exit /b 1

if "%CHECK_ONLY%"=="1" (
    call :check_services
    exit /b %errorlevel%
)

call :start_qq
if errorlevel 1 goto launch_failed

call :start_agent_api
if errorlevel 1 goto launch_failed

call :start_agent_gateway
if errorlevel 1 goto launch_failed

call :start_xiaomiao_main
if errorlevel 1 goto launch_failed

call :start_xiaomiaobot_web
if errorlevel 1 goto launch_failed

call :start_agent_webui
if errorlevel 1 goto launch_failed

goto launch_success

:preflight
if not exist "%HEALTH_PS%" (
    echo [Error] Missing health helper: %HEALTH_PS%
    pause
    exit /b 1
)
if not exist "%XIAOMIAO_DIR%\main.py" (
    echo [Error] Missing xiaomiao main.py: %XIAOMIAO_DIR%\main.py
    pause
    exit /b 1
)
if not exist "%XIAOMIAO_AGENT_CONFIG%" (
    echo [Error] Missing xiaomiaoAgent config: %XIAOMIAO_AGENT_CONFIG%
    pause
    exit /b 1
)
if not exist "%XIAOMIAOBOT_DIR%\package.json" (
    echo [Error] Missing xiaomiaobot package.json: %XIAOMIAOBOT_DIR%\package.json
    pause
    exit /b 1
)
if not exist "%XIAOMIAO_AGENT_WEBUI_DIR%\package.json" (
    echo [Error] Missing xiaomiaoAgent webui package.json: %XIAOMIAO_AGENT_WEBUI_DIR%\package.json
    pause
    exit /b 1
)
if not exist "%NAPCAT_DIR%\NapCatWinBootMain.exe" if not exist "%LAGRANGE_EXE%" (
    echo [Error] No QQ protocol found.
    echo         Expected NapCat: %NAPCAT_DIR%\NapCatWinBootMain.exe
    echo         Expected Lagrange: %LAGRANGE_EXE%
    pause
    exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" config-safe -ConfigPath "%XIAOMIAO_AGENT_CONFIG%"
if errorlevel 1 (
    pause
    exit /b 1
)
exit /b 0

:check_services
echo [Check] Current service state. No windows will be started.
echo.
call :check_port "QQ OneBot WebSocket" 5004
call :check_http "xiaomiaoAgent API" 8900 "http://127.0.0.1:8900/health" "status"
echo [xiaomiaoAgent gateway]
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" check -Kind Gateway -Name "xiaomiaoAgent gateway" -Port 8765 -BaseUrl "http://127.0.0.1:8765"
if errorlevel 1 set "CHECK_FAILED=1"
echo.
call :check_xiaomiao "xiaomiao main.py, bridge, and QQ listener" 5519 "http://127.0.0.1:5519/v1/xiaomiao/status" "xiaomiao-desktop-bridge"
call :check_http "xiaomiaobot web" %XIAOMIAOBOT_STAGE_WEB_PORT% "http://127.0.0.1:%XIAOMIAOBOT_STAGE_WEB_PORT%/" "xiaomiao"
call :check_http "xiaomiaoAgent WebUI" 5174 "http://127.0.0.1:5174/" "xiaomiaoAgent"
echo.
echo ========================================
if "%CHECK_FAILED%"=="1" (
    echo Check failed. See the failed health check above.
    echo ========================================
    exit /b 1
)
echo Check passed. No windows were started.
echo ========================================
exit /b 0

:check_port
echo [%~1]
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" check -Kind Port -Name "%~1" -Port %~2
if errorlevel 1 set "CHECK_FAILED=1"
echo.
exit /b 0

:check_http
echo [%~1]
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" check -Kind Http -Name "%~1" -Port %~2 -Url "%~3" -Needle "%~4"
if errorlevel 1 set "CHECK_FAILED=1"
echo.
exit /b 0

:check_xiaomiao
echo [%~1]
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" check -Kind Xiaomiao -Name "%~1" -Port %~2 -Url "%~3" -Needle "%~4"
if errorlevel 1 set "CHECK_FAILED=1"
echo.
exit /b 0

:assert_free
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" assert-free -Name "%~1" -Port %~2
exit /b %errorlevel%

:wait_port
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" wait -Kind Port -Name "%~1" -Port %~2 -TimeoutSeconds %WAIT_TIMEOUT_SECONDS%
exit /b %errorlevel%

:wait_http
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" wait -Kind Http -Name "%~1" -Port %~2 -Url "%~3" -Needle "%~4" -TimeoutSeconds %WAIT_TIMEOUT_SECONDS%
exit /b %errorlevel%

:wait_xiaomiao
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" wait -Kind Xiaomiao -Name "%~1" -Port %~2 -Url "%~3" -Needle "%~4" -TimeoutSeconds %WAIT_TIMEOUT_SECONDS%
exit /b %errorlevel%

:wait_gateway
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" wait -Kind Gateway -Name "%~1" -Port %~2 -BaseUrl "%~3" -TimeoutSeconds %WAIT_TIMEOUT_SECONDS%
exit /b %errorlevel%

:start_qq
echo [1/6] Starting QQ protocol...
echo       QQ protocol terminal stays visible for login.
echo       If the terminal QR code is hard to scan, open NapCat WebUI:
echo       http://127.0.0.1:6099
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" is-open -Port 5004 >nul 2>nul
if not errorlevel 1 (
    echo       QQ OneBot WebSocket already listening on 127.0.0.1:5004.
    echo       Reusing the existing QQ protocol process.
    echo       Close QQ/NapCat first if you need a fresh visible QQ terminal.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" check -Kind Port -Name "QQ OneBot WebSocket" -Port 5004
    exit /b %errorlevel%
)
if exist "%NAPCAT_DIR%\NapCatWinBootMain.exe" (
    start "QQ Protocol - NapCat" /D "%NAPCAT_DIR%" powershell -NoProfile -ExecutionPolicy Bypass -NoExit -Command "try { $raw = $Host.UI.RawUI; $raw.BufferSize = New-Object Management.Automation.Host.Size 180, 3000; $raw.WindowSize = New-Object Management.Automation.Host.Size 180, 45 } catch {}; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $OutputEncoding = [System.Text.Encoding]::UTF8; & '.\NapCatWinBootMain.exe' '%QQ_ACCOUNT%'"
) else (
    start "QQ Protocol - Lagrange" /D "%XIAOMIAO_DIR%" powershell -NoProfile -ExecutionPolicy Bypass -NoExit -Command "try { $raw = $Host.UI.RawUI; $raw.BufferSize = New-Object Management.Automation.Host.Size 180, 3000; $raw.WindowSize = New-Object Management.Automation.Host.Size 180, 45 } catch {}; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $OutputEncoding = [System.Text.Encoding]::UTF8; & '.\Lagrange.OneBot.exe'"
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%HEALTH_PS%" wait -Kind Port -Name "QQ OneBot WebSocket" -Port 5004 -TimeoutSeconds %QQ_WAIT_TIMEOUT_SECONDS%
exit /b %errorlevel%

:start_agent_api
echo.
echo [2/6] Starting xiaomiaoAgent API...
call :assert_free "xiaomiaoAgent API" 8900
if errorlevel 1 exit /b 1
start "xiaomiaoAgent API" /min /D "%XIAOMIAO_AGENT_DIR%" powershell -NoProfile -ExecutionPolicy Bypass -NoExit -Command "%CMD_AGENT_API%"
call :wait_http "xiaomiaoAgent API" 8900 "http://127.0.0.1:8900/health" "status"
exit /b %errorlevel%

:start_agent_gateway
echo.
echo [3/6] Starting xiaomiaoAgent gateway...
call :assert_free "xiaomiaoAgent gateway" 8765
if errorlevel 1 exit /b 1
start "xiaomiaoAgent gateway" /min /D "%XIAOMIAO_AGENT_DIR%" powershell -NoProfile -ExecutionPolicy Bypass -NoExit -Command "%CMD_AGENT_GATEWAY%"
call :wait_gateway "xiaomiaoAgent gateway" 8765 "http://127.0.0.1:8765"
exit /b %errorlevel%

:start_xiaomiao_main
echo.
echo [4/6] Starting xiaomiao main.py and bridge...
call :assert_free "xiaomiao main.py and bridge" 5519
if errorlevel 1 exit /b 1
start "xiaomiao main.py" /min /D "%XIAOMIAO_DIR%" powershell -NoProfile -ExecutionPolicy Bypass -NoExit -Command "%CMD_XIAOMIAO_MAIN%"
call :wait_xiaomiao "xiaomiao main.py, bridge, and QQ listener" 5519 "http://127.0.0.1:5519/v1/xiaomiao/status" "xiaomiao-desktop-bridge"
exit /b %errorlevel%

:start_xiaomiaobot_web
echo.
echo [5/6] Starting xiaomiaobot web...
call :assert_free "xiaomiaobot web" %XIAOMIAOBOT_STAGE_WEB_PORT%
if errorlevel 1 exit /b 1
start "xiaomiaobot web" /min /D "%XIAOMIAOBOT_STAGE_WEB_DIR%" powershell -NoProfile -ExecutionPolicy Bypass -NoExit -Command "%CMD_XIAOMIAOBOT_WEB%"
call :wait_http "xiaomiaobot web" %XIAOMIAOBOT_STAGE_WEB_PORT% "http://127.0.0.1:%XIAOMIAOBOT_STAGE_WEB_PORT%/" "xiaomiao"
exit /b %errorlevel%

:start_agent_webui
echo.
echo [6/6] Starting xiaomiaoAgent WebUI...
call :assert_free "xiaomiaoAgent WebUI" 5174
if errorlevel 1 exit /b 1
start "xiaomiaoAgent WebUI" /min /D "%XIAOMIAO_AGENT_WEBUI_DIR%" powershell -NoProfile -ExecutionPolicy Bypass -NoExit -Command "%CMD_AGENT_WEBUI%"
call :wait_http "xiaomiaoAgent WebUI" 5174 "http://127.0.0.1:5174/" "xiaomiaoAgent"
exit /b %errorlevel%

:launch_failed
echo.
echo ========================================
echo Launch stopped. Later services were not opened.
echo Fix the failed service above, then run start-all.cmd again.
echo ========================================
pause
exit /b 1

:launch_success
echo.
echo ========================================
echo All required services were started in minimized terminals.
echo ========================================
echo.
echo Ports:
echo   QQ OneBot WebSocket:   127.0.0.1:5004
echo   xiaomiao bridge:       127.0.0.1:5519
echo   xiaomiaoAgent API:     127.0.0.1:8900
echo   xiaomiaoAgent gateway: 127.0.0.1:8765
echo   xiaomiaoAgent WebUI:   http://127.0.0.1:5174
echo   xiaomiaobot web:       http://127.0.0.1:%XIAOMIAOBOT_STAGE_WEB_PORT%
echo.
pause
exit /b 0
