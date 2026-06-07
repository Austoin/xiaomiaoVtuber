@echo off
chcp 65001 >nul
setlocal EnableExtensions

set "ROOT_DIR=%~dp0"
set "XIAOMIAO_DIR=%ROOT_DIR%xiaomiao"
set "XIAOMIAO_AGENT_DIR=%ROOT_DIR%xiaomiaoAgent"
set "XIAOMIAO_AGENT_WEBUI_DIR=%XIAOMIAO_AGENT_DIR%\webui"
set "XIAOMIAOBOT_DIR=%ROOT_DIR%xiaomiaobot"
set "ROOT_CONFIG=%ROOT_DIR%config.json"
set "ROOT_CONFIG_EXAMPLE=%ROOT_DIR%config.example.json"
set "XIAOMIAO_CONFIG=%XIAOMIAO_DIR%\config.json"
set "XIAOMIAO_AGENT_CONFIG=%XIAOMIAO_AGENT_DIR%\.nanobot\config.json"
set "XIAOMIAO_AGENT_WORKSPACE=%XIAOMIAO_AGENT_DIR%\.nanobot\workspace"
set "CHECK_ONLY=0"
set "YES=0"
set "SKIP_PYTHON=0"
set "SKIP_NODE=0"
set "SKIP_WEBUI=0"
set "FAILED=0"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--check" (
    set "CHECK_ONLY=1"
    shift
    goto parse_args
)
if /I "%~1"=="--yes" (
    set "YES=1"
    shift
    goto parse_args
)
if /I "%~1"=="-y" (
    set "YES=1"
    shift
    goto parse_args
)
if /I "%~1"=="--skip-python" (
    set "SKIP_PYTHON=1"
    shift
    goto parse_args
)
if /I "%~1"=="--skip-node" (
    set "SKIP_NODE=1"
    shift
    goto parse_args
)
if /I "%~1"=="--skip-webui" (
    set "SKIP_WEBUI=1"
    shift
    goto parse_args
)
if /I "%~1"=="--help" goto usage_ok
if /I "%~1"=="-h" goto usage_ok
echo [Error] Unknown option: %~1
echo.
goto usage_error

:args_done
echo ========================================
echo   XiaoMiao environment setup
echo ========================================
echo Root: %ROOT_DIR%
echo.

call :check_layout
if errorlevel 1 exit /b 1

call :check_required_commands
if errorlevel 1 exit /b 1

if "%CHECK_ONLY%"=="1" (
    call :check_current_state
    exit /b %errorlevel%
)

call :ensure_workspace_dirs
if errorlevel 1 goto failed

if "%SKIP_PYTHON%"=="0" (
    call :setup_python
    if errorlevel 1 goto failed
) else (
    echo [Skip] Python dependencies.
)

if "%SKIP_NODE%"=="0" (
    call :setup_node
    if errorlevel 1 goto failed
) else (
    echo [Skip] Node / pnpm dependencies.
)

call :ensure_configs
if errorlevel 1 goto failed

echo.
echo ========================================
echo Environment setup finished.
echo Next:
echo   cmd /c call start-all.cmd --check
echo   cmd /c call start-all.cmd
echo ========================================
exit /b 0

:usage_ok
call :print_usage
exit /b 0

:usage_error
call :print_usage
exit /b 1

:print_usage
echo Usage:
echo   setup-env.cmd [options]
echo.
echo Description:
echo   Install or refresh local dependencies, create workspace folders,
echo   and initialize missing xiaomiaoAgent config in this project.
echo.
echo Options:
echo   --check        Only check tools, config files and dependency folders.
echo   --yes, -y      Copy config.example.json to config.json when missing.
echo   --skip-python  Skip Python dependency installation.
echo   --skip-node    Skip xiaomiaobot pnpm installation.
echo   --skip-webui   Skip xiaomiaoAgent WebUI npm installation.
echo   --help, -h     Show this help message.
echo.
echo Examples:
echo   setup-env.cmd
echo   setup-env.cmd --check
echo   setup-env.cmd --yes
exit /b 0

:check_layout
if not exist "%XIAOMIAO_DIR%\requirements.txt" (
    echo [Error] Missing: %XIAOMIAO_DIR%\requirements.txt
    exit /b 1
)
if not exist "%XIAOMIAO_AGENT_DIR%\pyproject.toml" (
    echo [Error] Missing: %XIAOMIAO_AGENT_DIR%\pyproject.toml
    exit /b 1
)
if not exist "%XIAOMIAOBOT_DIR%\package.json" (
    echo [Error] Missing: %XIAOMIAOBOT_DIR%\package.json
    exit /b 1
)
if not exist "%XIAOMIAO_AGENT_WEBUI_DIR%\package.json" (
    echo [Error] Missing: %XIAOMIAO_AGENT_WEBUI_DIR%\package.json
    exit /b 1
)
exit /b 0

:check_required_commands
echo [Check] Required commands
call :require_command conda
if "%SKIP_NODE%"=="0" (
    call :require_command node
    call :require_command corepack
    call :require_command npm
)
if "%FAILED%"=="1" exit /b 1
echo.
exit /b 0

:require_command
where "%~1" >nul 2>nul
if errorlevel 1 (
    echo   [Missing] %~1
    set "FAILED=1"
) else (
    echo   [OK] %~1
)
exit /b 0

:check_current_state
echo.
echo [Check] Conda environment: xiaomiao
call conda run --no-capture-output -n xiaomiao python --version
if errorlevel 1 set "FAILED=1"

echo.
echo [Check] Config files
call :check_file "%ROOT_CONFIG%" "root config.json"
call :check_file "%XIAOMIAO_CONFIG%" "xiaomiao config.json"
call :check_file "%XIAOMIAO_AGENT_CONFIG%" "xiaomiaoAgent .nanobot config.json"

echo.
echo [Check] Dependency folders
call :check_dir "%XIAOMIAOBOT_DIR%\node_modules" "xiaomiaobot node_modules"
if "%SKIP_WEBUI%"=="0" call :check_dir "%XIAOMIAO_AGENT_WEBUI_DIR%\node_modules" "xiaomiaoAgent WebUI node_modules"
call :check_dir "%XIAOMIAO_AGENT_WORKSPACE%" "xiaomiaoAgent workspace"
call :check_dir "%ROOT_DIR%workspace" "project workspace"

echo.
echo ========================================
if "%FAILED%"=="1" (
    echo Environment check failed. Run setup-env.cmd to install or initialize missing parts.
    echo ========================================
    exit /b 1
)
echo Environment check passed.
echo ========================================
exit /b 0

:check_file
if exist "%~1" (
    echo   [OK] %~2
) else (
    echo   [Missing] %~2: %~1
    set "FAILED=1"
)
exit /b 0

:check_dir
if exist "%~1" (
    echo   [OK] %~2
) else (
    echo   [Missing] %~2: %~1
    set "FAILED=1"
)
exit /b 0

:ensure_workspace_dirs
echo [Setup] Workspace directories
if not exist "%ROOT_DIR%workspace" mkdir "%ROOT_DIR%workspace"
if not exist "%ROOT_DIR%workspace\downloads" mkdir "%ROOT_DIR%workspace\downloads"
if not exist "%ROOT_DIR%workspace\downloads\qq" mkdir "%ROOT_DIR%workspace\downloads\qq"
if not exist "%ROOT_DIR%workspace\artifacts" mkdir "%ROOT_DIR%workspace\artifacts"
if not exist "%ROOT_DIR%workspace\tmp" mkdir "%ROOT_DIR%workspace\tmp"
if not exist "%XIAOMIAO_AGENT_WORKSPACE%" mkdir "%XIAOMIAO_AGENT_WORKSPACE%"
echo   [OK] Workspace folders are ready.
echo.
exit /b 0

:setup_python
echo [Setup] Python dependencies
call conda run --no-capture-output -n xiaomiao python --version
if errorlevel 1 (
    echo [Error] Conda environment 'xiaomiao' is not available.
    echo         Create it first or rename the environment in this script.
    exit /b 1
)

echo   Installing xiaomiao requirements...
call conda run --no-capture-output -n xiaomiao python -m pip install -r "%XIAOMIAO_DIR%\requirements.txt"
if errorlevel 1 exit /b 1

echo   Installing xiaomiaoAgent editable package with API extra...
call conda run --no-capture-output -n xiaomiao python -m pip install -e "%XIAOMIAO_AGENT_DIR%[api]"
if errorlevel 1 exit /b 1
echo.
exit /b 0

:setup_node
echo [Setup] Node / pnpm dependencies
call corepack enable
if errorlevel 1 exit /b 1
call corepack prepare pnpm@10.33.0 --activate
if errorlevel 1 exit /b 1

echo   Installing xiaomiaobot dependencies...
pushd "%XIAOMIAOBOT_DIR%"
call pnpm install
set "PNPM_EXIT=%ERRORLEVEL%"
popd
if not "%PNPM_EXIT%"=="0" exit /b %PNPM_EXIT%

if "%SKIP_WEBUI%"=="1" (
    echo   [Skip] xiaomiaoAgent WebUI npm install.
    echo.
    exit /b 0
)

echo   Installing xiaomiaoAgent WebUI dependencies...
pushd "%XIAOMIAO_AGENT_WEBUI_DIR%"
call npm install
set "NPM_EXIT=%ERRORLEVEL%"
popd
if not "%NPM_EXIT%"=="0" exit /b %NPM_EXIT%
echo.
exit /b 0

:ensure_configs
echo [Setup] Local config files
if exist "%ROOT_CONFIG%" (
    echo   [OK] root config.json exists.
) else (
    if exist "%ROOT_CONFIG_EXAMPLE%" (
        if "%YES%"=="1" (
            copy "%ROOT_CONFIG_EXAMPLE%" "%ROOT_CONFIG%" >nul
            echo   [Created] root config.json copied from config.example.json.
        ) else (
            echo   [Missing] root config.json
            echo   Run setup-env.cmd --yes to copy config.example.json automatically,
            echo   then edit API Key, baseUrl and model before startup.
        )
    ) else (
        echo   [Missing] root config.json and config.example.json.
    )
)

if exist "%XIAOMIAO_CONFIG%" (
    echo   [OK] xiaomiao config.json exists.
) else (
    echo   [Missing] %XIAOMIAO_CONFIG%
    echo   Please create it from your QQ / OneBot local configuration.
)

if exist "%XIAOMIAO_AGENT_CONFIG%" (
    echo   [OK] xiaomiaoAgent .nanobot config exists.
) else (
    echo   Creating xiaomiaoAgent .nanobot config...
    call conda run --no-capture-output -n xiaomiao xiaomiao onboard --config "%XIAOMIAO_AGENT_CONFIG%" --workspace "%XIAOMIAO_AGENT_WORKSPACE%"
    if errorlevel 1 exit /b 1
)
echo.
exit /b 0

:failed
echo.
echo ========================================
echo Environment setup failed. See the error above.
echo ========================================
exit /b 1
