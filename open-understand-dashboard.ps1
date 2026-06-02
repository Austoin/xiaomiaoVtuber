param(
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$GraphFile = Join-Path $ProjectRoot ".understand-anything\knowledge-graph.json"
$LogDir = Join-Path $ProjectRoot ".understand-anything"
$OutLog = Join-Path $LogDir "dashboard.log"
$ErrLog = Join-Path $LogDir "dashboard.err.log"
$PidFile = Join-Path $LogDir "dashboard.pid"
$DashboardDir = "C:\Users\liu'zhi'gui\.understand-anything\repo\understand-anything-plugin\packages\dashboard"

function Write-Status {
    param([string]$Message)
    Write-Host "[understand-dashboard] $Message"
}

function Assert-PathExists {
    param(
        [string]$Path,
        [string]$Description
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Description 不存在：$Path"
    }
}

function Resolve-Pnpm {
    $command = Get-Command pnpm.cmd -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    throw "未找到 pnpm.cmd，请先安装/启用 pnpm。"
}

function Reset-LogFile {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Force
    }
}

function Start-DashboardProcess {
    param([string]$PnpmPath)
    $env:GRAPH_DIR = $ProjectRoot
    return Start-Process `
        -FilePath $PnpmPath `
        -ArgumentList @("exec", "vite", "--host", "127.0.0.1") `
        -WorkingDirectory $DashboardDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $OutLog `
        -RedirectStandardError $ErrLog `
        -PassThru
}

function Wait-DashboardUrl {
    param([System.Diagnostics.Process]$Process)
    for ($i = 0; $i -lt 80; $i++) {
        if ($Process.HasExited) {
            $errorText = Read-TextIfExists $ErrLog
            throw "dashboard 进程已退出。错误日志：$errorText"
        }

        $output = Read-TextIfExists $OutLog
        if ($output -match "Dashboard URL:\s*(http://\S+)") {
            return $Matches[1]
        }

        Start-Sleep -Milliseconds 500
    }

    throw "等待 dashboard URL 超时，请查看日志：$OutLog"
}

function Read-TextIfExists {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        return Get-Content -LiteralPath $Path -Raw
    }
    return ""
}

Assert-PathExists -Path $GraphFile -Description "知识图谱文件"
Assert-PathExists -Path $DashboardDir -Description "Understand Dashboard 目录"
Assert-PathExists -Path $LogDir -Description "Understand Anything 输出目录"

$pnpm = Resolve-Pnpm
Reset-LogFile -Path $OutLog
Reset-LogFile -Path $ErrLog

Write-Status "启动 dashboard..."
$process = Start-DashboardProcess -PnpmPath $pnpm
Set-Content -LiteralPath $PidFile -Value $process.Id
Write-Status "进程 PID: $($process.Id)"
$url = Wait-DashboardUrl -Process $process

Write-Status "Dashboard URL: $url"
if (-not $NoOpen) {
    Start-Process $url
}
