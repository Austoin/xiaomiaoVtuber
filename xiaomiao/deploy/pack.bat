@echo off
setlocal

echo ============================================
echo   XiaoMiao QQ Bot - Pack Script
echo ============================================
echo.

cd /d "%~dp0.."
set "ZIP_FILE=%~dp0xiaomiaoVirtual.zip"
set "TEMP_ZIP=%CD%\xiaomiaoVirtual.tmp.zip"
set "BOT_FILES=main.py agent_backend.py bridge_event_store.py console_output.py desktop_bridge.py GoogleAI.py prerequisites.py qq_agent_bridge.py qq_agent_tools.py qq_permissions.py qq_workspace.py Quote.py SearchOnline.py unified_config.py config.json requirements.txt start.bat assets temps runtime deploy"

echo Source: %CD%
echo Output: %ZIP_FILE%
echo.

:: Delete old zip
if exist "%ZIP_FILE%" del /f /q "%ZIP_FILE%"
if exist "%TEMP_ZIP%" del /f /q "%TEMP_ZIP%"

:: Create placeholder in temps if empty
if not exist "temps\*" echo. > "temps\.gitkeep"

:: Check 7z
where 7z >nul 2>&1
if %errorlevel% equ 0 (
    echo Using 7-Zip...
    7z a -tzip "%ZIP_FILE%" %BOT_FILES% -xr!__pycache__ -xr!*.pyc -xr!xiaomiaoVirtual.zip
    goto :check
)

:: Use PowerShell Compress-Archive
echo Using PowerShell Compress-Archive...
powershell -NoProfile -Command "$paths = '%BOT_FILES%'.Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries); Compress-Archive -Path $paths -DestinationPath '%TEMP_ZIP%' -Force"
if exist "%TEMP_ZIP%" move /y "%TEMP_ZIP%" "%ZIP_FILE%" >nul

:check
echo.
echo ============================================
if exist "%ZIP_FILE%" (
    for %%A in ("%ZIP_FILE%") do echo [OK] Created: %%~nxA ^(%%~zA bytes^)
) else (
    echo [ERROR] Failed to create zip
)
echo ============================================
pause
