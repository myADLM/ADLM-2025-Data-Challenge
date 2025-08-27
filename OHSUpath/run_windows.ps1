

$ErrorActionPreference = 'Stop'

# Show elevation status
$wid = [Security.Principal.WindowsIdentity]::GetCurrent()
$wpr = New-Object Security.Principal.WindowsPrincipal($wid)
if ($wpr.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    Write-Host "[!] You are running as ADMINISTRATOR." -ForegroundColor Red
} else {
    Write-Host "[OK] You are running as a normal user." -ForegroundColor Green
}

# Always work from the script directory
Push-Location -LiteralPath $PSScriptRoot
try {
    try { $Host.UI.RawUI.WindowTitle = "OHSUpath - Streamlit" } catch {}

    if (-not (Test-Path .\app.py)) {
        throw "app.py not found in: $PSScriptRoot"
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
        throw "Python 3.11 not found. Please run setup.ps1 first, or install Python 3.11."
    }

    Write-Host "Launching Streamlit app..."
    & $PyCmd @($PyArgs + @('-m','streamlit','run','.\app.py'))
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
