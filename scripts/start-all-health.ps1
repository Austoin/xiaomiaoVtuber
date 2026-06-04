param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("check", "assert-free", "wait", "is-open")]
    [string] $Command,

    [ValidateSet("Port", "Http", "Gateway", "Xiaomiao")]
    [string] $Kind = "Port",

    [string] $Name = "service",
    [int] $Port = 0,
    [string] $Url = "",
    [string] $BaseUrl = "",
    [string] $Needle = "",
    [int] $TimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"
$script:LastHealthDetail = ""

function Test-TcpPort {
    param([int] $PortNumber)
    if ($PortNumber -le 0) { return $false }
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $task = $client.ConnectAsync("127.0.0.1", $PortNumber)
        return $task.Wait(1000) -and $client.Connected
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

function Get-PortOwners {
    param([int] $PortNumber)
    $owners = New-Object System.Collections.Generic.List[string]
    foreach ($line in (netstat -ano -p tcp)) {
        if ($line -match "^\s*TCP\s+\S+:$PortNumber\s+\S+\s+LISTENING\s+(\d+)\s*$") {
            $owners.Add($Matches[1])
        }
    }
    return $owners | Sort-Object -Unique
}

function Write-PortOwners {
    param([int] $PortNumber)
    $owners = @(Get-PortOwners -PortNumber $PortNumber)
    if ($owners.Count -eq 0) {
        Write-Host "      Owner PID: unknown"
        return
    }
    Write-Host "      Owner PID(s): $($owners -join ', ')"
    foreach ($owner in $owners) {
        $proc = Get-Process -Id ([int] $owner) -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "        $owner $($proc.ProcessName) $($proc.Path)"
        }
    }
}

function Test-ProcessConnectedToPort {
    param([string[]] $ProcessIds, [int] $RemotePort)
    if ($ProcessIds.Count -eq 0) { return $false }
    foreach ($line in (netstat -ano -p tcp)) {
        $pattern = "^\s*TCP\s+(\S+)\s+(\S+)\s+ESTABLISHED\s+(\d+)\s*$"
        if ($line -notmatch $pattern) { continue }
        if ($ProcessIds -notcontains $Matches[3]) { continue }
        if ($Matches[1] -like "*:$RemotePort" -or $Matches[2] -like "*:$RemotePort") {
            return $true
        }
    }
    return $false
}

function Test-HttpReady {
    param([string] $TargetUrl, [string] $ExpectedText)
    if ([string]::IsNullOrWhiteSpace($TargetUrl)) { return $false }
    try {
        $res = Invoke-WebRequest -UseBasicParsing -Uri $TargetUrl -TimeoutSec 5
        if ([int] $res.StatusCode -lt 200 -or [int] $res.StatusCode -ge 300) {
            return $false
        }
        if ([string]::IsNullOrEmpty($ExpectedText)) { return $true }
        return [string] $res.Content -like "*$ExpectedText*"
    }
    catch {
        return $false
    }
}

function Test-WebSocketReady {
    param([string] $WsUrl)
    $client = [System.Net.WebSockets.ClientWebSocket]::new()
    $cts = [System.Threading.CancellationTokenSource]::new()
    $cts.CancelAfter(5000)
    try {
        $client.ConnectAsync([Uri] $WsUrl, $cts.Token).GetAwaiter().GetResult()
        $buffer = [byte[]]::new(8192)
        $segment = [System.ArraySegment[byte]]::new($buffer)
        $result = $client.ReceiveAsync($segment, $cts.Token).GetAwaiter().GetResult()
        $text = [System.Text.Encoding]::UTF8.GetString($buffer, 0, $result.Count)
        return $text -like '*"event": "ready"*' -or $text -like '*"event":"ready"*'
    }
    catch {
        return $false
    }
    finally {
        if ($client.State -eq [System.Net.WebSockets.WebSocketState]::Open) {
            $closeCts = [System.Threading.CancellationTokenSource]::new()
            $closeCts.CancelAfter(1000)
            try {
                $client.CloseAsync(
                    [System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure,
                    "health-check",
                    $closeCts.Token
                ).GetAwaiter().GetResult()
            }
            catch {
            }
            $closeCts.Dispose()
        }
        $cts.Dispose()
        $client.Dispose()
    }
}

function Test-GatewayReady {
    param([string] $TargetBaseUrl)
    if ([string]::IsNullOrWhiteSpace($TargetBaseUrl)) { return $false }
    try {
        $base = [Uri] $TargetBaseUrl
        $bootstrapUrl = "$($base.Scheme)://$($base.Authority)/webui/bootstrap"
        $boot = Invoke-RestMethod -Uri $bootstrapUrl -TimeoutSec 5
        if (-not $boot.token -or -not $boot.ws_path) { return $false }
        $headers = @{ Authorization = "Bearer $($boot.token)" }
        $sessionsUrl = "$($base.Scheme)://$($base.Authority)/api/sessions"
        $sessions = Invoke-WebRequest -UseBasicParsing -Uri $sessionsUrl -Headers $headers -TimeoutSec 5
        if ([int] $sessions.StatusCode -lt 200 -or [int] $sessions.StatusCode -ge 300) {
            return $false
        }
        $sessionPayload = $sessions.Content | ConvertFrom-Json
        if (-not (Test-GatewayUnifiedSessionReadable $base $headers $sessionPayload)) {
            return $false
        }
        $scheme = if ($base.Scheme -eq "https") { "wss" } else { "ws" }
        $path = [string] $boot.ws_path
        if (-not $path.StartsWith("/")) { $path = "/$path" }
        $token = [System.Uri]::EscapeDataString([string] $boot.token)
        return Test-WebSocketReady "${scheme}://$($base.Authority)$path`?token=$token"
    }
    catch {
        return $false
    }
}

function Test-GatewayUnifiedSessionReadable {
    param(
        [Uri] $Base,
        [hashtable] $Headers,
        $SessionPayload
    )
    $targetKey = "api:xiaomiao-unified"
    $sessions = @($SessionPayload.sessions)
    $hasUnified = $false
    foreach ($session in $sessions) {
        if ([string] $session.key -eq $targetKey) {
            $hasUnified = $true
            break
        }
    }
    if (-not $hasUnified) { return $true }
    $encodedKey = [System.Uri]::EscapeDataString($targetKey)
    $messagesUrl = "$($Base.Scheme)://$($Base.Authority)/api/sessions/$encodedKey/messages"
    $messages = Invoke-WebRequest -UseBasicParsing -Uri $messagesUrl -Headers $Headers -TimeoutSec 5
    if ([int] $messages.StatusCode -ge 200 -and [int] $messages.StatusCode -lt 300) {
        return $true
    }
    $script:LastHealthDetail = "xiaomiao-unified session exists but messages API is not readable"
    return $false
}

function Test-XiaomiaoReady {
    if (-not (Test-HttpReady $Url $Needle)) {
        $script:LastHealthDetail = "bridge status endpoint is not ready"
        return $false
    }
    $owners = @(Get-PortOwners -PortNumber $Port)
    if (-not (Test-ProcessConnectedToPort $owners 5004)) {
        $script:LastHealthDetail = "bridge PID is not connected to QQ OneBot port 5004"
        return $false
    }
    $script:LastHealthDetail = ""
    return $true
}

function Test-Health {
    switch ($Kind) {
        "Port" { return Test-TcpPort $Port }
        "Http" { return Test-HttpReady $Url $Needle }
        "Gateway" { return Test-GatewayReady $BaseUrl }
        "Xiaomiao" { return Test-XiaomiaoReady }
    }
}

function Invoke-Check {
    $listening = if ($Port -gt 0) { Test-TcpPort $Port } else { $false }
    if ($listening) {
        Write-Host "      $Name port $Port is listening."
        Write-PortOwners $Port
    }
    elseif ($Port -gt 0) {
        Write-Host "      $Name port $Port is free. Would start a visible terminal."
        return $true
    }
    $ready = Test-Health
    if ($ready) {
        Write-Host "      Health check passed: $Name"
        return $true
    }
    Write-Host "      Health check failed: $Name"
    if ($script:LastHealthDetail) {
        Write-Host "      Detail: $script:LastHealthDetail"
    }
    return $false
}

function Invoke-AssertFree {
    if (-not (Test-TcpPort $Port)) { return $true }
    Write-Host "[Error] $Name already owns 127.0.0.1:$Port."
    Write-PortOwners $Port
    Write-Host "        start-all.cmd cannot attach an old process to a new visible terminal."
    Write-Host "        Close that service first, then run start-all.cmd again."
    return $false
}

function Invoke-Wait {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    Write-Host "      Waiting for $Name ..."
    while ((Get-Date) -lt $deadline) {
        if (Test-Health) {
            Write-Host "      Ready: $Name"
            return $true
        }
        Start-Sleep -Seconds 1
    }
    Write-Host "[Error] $Name did not become ready within ${TimeoutSeconds}s."
    if ($script:LastHealthDetail) {
        Write-Host "        Detail: $script:LastHealthDetail"
    }
    return $false
}

switch ($Command) {
    "check" { if (Invoke-Check) { exit 0 } else { exit 1 } }
    "assert-free" { if (Invoke-AssertFree) { exit 0 } else { exit 1 } }
    "wait" { if (Invoke-Wait) { exit 0 } else { exit 1 } }
    "is-open" { if (Test-TcpPort $Port) { exit 0 } else { exit 1 } }
}
