@echo off
chcp 65001 >nul
title xiaomiaoAgent TUI - 终端对话界面
color 0A

echo ========================================
echo xiaomiaoAgent TUI 终端对话界面
echo ========================================
echo.
echo 启动中...
echo.

set "ROOT_DIR=%~dp0"
set "AGENT_DIR=%ROOT_DIR%xiaomiaoAgent"
set "AGENT_CONFIG=%ROOT_DIR%.cache\\agent\\nanobot\\config.json"

cd /d "%AGENT_DIR%"

REM 激活 conda 环境
call F:\Anaconda3\Scripts\activate.bat xiaomiao

REM 启动 TUI
python -m xiaomiao_agent agent --config "%AGENT_CONFIG%" --markdown --no-logs

pause
