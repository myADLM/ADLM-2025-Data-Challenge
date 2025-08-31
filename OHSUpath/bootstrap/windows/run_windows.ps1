

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

# Show elevation status
$wid = [Security.Principal.WindowsIdentity]::GetCurrent()
$wpr = New-Object Security.Principal.WindowsPrincipal($wid)
if ($wpr.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    Write-Host "[!] You are running as ADMINISTRATOR." -ForegroundColor Red
} else {
    Write-Host "[OK] You are running as a normal user." -ForegroundColor Green
}


function Start-OllamaService {
    # Try fast path: is API already up?
    try {
        Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 | Out-Null
        Write-Host "[i] Ollama API is already responsive."
        return
    } catch {}

    $apiOk = $false

    # Case 1: service installed
    $svc = Get-Service -Name 'Ollama' -ErrorAction SilentlyContinue
    if ($null -ne $svc) {
        if ($svc.Status -ne 'Running') {
            Write-Host "[i] Starting Ollama service..."
            Start-Service -Name 'Ollama' | Out-Null
        } else {
            Write-Host "[i] Ollama service already running, probing API..."
        }
        for ($i=0; $i -lt 20; $i++) {
            try { Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 2 | Out-Null; $apiOk=$true; break } catch { Start-Sleep -Milliseconds 500 }
        }
        if ($apiOk) { return }
        Write-Host "[!] Ollama service did not respond to API after restart attempt."
    }

    # Case 2: no service, fallback to direct process
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        throw "Ollama CLI not found. Please run Windows_Click_Me_To_Setup_The_Computer.bat first."
    }
    Write-Host "[i] Launching Ollama daemon directly..."

    # Start hidden process (no cmd window)
    Start-Process -FilePath "ollama" -ArgumentList "serve" `
         -WindowStyle Hidden -PassThru

    # Probe API
    for ($i=0; $i -lt 20; $i++) {
        try { Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 2 | Out-Null; $apiOk=$true; break } catch { Start-Sleep -Milliseconds 500 }
    }
    if ($apiOk) {
        Write-Host "[i] Ollama daemon is responsive."
        return
    }

    throw "Failed to start Ollama (API not responding)."
}


function Confirm-OllamaModel {
    param([string]$Tag = 'deepseek-r1-8b-int8')

    # Helper: check presence via API or CLI
    function Test-ModelPresent([string]$t) {
        try {
            $names = (Invoke-RestMethod -Method GET -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2).models.name
            if ($names -contains $t) { return $true }
        } catch {}
        try {
            $hit = (ollama list | Select-String -Pattern ("^" + [regex]::Escape($t) + "\b") -Quiet)
            if ($hit) { return $true }
        } catch {}
        return $false
    }

    if (Test-ModelPresent $Tag) { return }

    $mfPath = Join-Path $RepoRoot "models\DeepseekR1\Modelfile"
    if (-not (Test-Path $mfPath)) {
        throw "Model '$Tag' missing and no local Modelfile at $mfPath. Please run Windows_Click_Me_To_Setup_The_Computer.bat first."
    }

    Write-Host "[i] Creating model '$Tag' from local Modelfile..."

    $cmdLine = "ollama create $Tag -f `"$mfPath`" >NUL 2>&1"
    $p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $cmdLine `
         -WorkingDirectory $RepoRoot -NoNewWindow -PassThru

    # Allow time even if daemon had to spin up internally
    if (-not (Wait-Process -Id $p.Id -Timeout 600)) {
        try { Stop-Process -Id $p.Id -Force } catch {}
        throw "Timeout creating model '$Tag'."
    }
    if ($p.ExitCode -ne 0) {
        throw "ollama create exited with code $($p.ExitCode)."
    }

    # Final confirmation (API or CLI), up to ~15s
    for ($i=0; $i -lt 30; $i++) {
        if (Test-ModelPresent $Tag) { return }
        Start-Sleep -Milliseconds 500
    }
    throw "Model '$Tag' not visible after creation."
}

# work from repo root
Push-Location -LiteralPath $RepoRoot
try {
    try { $Host.UI.RawUI.WindowTitle = "OHSUpath - Streamlit" } catch {}

    $appPath = Join-Path $RepoRoot 'app.py'
    if (-not (Test-Path $appPath)) {
        throw "app.py not found in: $RepoRoot"
    }

    # Detect Python 3.11 (prefer 'py -3.11', fallback to 'python')
    $PyCmd  = $null
    $PyArgs = @()

    if (Get-Command py -ErrorAction SilentlyContinue) {
        try {
            $v = & py -3.11 -c "import sys; print(sys.version.split()[0])" 2>$null
            if ($LASTEXITCODE -eq 0 -and $v -match '^3\.11\.') {
                $PyCmd  = 'py'
                $PyArgs = @('-3.11')
            }
        } catch {}
    }
    if (-not $PyCmd) {
        if (Get-Command python -ErrorAction SilentlyContinue) {
            try {
                $v = & python -c "import sys; print(sys.version.split()[0])"
                if ($LASTEXITCODE -eq 0 -and $v -match '^3\.11\.') {
                    $PyCmd  = 'python'
                    $PyArgs = @()
                }
            } catch {}
        }
    }
    if (-not $PyCmd) {
        throw "Python 3.11 not found. Please run Windows_Click_Me_To_Setup_The_Computer.bat first, or install Python 3.11."
    }

    # Ensure Ollama service and model are ready
    Start-OllamaService
    Confirm-OllamaModel

    Write-Host "Launching Streamlit app..."
    & $PyCmd @($PyArgs + @('-m','streamlit','run', $appPath))
}
catch {
    Write-Host ""
    Write-Host "[x] Failed to launch:" -ForegroundColor Red
    Write-Host "    $($_.Exception.Message)"
    Write-Host ""
    Read-Host "Press Enter to close..."
}
finally {
    Pop-Location
}
