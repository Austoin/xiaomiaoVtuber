@echo off
chcp 65001 >nul
call "%~dp0web\monitoring\start-monitor-simple.cmd" %*
