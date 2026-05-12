@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo        Jianer QQ Bot Launcher
echo ========================================
echo.

if exist "NapCat.Shell.Windows.OneKey\NapCat.44498.Shell\napcat.bat" (
    echo [1/2] Starting NapCat...
    cd /d "%~dp0NapCat.Shell.Windows.OneKey\NapCat.44498.Shell"
    start "NapCat" cmd /k "napcat.quick.bat 3994383071"
    cd /d "%~dp0"
    echo.
    echo Please wait for NapCat to login...
    echo Press any key after you see "WebSocket: 127.0.0.1:5004"
    pause
    goto :start_bot
)

if exist "Lagrange.OneBot.exe" (
    echo [1/2] Starting Lagrange.OneBot...
    start "Lagrange" cmd /k "Lagrange.OneBot.exe"
    echo Press any key after login success...
    pause
    goto :start_bot
)

echo [Error] No protocol framework found!
pause
exit /b 1

:start_bot
echo.
echo [2/2] Starting Jianer Bot...
start "Jianer Bot" cmd /k "python main.py"
echo.
echo ========================================
echo  Started successfully!
echo ========================================
echo.
pause
