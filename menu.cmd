@echo off
chcp 65001 >nul
setlocal EnableExtensions

set "ROOT_DIR=%~dp0"
set "SCRIPTS_DIR=%ROOT_DIR%scripts"

if /I "%~1"=="--help" goto help
if /I "%~1"=="-h" goto help
if /I "%~1"=="help" goto help
if /I "%~1"=="list" goto list
if /I "%~1"=="all" goto start_all
if /I "%~1"=="check" goto start_check
if /I "%~1"=="tui" goto start_tui
if /I "%~1"=="monitor" goto start_monitor
if /I "%~1"=="monitor-simple" goto start_monitor_simple
if /I "%~1"=="setup" goto setup_env
if /I "%~1"=="setup-check" goto setup_check
if not "%~1"=="" goto unknown

:menu
cls
echo ========================================
echo   XiaoMiao launcher menu
echo ========================================
echo Root: %ROOT_DIR%
echo.
echo   1. Start all services
echo   2. Check service status
echo   3. Start xiaomiaoAgent TUI
echo   4. Start monitoring dashboard
echo   5. Start simple monitoring dashboard
echo   6. Run environment setup
echo   7. Check environment setup
echo   0. Exit
echo.
set "CHOICE="
set /p "CHOICE=Select an option: "

if "%CHOICE%"=="1" goto start_all_interactive
if "%CHOICE%"=="2" goto start_check_interactive
if "%CHOICE%"=="3" goto start_tui_interactive
if "%CHOICE%"=="4" goto start_monitor_interactive
if "%CHOICE%"=="5" goto start_monitor_simple_interactive
if "%CHOICE%"=="6" goto setup_env_interactive
if "%CHOICE%"=="7" goto setup_check_interactive
if "%CHOICE%"=="0" exit /b 0

echo.
echo Unknown option: %CHOICE%
pause
goto menu

:list
echo all
echo check
echo tui
echo monitor
echo monitor-simple
echo setup
echo setup-check
exit /b 0

:help
echo Usage:
echo   menu.cmd
echo   menu.cmd all
echo   menu.cmd check
echo   menu.cmd tui
echo   menu.cmd monitor
echo   menu.cmd monitor-simple
echo   menu.cmd setup
echo   menu.cmd setup-check
echo   menu.cmd list
echo.
echo npm/pnpm shortcuts:
echo   pnpm start
echo   pnpm run start:all
echo   pnpm run start:check
echo   pnpm run tui
echo   pnpm run monitor
echo   pnpm run monitor:simple
echo   pnpm run setup
echo   pnpm run setup:check
exit /b 0

:unknown
echo Unknown command: %~1
echo.
goto help

:start_all
call "%SCRIPTS_DIR%\start-all.cmd" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:start_check
call "%SCRIPTS_DIR%\start-all.cmd" --check %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:start_tui
call "%SCRIPTS_DIR%\start-tui.cmd" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:start_monitor
call "%SCRIPTS_DIR%\start-monitor.cmd" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:start_monitor_simple
call "%SCRIPTS_DIR%\start-monitor-simple.cmd" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:setup_env
call "%SCRIPTS_DIR%\setup-env.cmd" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:setup_check
call "%SCRIPTS_DIR%\setup-env.cmd" --check %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:start_all_interactive
call "%SCRIPTS_DIR%\start-all.cmd"
goto return_to_menu

:start_check_interactive
call "%SCRIPTS_DIR%\start-all.cmd" --check
goto return_to_menu

:start_tui_interactive
call "%SCRIPTS_DIR%\start-tui.cmd"
goto return_to_menu

:start_monitor_interactive
call "%SCRIPTS_DIR%\start-monitor.cmd"
goto return_to_menu

:start_monitor_simple_interactive
call "%SCRIPTS_DIR%\start-monitor-simple.cmd"
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
