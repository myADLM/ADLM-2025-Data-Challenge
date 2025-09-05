#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'

# Move from bootstrap/linux to repo root
cd "$(dirname "$0")/../.."

APP_FILE="./app.py"
if [[ ! -f "$APP_FILE" ]]; then
  echo "[x] app.py not found at repo root."
  exit 1
fi

if ! command -v python3.11 >/dev/null 2>&1; then
  echo "[x] Python 3.11 not found. Run ./bootstrap/linux/setup.sh first."
  exit 1
fi

if [[ ! -d ".venv311" ]]; then
  echo "[x] Virtualenv missing. Run ./bootstrap/linux/setup.sh first."
  exit 1
fi

# shellcheck disable=SC1091
source ".venv311/bin/activate" || {
  echo "[x] Failed to activate virtualenv."
  exit 1
}

# --- RAG memory-safe defaults for Linux/WSL2 ---
export CONFIG__pdf_loader__num_proc="${CONFIG__pdf_loader__num_proc:-2}"
export CONFIG__split__num_proc="${CONFIG__split__num_proc:-2}"
export CONFIG__pdf_loader__prefetch_budget_mb="${CONFIG__pdf_loader__prefetch_budget_mb:-64}"
export CONFIG__pdf_loader__io_batch_files="${CONFIG__pdf_loader__io_batch_files:-8}"
export RAG_SHARD_FILES="${RAG_SHARD_FILES:-300}"


export CONFIG__runtime__device="cuda"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

export HF_HUB_DISABLE_SYMLINKS_WARNING=1


start_ollama_if_needed() {
  if curl -sSf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "[i] Ollama API is responsive."
    return
  fi
  if command -v systemctl >/dev/null 2>&1; then
    echo "[i] Starting Ollama via systemd ..."
    sudo systemctl start ollama || true
    for _ in {1..30}; do
      if curl -sSf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then return; fi
      sleep 0.5
    done
  fi
  echo "[i] Launching background ollama serve ..."
  nohup ollama serve >/dev/null 2>&1 &
  for _ in {1..40}; do
    if curl -sSf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then return; fi
    sleep 0.5
  done
  echo "[x] Ollama API not responding."
  exit 1
}

confirm_model() {
  local tag="deepseek-r1-8b-int8"
  local mf="./models/DeepseekR1/Modelfile"
  if ollama list 2>/dev/null | awk '{print $1}' | cut -d: -f1 | grep -qx "$tag"; then
    return
  fi
  if [[ ! -f "$mf" ]]; then
    echo "[x] Model '$tag' missing and no local Modelfile at $mf."
    echo "[x] Run ./bootstrap/linux/setup.sh first."
    exit 1
  fi
  echo "[i] Creating model '$tag' from local Modelfile ..."
  ollama create "$tag" -f "$mf" >/dev/null
  for _ in {1..40}; do
    if ollama list 2>/dev/null | awk '{print $1}' | cut -d: -f1 | grep -qx "$tag"; then return; fi
    sleep 0.5
  done
  echo "[x] Model '$tag' not visible after creation."
  exit 1
}

start_ollama_if_needed
confirm_model

echo "Launching Streamlit app ..."
python -m streamlit run "$APP_FILE"
