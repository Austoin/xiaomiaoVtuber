@echo off
chcp 65001 >nul
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT_DIR=%%~fI\"
call "%ROOT_DIR%web\monitoring\start-monitor-simple.cmd" %*
