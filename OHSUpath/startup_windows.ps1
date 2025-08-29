# =====================================================================
# Full Windows Setup (PowerShell, single-file, relative paths) - STRICT
# - Ensure Python 3.11 (py/python; auto-install via winget)
# - Install requirements + pip check
# - Download Hugging Face models (strict verification) into .\models\...
# - Install Ollama + create deepseek-r1-8b-int8 (strict verification)
# - Full logging to .\setup.log; FAIL-FAST (do not reach Step 6 on error)
# =====================================================================

$ErrorActionPreference = 'Stop'
$logPath = Join-Path $PSScriptRoot 'setup.log'
Start-Transcript -Path $logPath -Append | Out-Null

Write-Host "============================================================="
Write-Host " Full Windows Setup (PowerShell)"
Write-Host "============================================================="


# -----------------------------
# Pre-check: Ensure Internet Connectivity
# -----------------------------
$connected = $false
try {
  $client = New-Object System.Net.Sockets.TcpClient
  $iar = $client.BeginConnect('huggingface.co', 443, $null, $null)
  if ($iar.AsyncWaitHandle.WaitOne(1500, $false)) {
    $client.EndConnect($iar)
    $connected = $true
  }
  $client.Close()
} catch { }
if (-not $connected) {
  throw "No internet connectivity (HTTPS 443) to huggingface.co. Please connect to the internet and re-run."
}


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
# Global constants
# -----------------------------
$modelsRoot = ".\models"
$r1Dir      = ".\models\DeepseekR1"
$miniDir    = ".\models\all-MiniLM-L6-v2"
$instDir    = ".\models\InstructorXL"
$r1File     = 'DeepSeek-R1-Distill-Llama-8B-Q8_0.gguf'

# -----------------------------
# Helpers
# -----------------------------
function Resolve-Python {
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
  Write-Host "[i] Installing Python 3.11 via winget..."
  winget install --id Python.Python.3.11 --exact --silent --accept-package-agreements --accept-source-agreements | Out-Null
  Start-Sleep -Seconds 3
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
  param([Parameter(Mandatory=$true)][string[]]$PyArgs)
  & $script:PythonCmd @($script:PythonArgs + $PyArgs)
}

# -----------------------------
# Step 1/6: Ensure Python 3.11
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 1/6: Check Python Availability"
Write-Host "============================================================="
Resolve-Python
Write-Host "[OK] Using Python: $script:PythonCmd $($script:PythonArgs -join ' ')"
Invoke-Python @('--version')
Write-Host ""

# -----------------------------
# Step 2/6: Install requirements (STRICT)
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 2/6: Install Python requirements"
Write-Host "============================================================="
try {
  Write-Host "[i] Upgrading pip/setuptools/wheel..."
  Invoke-Python @('-m','pip','install','--upgrade','pip','setuptools','wheel')

  if (Test-Path .\requirements.txt) {
    Write-Host "[i] Installing requirements.txt..."
    Invoke-Python @('-m','pip','install','-r','.\requirements.txt')
  } else {
    Write-Host "[i] No requirements.txt found, skipping file-based installs."
  }

  # Ensure required libraries are always installed
  Invoke-Python @('-m','pip','install','--upgrade','huggingface_hub','sentence-transformers')

  Write-Host "[i] Verifying environment with 'pip check'..."
  Invoke-Python @('-m','pip','check')
  Write-Host "[OK] Python dependencies installed and verified.`n"
} catch {
  throw "Failed to install/verify Python dependencies: $($_.Exception.Message)"
}

# -----------------------------
# Step 3/6: Download Hugging Face models (STRICT)
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
  Invoke-Python @('-m','pip','install','-q','hf_transfer')
} catch {
  Write-Host "[!] Could not install hf_transfer. Falling back to standard downloader."
}

New-Item -ItemType Directory -Force -Path $modelsRoot,$r1Dir,$miniDir,$instDir | Out-Null

$tmpDir = ".\.tmp"
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
$pyTemp = Join-Path $tmpDir "hf_download_$PID.py"

# Python helper for strict model downloads
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

def has_required_files_model_dir(dirpath: str) -> bool:
    # Require at least one tokenizer/vocab file and one weight file
    tok = any(Path(dirpath, fn).exists() for fn in ("tokenizer.json","vocab.txt","spiece.model","tokenizer.model"))
    wts = any(Path(dirpath, fn).exists() for fn in ("model.safetensors","pytorch_model.bin","flax_model.msgpack"))
    return tok and wts

ok = True

# 1) DeepSeek R1 GGUF (expect >= 7GB to avoid partials)
r1_path = os.path.join(R1_DIR, R1_FILE)
if os.path.exists(r1_path) and os.path.getsize(r1_path) >= 7*1024*1024*1024:
    print("[OK] DeepSeek R1 GGUF present:", r1_path, os.path.getsize(r1_path), "bytes")
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
        size = os.path.getsize(r1_path) if os.path.exists(r1_path) else 0
        if size < 7*1024*1024*1024:
            raise RuntimeError(f"GGUF too small or missing: {size} bytes")
        print("[OK] DeepSeek R1 GGUF ready:", size, "bytes")
    except Exception as e:
        ok = False
        print("[!] DeepSeek R1 GGUF download/verify failed:", e)

# 2) all-MiniLM-L6-v2
if has_required_files_model_dir(MINILM_DIR):
    print("[OK] all-MiniLM-L6-v2 verified:", MINILM_DIR)
else:
    try:
        print("[i] Downloading all-MiniLM-L6-v2 ->", MINILM_DIR)
        snapshot_download(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            local_dir=MINILM_DIR,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        if not has_required_files_model_dir(MINILM_DIR):
            raise RuntimeError("all-MiniLM-L6-v2 missing required files after download")
        print("[OK] all-MiniLM-L6-v2 verified.")
    except Exception as e:
        ok = False
        print("[!] all-MiniLM-L6-v2 download/verify failed:", e)

# 3) instructor-xl
if has_required_files_model_dir(INSTRUCTOR_DIR):
    print("[OK] instructor-xl verified:", INSTRUCTOR_DIR)
else:
    try:
        print("[i] Downloading instructor-xl ->", INSTRUCTOR_DIR)
        snapshot_download(
            repo_id="hkunlp/instructor-xl",
            local_dir=INSTRUCTOR_DIR,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        if not has_required_files_model_dir(INSTRUCTOR_DIR):
            raise RuntimeError("instructor-xl missing required files after download")
        print("[OK] instructor-xl verified.")
    except Exception as e:
        ok = False
        print("[!] instructor-xl download/verify failed:", e)

sys.exit(0 if ok else 1)
'@

Set-Content -Path $pyTemp -Value $pyCode -Encoding UTF8

$env:R1_DIR         = $r1Dir
$env:MINILM_DIR     = $miniDir
$env:INSTRUCTOR_DIR = $instDir
$env:R1_FILE        = $r1File

try {
  Invoke-Python @($pyTemp)
} finally {
  Remove-Item -Force -ErrorAction SilentlyContinue $pyTemp
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $tmpDir
}
Write-Host ""

# -----------------------------
# Step 4/6: Ensure Ollama + local model (STRICT)
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 4/6: Ensure Ollama + local model"
Write-Host "============================================================="

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  Write-Host "[i] Installing Ollama via winget..."
  winget install --id Ollama.Ollama --exact --silent --accept-package-agreements --accept-source-agreements | Out-Null
  Start-Sleep -Seconds 2
}
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  throw "Ollama CLI not found after installation."
}

# Create/verify Modelfile with explicit relative path
$modelfile = Join-Path $r1Dir 'Modelfile'
if (-not (Test-Path (Join-Path $r1Dir $r1File))) {
  throw "GGUF missing: $(Join-Path $r1Dir $r1File)"
}
if (-not (Test-Path $modelfile)) {
  Set-Content -Path $modelfile -Value "FROM ./$r1File" -Encoding UTF8
  Write-Host "[OK] Modelfile created: $modelfile"
} else {
  $content = Get-Content $modelfile -Raw
  if ($content.Trim() -notmatch "FROM\s+\./$([Regex]::Escape($r1File))") {
    Set-Content -Path $modelfile -Value "FROM ./$r1File" -Encoding UTF8
    Write-Host "[i] Modelfile updated to reference ./$r1File"
  } else {
    Write-Host "[OK] Modelfile exists and references ./$r1File"
  }
}

# Create model if missing
$existingNames = (& ollama list) -split "`r?`n" |
  ForEach-Object { ($_ -split '\s+')[0].Split(':')[0] } |
  Where-Object { $_ }
$exists = $existingNames -contains 'deepseek-r1-8b-int8'
if (-not $exists) {
  Write-Host "[i] Creating Ollama model: deepseek-r1-8b-int8"
  Push-Location $r1Dir
  try {
    & ollama create deepseek-r1-8b-int8 -f Modelfile
    Write-Host "[OK] Ollama model created: deepseek-r1-8b-int8"
  } finally { Pop-Location }
}

# Verify model accessibility
try {
  & ollama show deepseek-r1-8b-int8 | Out-Null
  Write-Host "[OK] Ollama model metadata accessible."
} catch {
  throw "Ollama model 'deepseek-r1-8b-int8' not accessible via 'ollama show'."
}

Write-Host ""

# -----------------------------
# Step 5/6: Final verification gate (FAST run-time tests with timeout)
# -----------------------------
Write-Host "============================================================="
Write-Host " Step 5/6: Final verification gate (fast run-time tests)"
Write-Host "============================================================="

# Tunables
$VERIFY_TIMEOUT_SECONDS = 25
$ModelName = 'deepseek-r1-8b-int8'
$STOP_OLLAMA_AFTER_TESTS = $true
$OLLAMA_KEEP_ALIVE_SECONDS = 1

# Helper: strict python invoker
function Invoke-Python-Strict {
  param(
    [string[]]$PyArgs,
    [string]$FailMsg,
    [switch]$PassThru
  )
  $out = Invoke-Python $PyArgs
  $code = $LASTEXITCODE
  if ($code -ne 0) { throw $FailMsg }
  if ($PassThru) { return $out } elseif ($out) { $out | Write-Host }
}

# 1) Python re-check
Invoke-Python-Strict -PyArgs @('--version') -FailMsg "Python not available."
Invoke-Python-Strict -PyArgs @('-m','pip','check') -FailMsg "Pip dependency check failed."

# 2) Ollama quick metadata + run
Write-Host "[i] Testing DeepSeek R1 model with Ollama (timed)..."
$prevKeepAlive = $env:OLLAMA_KEEP_ALIVE
$env:OLLAMA_KEEP_ALIVE = "${OLLAMA_KEEP_ALIVE_SECONDS}s"

& ollama show $ModelName | Out-Null
if ($LASTEXITCODE -ne 0) {
  $env:OLLAMA_KEEP_ALIVE = $prevKeepAlive
  throw "Ollama model '$ModelName' not accessible via 'ollama show'."
}

function Invoke-Process-WithTimeout {
  param(
    [string]$FilePath,
    [string[]]$Arguments,
    [int]$TimeoutSeconds
  )
  $tmpBase = [System.IO.Path]::GetRandomFileName()
  $tmpOut  = Join-Path $env:TEMP "ollama_${tmpBase}_out.txt"
  $tmpErr  = Join-Path $env:TEMP "ollama_${tmpBase}_err.txt"
  foreach ($f in @($tmpOut,$tmpErr)) { if (Test-Path $f) { Remove-Item $f -Force -ErrorAction SilentlyContinue } }

  $p = Start-Process -FilePath $FilePath -ArgumentList $Arguments -NoNewWindow `
       -RedirectStandardOutput $tmpOut -RedirectStandardError $tmpErr -PassThru
  if (-not $p.WaitForExit($TimeoutSeconds * 1000)) {
    try { $p.Kill() } catch {}
  }
  $out = ""
  if (Test-Path $tmpOut) { try { $out += (Get-Content $tmpOut -Raw -ErrorAction SilentlyContinue) } catch {} }
  if (Test-Path $tmpErr) { try { $out += (Get-Content $tmpErr -Raw -ErrorAction SilentlyContinue) } catch {} }
  foreach ($f in @($tmpOut,$tmpErr)) { if (Test-Path $f) { Remove-Item $f -Force -ErrorAction SilentlyContinue } }
  return $out
}

try {
  $ollamaOut = Invoke-Process-WithTimeout -FilePath "ollama" -Arguments @("run",$ModelName,"-p","ping","-n","8") -TimeoutSeconds $VERIFY_TIMEOUT_SECONDS
  if (-not [string]::IsNullOrWhiteSpace($ollamaOut)) {
    Write-Host "[OK] Ollama model responded (limited tokens)."
  } else {
    throw "DeepSeek R1 quick run timed out ($VERIFY_TIMEOUT_SECONDS s) or returned empty output. Metadata was OK."
  }
}
finally {
  $env:OLLAMA_KEEP_ALIVE = $prevKeepAlive
  if ($STOP_OLLAMA_AFTER_TESTS) {
    try { & ollama stop $ModelName | Out-Null } catch {}
  }
}

# 3) all-MiniLM-L6-v2 quick encode
Write-Host "[i] Testing all-MiniLM-L6-v2 with SentenceTransformers..."
Invoke-Python-Strict -PyArgs @('-c', @"
from sentence_transformers import SentenceTransformer
import numpy as np, sys

m = SentenceTransformer(r'$miniDir', device='cpu')
emb = m.encode(['hello world'], convert_to_tensor=False, show_progress_bar=False, normalize_embeddings=False)
arr = np.asarray(emb)
print('[OK] all-MiniLM-L6-v2 responded with shape', getattr(arr, 'shape', None), 'dtype', getattr(arr, 'dtype', None))
sys.exit(0 if getattr(arr, 'ndim', 0) == 2 and arr.shape[1] > 0 else 1)
"@) -FailMsg "all-MiniLM-L6-v2 run test failed."

Write-Host "[OK] All fast run-time verification tests passed."
Write-Host "============================================================="

# -----------------------------
# Step 6/6: Display information (only reached on success)
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
