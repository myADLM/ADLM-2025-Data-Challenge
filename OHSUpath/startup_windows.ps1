# =====================================================================
# Full Windows Setup (PowerShell, single-file, relative paths)
# - Ensure Python 3.11 (py launcher or python.exe; auto-install via winget)
# - Install requirements
# - Download Hugging Face models (progress) into .\models\...
# - Install Ollama + create deepseek-r1-8b-int8 (relative Modelfile)
# - Full logging to .\setup.log and safe exit on errors
# =====================================================================

$ErrorActionPreference = 'Stop'
$logPath = Join-Path $PSScriptRoot 'setup.log'
Start-Transcript -Path $logPath -Append | Out-Null

Write-Host "============================================================="
Write-Host " Full Windows Setup (PowerShell)"
Write-Host "============================================================="

# Keep window open and stop transcript on any unhandled error
trap {
  Write-Host "`n[x] Unexpected error:" $_.Exception.Message
  Write-Host "See full log at: $logPath"
  try { Stop-Transcript | Out-Null } catch {}
  Read-Host -Prompt "Press Enter to close..."
  exit 1
}

# -----------------------------
# Step 0. Elevate to Admin
# -----------------------------
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
   ).IsInRole([Security.Principal.WindowsBuiltinRole] "Administrator")) {
  Write-Host "[i] Relaunching with Administrator privileges..."
  Start-Process powershell.exe "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
  try { Stop-Transcript | Out-Null } catch {}
  exit
}
Write-Host "[OK] Running as Administrator.`n"

# Work from repo root (relative paths everywhere)
Push-Location -LiteralPath $PSScriptRoot

# -----------------------------
# Helpers
# -----------------------------
function Resolve-Python {
  # Try: py -3.11
  if (Get-Command py -ErrorAction SilentlyContinue) {
    try {
      $v = & py -3.11 -c "import sys; print(sys.version.split()[0])" 2>$null
      if ($LASTEXITCODE -eq 0 -and $v -match '^3\.11\.') {
        $script:PythonCmd = 'py'
        $script:PythonArgs = @('-3.11')
        return
      }
    } catch {}
  }
  # Try: python (must be 3.11)
  if (Get-Command python -ErrorAction SilentlyContinue) {
    try {
      $v = & python -c "import sys; print(sys.version.split()[0])"
      if ($LASTEXITCODE -eq 0 -and $v -match '^3\.11\.') {
        $script:PythonCmd = 'python'
        $script:PythonArgs = @()
        return
      }
    } catch {}
  }
  # Install Python 3.11 via winget (no absolute paths written)
  Write-Host "[i] Installing Python 3.11 via winget..."
  winget install --id Python.Python.3.11 --exact --silent --accept-package-agreements --accept-source-agreements | Out-Null
  Start-Sleep -Seconds 3
  # Try again
  if (Get-Command py -ErrorAction SilentlyContinue) {
    $v = & py -3.11 -c "import sys; print(sys.version.split()[0])" 2>$null
    if ($LASTEXITCODE -eq 0 -and $v -match '^3\.11\.') {
      $script:PythonCmd = 'py'
      $script:PythonArgs = @('-3.11')
      return
    }
  }
  if (Get-Command python -ErrorAction SilentlyContinue) {
    $v = & python -c "import sys; print(sys.version.split()[0])"
    if ($LASTEXITCODE -eq 0 -and $v -match '^3\.11\.') {
      $script:PythonCmd = 'python'
      $script:PythonArgs = @()
      return
    }
  }
  throw "Python 3.11 not found after installation. Please sign out/in or reboot and run again."
}

function Invoke-Python {
  param([Parameter(Mandatory=$true)][string[]]$Args)
  & $script:PythonCmd @($script:PythonArgs + $Args)
}

# -----------------------------
# Step 1. Ensure Python 3.11
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 1/6: Check Python Availability"
Write-Host "============================================================="
Resolve-Python
Write-Host "[OK] Using Python: $script:PythonCmd $($script:PythonArgs -join ' ')"
Invoke-Python @('--version')
Write-Host ""

# -----------------------------
# Step 2. Install requirements
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 2/6: Install Python requirements"
Write-Host "============================================================="
try {
  Write-Host "[i] Upgrading pip/setuptools/wheel..."
  Invoke-Python @('-m','pip','install','--upgrade','pip','setuptools','wheel')
  Write-Host "[i] Installing requirements.txt..."
  Invoke-Python @('-m','pip','install','-r','.\requirements.txt')
  Write-Host "[OK] Requirements installed or already satisfied.`n"
} catch {
  throw "Failed to install Python dependencies: $($_.Exception.Message)"
}

# -----------------------------
# Step 3. Download Hugging Face models
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 3/6: Download Hugging Face models"
Write-Host "============================================================="

$env:HF_HUB_DISABLE_PROGRESS_BARS="0"
$env:HF_HUB_ENABLE_HF_TRANSFER="1"
$env:HF_HUB_OFFLINE="0"
$env:TQDM_DISABLE="0"

try {
  Write-Host "[i] Ensuring hf_transfer..."
  Invoke-Python @('-m','pip','install','hf_transfer','-q')
} catch {
  Write-Host "[!] Could not install hf_transfer. Continuing with standard downloader."
}

# Relative folders under repo
$modelsRoot = ".\models"
$r1Dir      = ".\models\DeepseekR1"
$miniDir    = ".\models\all-MiniLM-L6-v2"
$instDir    = ".\models\InstructorXL"
$r1File     = 'DeepSeek-R1-Distill-Llama-8B-Q8_0.gguf'

New-Item -ItemType Directory -Force -Path $modelsRoot,$r1Dir,$miniDir,$instDir | Out-Null

# Helper Python (relative temp inside repo)
$tmpDir = ".\.tmp"
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
$pyTemp = Join-Path $tmpDir "hf_download_$PID.py"

# NOTE: has_real_files() ignores .gitkeep / hidden files and checks size > 0
$pyCode = @'
import os, sys
from pathlib import Path
print = lambda *a,**k: __import__("builtins").print(*a, **dict(k, flush=True))

try:
    from huggingface_hub import snapshot_download, hf_hub_download
except Exception as e:
    print("[x] huggingface_hub import failed:", e)
    sys.exit(1)

R1_DIR         = os.environ["R1_DIR"]
MINILM_DIR     = os.environ["MINILM_DIR"]
INSTRUCTOR_DIR = os.environ["INSTRUCTOR_DIR"]
R1_FILE        = os.environ["R1_FILE"]

for d in (R1_DIR, MINILM_DIR, INSTRUCTOR_DIR):
    Path(d).mkdir(parents=True, exist_ok=True)

def has_real_files(p: str) -> bool:
    try:
        for entry in os.scandir(p):
            name = entry.name.lower()
            if name == ".gitkeep" or name.startswith('.'):
                continue
            if entry.is_file() and os.path.getsize(entry.path) > 0:
                return True
        return False
    except FileNotFoundError:
        return False

ok = True

# DeepSeek R1 GGUF (single file)
r1_path = os.path.join(R1_DIR, R1_FILE)
if os.path.exists(r1_path) and os.path.getsize(r1_path) > 0:
    print("[OK] DeepSeek R1 GGUF already present:", r1_path)
else:
    try:
        print("[i] Downloading DeepSeek R1 GGUF ->", r1_path)
        hf_hub_download(
            repo_id="unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF",
            filename=R1_FILE,
            local_dir=R1_DIR,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print("[OK] DeepSeek R1 GGUF ready.")
    except Exception as e:
        ok = False
        print("[!] DeepSeek R1 GGUF download failed:", e)

# all-MiniLM-L6-v2
if has_real_files(MINILM_DIR):
    print("[OK] all-MiniLM-L6-v2 already present:", MINILM_DIR)
else:
    try:
        print("[i] Downloading all-MiniLM-L6-v2 ->", MINILM_DIR)
        snapshot_download(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            local_dir=MINILM_DIR,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print("[OK] all-MiniLM-L6-v2 ready.")
    except Exception as e:
        ok = False
        print("[!] all-MiniLM-L6-v2 download failed:", e)

# instructor-xl
if has_real_files(INSTRUCTOR_DIR):
    print("[OK] instructor-xl already present:", INSTRUCTOR_DIR)
else:
    try:
        print("[i] Downloading instructor-xl ->", INSTRUCTOR_DIR)
        snapshot_download(
            repo_id="hkunlp/instructor-xl",
            local_dir=INSTRUCTOR_DIR,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print("[OK] instructor-xl ready.")
    except Exception as e:
        ok = False
        print("[!] instructor-xl download failed:", e)

sys.exit(0 if ok else 1)
'@

Set-Content -Path $pyTemp -Value $pyCode -Encoding UTF8

# Export RELATIVE paths to the helper
$env:R1_DIR         = $r1Dir
$env:MINILM_DIR     = $miniDir
$env:INSTRUCTOR_DIR = $instDir
$env:R1_FILE        = $r1File

try {
  Invoke-Python @($pyTemp)
} finally {
  Remove-Item -Force -ErrorAction SilentlyContinue $pyTemp
  if ((Get-ChildItem $tmpDir -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0) {
    Remove-Item -Force -ErrorAction SilentlyContinue $tmpDir
  }
}
Write-Host ""

# -----------------------------
# Step 4. Ensure Ollama + local model
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 4/6: Ensure Ollama + local model"
Write-Host "============================================================="

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  Write-Host "[i] Installing Ollama via winget..."
  winget install --id Ollama.Ollama --exact --silent --accept-package-agreements --accept-source-agreements | Out-Null
}

if (Get-Command ollama -ErrorAction SilentlyContinue) {
  $modelfile = Join-Path $r1Dir 'Modelfile'   # relative to repo root
  if (-not (Test-Path $modelfile)) {
    Set-Content -Path $modelfile -Value "FROM $r1File" -Encoding UTF8
    Write-Host "[OK] Modelfile created: $modelfile"
  } else {
    Write-Host "[OK] Modelfile exists: $modelfile"
  }

  $exists = (ollama list | Select-String -Pattern '^deepseek-r1-8b-int8' -Quiet)
  if (-not $exists) {
    Write-Host "[i] Creating Ollama model: deepseek-r1-8b-int8"
    Push-Location $r1Dir
    try {
      & ollama create deepseek-r1-8b-int8 -f Modelfile
      Write-Host "[OK] Ollama model created: deepseek-r1-8b-int8"
    } catch {
      Write-Host "[!] ollama create failed. You can run it manually in:"
      Write-Host "    $r1Dir"
      Write-Host "    ollama create deepseek-r1-8b-int8 -f Modelfile"
    } finally { Pop-Location }
  } else {
    Write-Host "[OK] Ollama model already exists."
  }
} else {
  Write-Host "[x] Ollama is not available. Please install it manually and re-run this step."
}
Write-Host ""

# -----------------------------
# Step 5. Final info
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 5/6: Done"
Write-Host "============================================================="
Write-Host "[OK] Setup finished."
Write-Host "============================================================="


# -----------------------------
# Step 6. Display information
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 6/6: Next step"
Write-Host "============================================================="
Write-Host ""
Write-Host ""
Write-Host "Please double click the following file in the SAME folder to run the app:"
Write-Host ""
Write-Host "  Windows_Click_Me_To_Run_The_App.bat"
Write-Host ""
Write-Host ""
Write-Host "Tip: Run it as a NORMAL user (non-admin) if possible."
Write-Host ""
Write-Host ""
Write-Host "The setup is now complete, feel free to close this window."
Write-Host ""
Write-Host ""
Write-Host "============================================================="
Pop-Location
try { Stop-Transcript | Out-Null } catch {}
Read-Host -Prompt "Press Enter to close..."
