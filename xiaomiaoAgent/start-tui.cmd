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

cd /d f:\xiaomiaoVirtual\xiaomiaoAgent

REM 激活 conda 环境
call F:\Anaconda3\Scripts\activate.bat xiaomiao

REM 启动 TUI
python -m xiaomiao_agent agent --config .nanobot\config.json --markdown --no-logs

pause
