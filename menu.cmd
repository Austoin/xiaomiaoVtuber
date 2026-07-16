@echo off
chcp 65001 >nul
setlocal EnableExtensions

set "ROOT_DIR=%~dp0"
set "SCRIPTS_DIR=%ROOT_DIR%scripts"
set "XIAOMIAO_DIR=%ROOT_DIR%xiaomiao"
set "XIAOMIAOBOT_DIR=%ROOT_DIR%xiaomiaobot"
set "XIAOMIAO_AGENT_DIR=%ROOT_DIR%xiaomiaoAgent"
set "MINECRAFT_DIR=%XIAOMIAOBOT_DIR%\services\minecraft"
set "TWITTER_DIR=%XIAOMIAOBOT_DIR%\services\twitter-services"
set "AGENT_CONFIG=%ROOT_DIR%.cache\agent\nanobot\config.json"

set "COMMAND=%~1"
set "FORWARDED_ARGS="
if not "%~1"=="" (
    for /f "tokens=1,* delims= " %%A in ("%*") do set "FORWARDED_ARGS=%%B"
)

if /I "%COMMAND%"=="--help" goto help
if /I "%COMMAND%"=="-h" goto help
if /I "%COMMAND%"=="help" goto help
if /I "%COMMAND%"=="list" goto list
if /I "%COMMAND%"=="all" goto start_all
if /I "%COMMAND%"=="check" goto start_check
if /I "%COMMAND%"=="qq" goto start_qq
if /I "%COMMAND%"=="xiaomiao" goto start_qq
if /I "%COMMAND%"=="tui" goto start_tui
if /I "%COMMAND%"=="agent" goto start_agent
if /I "%COMMAND%"=="agent-api" goto start_agent_api
if /I "%COMMAND%"=="agent-gateway" goto start_agent_gateway
if /I "%COMMAND%"=="agent-webui" goto start_agent_webui
if /I "%COMMAND%"=="bot-minecraft" goto bot_minecraft
if /I "%COMMAND%"=="bot-twitter" goto bot_twitter
if /I "%COMMAND%"=="bot-script" goto bot_script
if /I "%COMMAND%"=="bot-web" goto bot_web
if /I "%COMMAND%"=="bot-tamagotchi" goto bot_tamagotchi
if /I "%COMMAND%"=="bot-test" goto bot_test
if /I "%COMMAND%"=="bot-typecheck" goto bot_typecheck
if /I "%COMMAND%"=="bot-build" goto bot_build
if /I "%COMMAND%"=="test-xiaomiao" goto test_xiaomiao
if /I "%COMMAND%"=="test-agent-config" goto test_agent_config
if /I "%COMMAND%"=="setup" goto setup_env
if /I "%COMMAND%"=="setup-check" goto setup_check
if not "%COMMAND%"=="" goto unknown

:menu
cls
echo ========================================
echo   XiaoMiao launcher menu
echo ========================================
echo Root: %ROOT_DIR%
echo.
echo   1. Start all services
echo   2. Check service status
echo   3. Start QQ adapter
echo   4. Start xiaomiaoAgent TUI
echo   5. Start xiaomiaoAgent API
echo   6. Start xiaomiaoAgent Gateway
echo   7. Start xiaomiaoAgent WebUI
echo   8. Start Minecraft service
echo   9. Start Twitter MCP service
echo  10. Start xiaomiaobot stage-web
echo  11. Run xiaomiao tests
echo  12. Run Agent config tests
echo  13. Run environment setup
echo  14. Check environment setup
echo   0. Exit
echo.
set "CHOICE="
set /p "CHOICE=Select an option: "

if "%CHOICE%"=="1" goto start_all_interactive
if "%CHOICE%"=="2" goto start_check_interactive
if "%CHOICE%"=="3" goto start_qq_interactive
if "%CHOICE%"=="4" goto start_tui_interactive
if "%CHOICE%"=="5" goto start_agent_api_interactive
if "%CHOICE%"=="6" goto start_agent_gateway_interactive
if "%CHOICE%"=="7" goto start_agent_webui_interactive
if "%CHOICE%"=="8" goto bot_minecraft_interactive
if "%CHOICE%"=="9" goto bot_twitter_interactive
if "%CHOICE%"=="10" goto bot_web_interactive
if "%CHOICE%"=="11" goto test_xiaomiao_interactive
if "%CHOICE%"=="12" goto test_agent_config_interactive
if "%CHOICE%"=="13" goto setup_env_interactive
if "%CHOICE%"=="14" goto setup_check_interactive
if "%CHOICE%"=="0" exit /b 0

echo.
echo Unknown option: %CHOICE%
pause
goto menu

:list
echo all
echo check
echo qq
echo xiaomiao
echo tui
echo agent
echo agent-api
echo agent-gateway
echo agent-webui
echo bot-minecraft
echo bot-twitter
echo bot-script
echo bot-web
echo bot-tamagotchi
echo bot-test
echo bot-typecheck
echo bot-build
echo test-xiaomiao
echo test-agent-config
echo setup
echo setup-check
exit /b 0

:help
echo Usage:
echo   menu.cmd
echo   menu.cmd ^<command^> [args]
echo.
echo Service commands:
echo   all                 Start QQ, Agent API, QQ adapter, and stage-web
echo   check               Check service status without starting windows
echo   qq                  Start xiaomiao QQ adapter
echo   tui                 Start xiaomiaoAgent TUI
echo   agent               Run xiaomiaoAgent direct CLI with shared config
echo   agent-api           Start OpenAI-compatible Agent API
echo   agent-gateway       Start xiaomiaoAgent gateway
echo   agent-webui         Start embedded xiaomiaoAgent WebUI
echo.
echo xiaomiaobot commands:
echo   bot-script SCRIPT   Run any xiaomiaobot package.json script
echo   bot-web             Run stage-web dev server
echo   bot-tamagotchi      Run stage-tamagotchi dev server
echo   bot-minecraft       Start the Minecraft integration
echo   bot-twitter         Start the Twitter MCP integration
echo   bot-test            Run xiaomiaobot tests
echo   bot-typecheck       Run xiaomiaobot typecheck
echo   bot-build           Build xiaomiaobot apps/packages
echo.
echo Maintenance commands:
echo   test-xiaomiao       Run xiaomiao Python tests
echo   test-agent-config   Run Agent config path tests
echo   setup               Run environment setup
echo   setup-check         Check environment setup
echo   list                Print command names
echo.
echo pnpm shortcuts:
echo   pnpm start
echo   pnpm run qq
echo   pnpm run agent:api
echo   pnpm run bot:web
echo   pnpm run bot:knip
echo   pnpm run test:xiaomiao
exit /b 0

:unknown
echo Unknown command: %COMMAND%
echo.
goto help

:start_all
call "%SCRIPTS_DIR%\start-all.cmd" %FORWARDED_ARGS%
exit /b %errorlevel%

:start_check
call "%SCRIPTS_DIR%\start-all.cmd" --check %FORWARDED_ARGS%
exit /b %errorlevel%

:start_qq
call :require_file "%XIAOMIAO_DIR%\main.py"
if errorlevel 1 exit /b 1
call conda run --no-capture-output -n xiaomiao python "%XIAOMIAO_DIR%\main.py" %FORWARDED_ARGS%
exit /b %errorlevel%

:start_tui
call "%SCRIPTS_DIR%\start-tui.cmd" %FORWARDED_ARGS%
exit /b %errorlevel%

:start_agent
call :require_file "%XIAOMIAO_AGENT_DIR%\xiaomiao_agent\__main__.py"
if errorlevel 1 exit /b 1
pushd "%XIAOMIAO_AGENT_DIR%"
call conda run --no-capture-output -n xiaomiao python -m xiaomiao_agent agent --config "%AGENT_CONFIG%" %FORWARDED_ARGS%
set "EXIT_CODE=%errorlevel%"
popd
exit /b %EXIT_CODE%

:start_agent_api
call :require_file "%XIAOMIAO_AGENT_DIR%\xiaomiao_agent\__main__.py"
if errorlevel 1 exit /b 1
pushd "%XIAOMIAO_AGENT_DIR%"
call conda run --no-capture-output -n xiaomiao python -m xiaomiao_agent serve --config "%AGENT_CONFIG%" %FORWARDED_ARGS%
set "EXIT_CODE=%errorlevel%"
popd
exit /b %EXIT_CODE%

:start_agent_gateway
call :require_file "%XIAOMIAO_AGENT_DIR%\xiaomiao_agent\__main__.py"
if errorlevel 1 exit /b 1
pushd "%XIAOMIAO_AGENT_DIR%"
call conda run --no-capture-output -n xiaomiao python -m xiaomiao_agent gateway --config "%AGENT_CONFIG%" %FORWARDED_ARGS%
set "EXIT_CODE=%errorlevel%"
popd
exit /b %EXIT_CODE%

:start_agent_webui
call :require_file "%XIAOMIAO_AGENT_DIR%\xiaomiao_agent\__main__.py"
if errorlevel 1 exit /b 1
pushd "%XIAOMIAO_AGENT_DIR%"
call conda run --no-capture-output -n xiaomiao python -m xiaomiao_agent webui --config "%AGENT_CONFIG%" %FORWARDED_ARGS%
set "EXIT_CODE=%errorlevel%"
popd
exit /b %EXIT_CODE%

:bot_minecraft
call :require_file "%MINECRAFT_DIR%\package.json"
if errorlevel 1 exit /b 1
call pnpm --dir "%MINECRAFT_DIR%" run start -- %FORWARDED_ARGS%
exit /b %errorlevel%

:bot_twitter
call :require_file "%TWITTER_DIR%\package.json"
if errorlevel 1 exit /b 1
call pnpm --dir "%TWITTER_DIR%" run dev -- %FORWARDED_ARGS%
exit /b %errorlevel%

:bot_script
call :require_file "%XIAOMIAOBOT_DIR%\package.json"
if errorlevel 1 exit /b 1
if "%~2"=="" (
    echo [Error] Missing xiaomiaobot script name.
    echo Usage: menu.cmd bot-script ^<script^> [args]
    exit /b 1
)
set "BOT_SCRIPT=%~2"
set "BOT_SCRIPT_ARGS="
for /f "tokens=1,2,* delims= " %%A in ("%*") do set "BOT_SCRIPT_ARGS=%%C"
call pnpm --dir "%XIAOMIAOBOT_DIR%" %BOT_SCRIPT% %BOT_SCRIPT_ARGS%
exit /b %errorlevel%

:bot_web
call :require_file "%XIAOMIAOBOT_DIR%\package.json"
if errorlevel 1 exit /b 1
call pnpm --dir "%XIAOMIAOBOT_DIR%" run dev:web -- %FORWARDED_ARGS%
exit /b %errorlevel%

:bot_tamagotchi
call :require_file "%XIAOMIAOBOT_DIR%\package.json"
if errorlevel 1 exit /b 1
call pnpm --dir "%XIAOMIAOBOT_DIR%" run dev:tamagotchi -- %FORWARDED_ARGS%
exit /b %errorlevel%

:bot_test
call :require_file "%XIAOMIAOBOT_DIR%\package.json"
if errorlevel 1 exit /b 1
call pnpm --dir "%XIAOMIAOBOT_DIR%" exec vitest run %FORWARDED_ARGS%
exit /b %errorlevel%

:bot_typecheck
call :require_file "%XIAOMIAOBOT_DIR%\package.json"
if errorlevel 1 exit /b 1
call pnpm --dir "%XIAOMIAOBOT_DIR%" run typecheck -- %FORWARDED_ARGS%
exit /b %errorlevel%

:bot_build
call :require_file "%XIAOMIAOBOT_DIR%\package.json"
if errorlevel 1 exit /b 1
call pnpm --dir "%XIAOMIAOBOT_DIR%" run build -- %FORWARDED_ARGS%
exit /b %errorlevel%

:test_xiaomiao
call python -m pytest test/xiaomiao %FORWARDED_ARGS%
exit /b %errorlevel%

:test_agent_config
pushd "%XIAOMIAO_AGENT_DIR%"
call uv run pytest tests/config/test_config_paths.py -q %FORWARDED_ARGS%
set "EXIT_CODE=%errorlevel%"
popd
exit /b %EXIT_CODE%

:setup_env
call "%SCRIPTS_DIR%\setup-env.cmd" %FORWARDED_ARGS%
exit /b %errorlevel%

:setup_check
call "%SCRIPTS_DIR%\setup-env.cmd" --check %FORWARDED_ARGS%
exit /b %errorlevel%

:start_all_interactive
call "%SCRIPTS_DIR%\start-all.cmd"
goto return_to_menu

:start_check_interactive
call "%SCRIPTS_DIR%\start-all.cmd" --check
goto return_to_menu

:start_qq_interactive
call conda run --no-capture-output -n xiaomiao python "%XIAOMIAO_DIR%\main.py"
goto return_to_menu

:start_tui_interactive
call "%SCRIPTS_DIR%\start-tui.cmd"
goto return_to_menu

:start_agent_api_interactive
pushd "%XIAOMIAO_AGENT_DIR%"
call conda run --no-capture-output -n xiaomiao python -m xiaomiao_agent serve --config "%AGENT_CONFIG%"
popd
goto return_to_menu

:start_agent_gateway_interactive
pushd "%XIAOMIAO_AGENT_DIR%"
call conda run --no-capture-output -n xiaomiao python -m xiaomiao_agent gateway --config "%AGENT_CONFIG%"
popd
goto return_to_menu

:start_agent_webui_interactive
call "%~f0" agent-webui
goto return_to_menu

:bot_minecraft_interactive
call "%~f0" bot-minecraft
goto return_to_menu

:bot_twitter_interactive
call "%~f0" bot-twitter
goto return_to_menu

:bot_web_interactive
call pnpm --dir "%XIAOMIAOBOT_DIR%" run dev:web
goto return_to_menu

:test_xiaomiao_interactive
call python -m pytest test/xiaomiao
goto return_to_menu

:test_agent_config_interactive
pushd "%XIAOMIAO_AGENT_DIR%"
call uv run pytest tests/config/test_config_paths.py -q
popd
goto return_to_menu

:setup_env_interactive
call "%SCRIPTS_DIR%\setup-env.cmd"
goto return_to_menu

:setup_check_interactive
call "%SCRIPTS_DIR%\setup-env.cmd" --check
goto return_to_menu

:return_to_menu
echo.
pause
goto menu

:require_file
if not exist "%~1" (
    echo [Error] Missing required file: %~1
    exit /b 1
)
exit /b 0
