#!/usr/bin/env bash
# =====================================================================
# Full Linux Setup (Ubuntu/Debian)
# - Uses only relative paths after cd to repo root
# - Ensure Python 3.11 (+ venv + dev headers)
# - pip install + pip check
# - Download and verify HF models into ./models/...
# - Install/start Ollama and create model deepseek-r1-8b-int8 from local GGUF
# - Fail fast with logs to ./setup.log
# =====================================================================

set -Eeuo pipefail
IFS=$'\n\t'

# Move from bootstrap/linux to repo root
cd "$(dirname "$0")/../.."

LOG="./setup.log"
exec > >(tee -a "$LOG") 2>&1

echo "============================================================="
echo " Full Linux Setup"
echo "============================================================="

# Internet connectivity check (HTTPS 443 to huggingface.co)
echo "[i] Checking internet connectivity to huggingface.co:443 ..."
if ! timeout 2 bash -c 'exec 3<>/dev/tcp/huggingface.co/443' 2>/dev/null; then
  if ! curl -sSfI --connect-timeout 2 https://huggingface.co >/dev/null; then
    echo "[x] No internet connectivity to huggingface.co:443."
    exit 1
  fi
fi
echo "[OK] Internet connectivity looks good."

trap 'echo; echo "[x] Unexpected error. See log: ./setup.log"' ERR

# Constants (relative to repo root)
MODELS_ROOT="./models"
R1_DIR="./models/DeepseekR1"
MINI_DIR="./models/all-MiniLM-L6-v2"
INST_DIR="./models/InstructorXL"
R1_FILE="DeepSeek-R1-Distill-Llama-8B-Q8_0.gguf"

# Step 0: base packages
echo "============================================================="
echo " Step 0/6: Ensure base packages"
echo "============================================================="
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y curl ca-certificates git software-properties-common build-essential tmux nodejs npm
else
  echo "[x] This script targets Ubuntu/Debian (apt-get)."
  exit 1
fi

if ! command -v node >/dev/null 2>&1 && command -v nodejs >/dev/null 2>&1; then
  sudo ln -sf "$(command -v nodejs)" /usr/bin/node
fi
echo "[check] node: $(node -v 2>/dev/null || echo missing)"
echo "[check] npm : $(npm -v 2>/dev/null || echo missing)"

if [[ -f "./net/gateway/package.json" ]]; then
  echo "[i] Installing gateway deps (net/gateway) ..."
  (cd ./net/gateway && { [[ -f package-lock.json ]] && npm ci || npm i; })
else
  echo "[i] Skip gateway: no package.json"
fi
if [[ -f "./net/web/package.json" ]]; then
  echo "[i] Installing web deps (net/web) ..."
  (cd ./net/web && { [[ -f package-lock.json ]] && npm ci || npm i; })
else
  echo "[i] Skip web: no package.json"
fi

# Helpers: Python 3.11 (+ venv + dev headers)
PY311_BIN=""
ensure_python311() {
  # If python3.11 already exists, still ensure venv and dev headers
  if command -v python3.11 >/dev/null 2>&1; then
    PY311_BIN="python3.11"
    sudo apt-get install -y python3.11-venv python3.11-dev || true
  else
    echo "[i] Installing Python 3.11 ..."
    # Try from Ubuntu first
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev || true
    # If python still missing, add deadsnakes PPA and retry
    if ! command -v python3.11 >/dev/null 2>&1; then
      sudo add-apt-repository -y ppa:deadsnakes/ppa
      sudo apt-get update -y
      sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
    fi
    if ! command -v python3.11 >/dev/null 2>&1; then
      echo "[x] Python 3.11 not found after installation."
      exit 1
    fi
    PY311_BIN="python3.11"
  fi

  # Verify headers exist (required by C/C++ extension builds, e.g. pytrec-eval)
  if [[ ! -f "/usr/include/python3.11/Python.h" ]]; then
    # Some distros place headers under different include roots; hard fail if missing
    echo "[x] Missing Python.h (python3.11-dev). Please ensure python3.11-dev is available."
    exit 1
  fi
}

# Step 1: Python 3.11 + venv + dev headers
echo "============================================================="
echo " Step 1/6: Python 3.11 and venv"
echo "============================================================="
ensure_python311
echo "[OK] Using $("$PY311_BIN" -V 2>&1)"

VENV_DIR=".venv311"
if [[ ! -d "$VENV_DIR" ]]; then
  "$PY311_BIN" -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source ".venv311/bin/activate"
python -V

# Step 2: pip install + pip check
echo "============================================================="
echo " Step 2/6: Install Python requirements"
echo "============================================================="
python -m pip install --upgrade pip setuptools wheel

# Pin numpy first to avoid conflicts
echo "[i] Installing numpy ..."
python -m pip install "numpy<2,>=1.24"

# Detect CUDA and install JAX with correct version before other packages
echo "[i] Detecting CUDA availability ..."
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "[i] NVIDIA GPU detected, installing JAX with CUDA 12 ..."
  python -m pip install "jax[cuda12]<0.8"
else
  echo "[i] No GPU detected, installing JAX CPU-only ..."
  python -m pip install "jax<0.8" "jaxlib<0.8"
fi

# Install other requirements
if [[ -f "./requirements.txt" ]]; then
  echo "[i] Installing from requirements.txt ..."
  python -m pip install -r ./requirements.txt
else
  echo "[i] No requirements.txt found, skipping."
fi

python -m pip install --upgrade huggingface_hub sentence-transformers
python -m pip install -q hf_transfer || true
python -m pip check

# Step 3: download and verify models
echo "============================================================="
echo " Step 3/6: Download and verify models"
echo "============================================================="
export HF_HUB_DISABLE_PROGRESS_BARS=0
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_HUB_OFFLINE=0
export TQDM_DISABLE=0

mkdir -p "$MODELS_ROOT" "$R1_DIR" "$MINI_DIR" "$INST_DIR"
mkdir -p ".tmp"
PY_HELPER=".tmp/hf_download_$$.py"

cat > "$PY_HELPER" << 'PYCODE'
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

def has_required_files_model_dir(p: str) -> bool:
    tok = any(Path(p, fn).exists() for fn in ("tokenizer.json","vocab.txt","spiece.model","tokenizer.model"))
    wts = any(Path(p, fn).exists() for fn in ("model.safetensors","pytorch_model.bin","flax_model.msgpack"))
    return tok and wts

ok = True

# 1) DeepSeek R1 GGUF (>=7GB)
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
PYCODE

export R1_DIR="$R1_DIR" MINILM_DIR="$MINI_DIR" INSTRUCTOR_DIR="$INST_DIR" R1_FILE="$R1_FILE"
python "$PY_HELPER"
rm -rf ".tmp"
echo

# Step 4: Ollama + local model
echo "============================================================="
echo " Step 4/6: Ensure Ollama and local model"
echo "============================================================="

if ! command -v ollama >/dev/null 2>&1; then
  echo "[i] Installing Ollama ..."
  curl -fsSL https://ollama.com/install.sh | sudo bash
fi
if ! command -v ollama >/dev/null 2>&1; then
  echo "[x] Ollama CLI not found after installation."
  exit 1
fi

if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl enable --now ollama || true
fi

api_ok=0
for _ in {1..40}; do
  if curl -sSf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then api_ok=1; break; fi
  sleep 0.5
done
if [[ "$api_ok" -ne 1 ]]; then
  echo "[i] Falling back to background serve ..."
  nohup ollama serve >/dev/null 2>&1 &
  for _ in {1..40}; do
    if curl -sSf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then api_ok=1; break; fi
    sleep 0.5
  done
fi
if [[ "$api_ok" -ne 1 ]]; then
  echo "[x] Ollama API not responding."
  exit 1
fi
echo "[OK] Ollama API responsive."

MODELFILE_PATH="$R1_DIR/Modelfile"
if [[ ! -f "$R1_DIR/$R1_FILE" ]]; then
  echo "[x] GGUF missing: $R1_DIR/$R1_FILE"
  exit 1
fi
if [[ ! -f "$MODELFILE_PATH" ]]; then
  echo "FROM ./$R1_FILE" > "$MODELFILE_PATH"
  echo "[OK] Modelfile created: $MODELFILE_PATH"
else
  if ! grep -q "FROM ./$R1_FILE" "$MODELFILE_PATH"; then
    echo "FROM ./$R1_FILE" > "$MODELFILE_PATH"
    echo "[i] Modelfile updated to reference ./$R1_FILE"
  else
    echo "[OK] Modelfile already references ./$R1_FILE"
  fi
fi

MODEL_TAG="deepseek-r1-8b-int8"
if ! (ollama list 2>/dev/null | awk '{print $1}' | cut -d: -f1 | grep -qx "$MODEL_TAG"); then
  echo "[i] Creating Ollama model: $MODEL_TAG"
  (cd "$R1_DIR" && ollama create "$MODEL_TAG" -f Modelfile)
fi

if ! ollama show "$MODEL_TAG" >/dev/null 2>&1; then
  echo "[x] Ollama model '$MODEL_TAG' not accessible."
  exit 1
fi
echo

# Step 5: fast runtime checks
echo "============================================================="
echo " Step 5/6: Fast runtime checks"
echo "============================================================="
python -m pip check

echo "[i] Testing Ollama quick run (timeout 25s) ..."
export OLLAMA_KEEP_ALIVE="1s"

READINESS_PAYLOAD=$(cat <<'JSON'
{
  "model": "__MODEL__",
  "prompt": "ping",
  "options": { "num_predict": 8 },
  "stream": false
}
JSON
)
READINESS_PAYLOAD="${READINESS_PAYLOAD/__MODEL__/$MODEL_TAG}"

if ! RESP="$(timeout 25s curl -sSf -H 'Content-Type: application/json' \
  -X POST http://127.0.0.1:11434/api/generate \
  -d "$READINESS_PAYLOAD" 2>&1)"; then
  echo "$RESP"
  echo "[x] Ollama /api/generate request failed."
  exit 1
fi

if echo "$RESP" | grep -q "\"response\""; then
  echo "[OK] Ollama responded."
else
  echo "$RESP"
  echo "[x] Unexpected response payload from Ollama."
  exit 1
fi

echo "[i] Testing all-MiniLM-L6-v2 with SentenceTransformers ..."
python - << 'PY'
from sentence_transformers import SentenceTransformer
import numpy as np, sys
m = SentenceTransformer(r'./models/all-MiniLM-L6-v2', device='cpu')
emb = m.encode(['hello world'], convert_to_tensor=False, show_progress_bar=False, normalize_embeddings=False)
arr = np.asarray(emb)
ok = (getattr(arr, 'ndim', 0) == 2 and arr.shape[1] > 0)
print('[OK] all-MiniLM-L6-v2 responded with shape', getattr(arr,'shape',None), 'dtype', getattr(arr,'dtype',None))
sys.exit(0 if ok else 1)
PY

echo "[OK] All fast checks passed."
echo "============================================================="

# Step 6: next step
echo "============================================================="
echo " Step 6/6: Next step"
echo "============================================================="
echo
echo "Run the app with:"
echo "  ./bootstrap/linux/run_app.sh"
echo
echo "Setup complete. Log: ./setup.log"
