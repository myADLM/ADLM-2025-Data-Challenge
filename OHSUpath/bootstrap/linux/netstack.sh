#!/usr/bin/env bash
# netstack.sh - bootstrap env + start/stop/status/logs for net (api/gateway/web)
set -euo pipefail
set -o errtrace

# -------- error handling --------
on_error() {
  local exit_code="$1"
  local failed_cmd="$2"
  local line_no="$3"
  echo "[ERROR] command failed (exit ${exit_code})"
  echo "        at: ${0}:${line_no}"
  echo "        cmd: ${failed_cmd}"
  # function stack (skip on_error itself)
  local i=1
  while [ $i -lt ${#FUNCNAME[@]} ]; do
    local f="${FUNCNAME[$i]}"
    local src="${BASH_SOURCE[$i]}"
    local ln="${BASH_LINENO[$((i-1))]}"
    echo "        stack[$i]: ${f} at ${src}:${ln}"
    i=$((i+1))
  done
}
trap 'on_error $? "$BASH_COMMAND" $LINENO' ERR

# global debug flag: NETSTACK_DEBUG=1 or first arg "--debug"
if [[ "${NETSTACK_DEBUG:-0}" == "1" ]]; then set -x; fi
if [[ "${1:-}" == "--debug" ]]; then set -x; shift; fi

# ---------- Paths ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OH_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
NET_DIR="${OH_DIR}/net"
GW_DIR="${NET_DIR}/gateway"
WEB_DIR="${NET_DIR}/web"
LOG_DIR="${NET_DIR}/logs"
PY_VENV="${OH_DIR}/.venv311"
SESSION_NAME="ohsu-net"

mkdir -p "${GW_DIR}" "${WEB_DIR}" "${LOG_DIR}"

# ---------- Helpers ----------
gen_secret() { openssl rand -hex 32 2>/dev/null || (head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n'); }
backup_file() {
  local f="${1:-}"
  if [ -n "$f" ] && [ -f "$f" ]; then
    cp "$f" "$f.bak.$(date +%Y%m%d%H%M%S)"
  fi
}
read_kv() { grep -E "^$2=" "$1" 2>/dev/null | head -n1 | cut -d'=' -f2- | tr -d $'\r' || true; }
set_kv() { # set_kv FILE KEY VALUE (insert if missing; replace only when allowed)
  local f="$1" k="$2" v="$3"
  touch "$f"
  if grep -qE "^$k=" "$f"; then
    if [[ "${ALLOW_OVERWRITE:-0}" -eq 1 ]]; then sed -i "s#^$k=.*#$k=$v#g" "$f"; fi
  else
    echo "$k=$v" >> "$f"
  fi
}
need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[-] missing dependency: $1"
    case "$1" in
      node|npm)
        echo "    install (Ubuntu): curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
        ;;
      python3)
        echo "    install (Ubuntu): sudo apt-get install -y python3.11 python3.11-venv python3.11-dev"
        ;;
      openssl)
        echo "    install (Ubuntu): sudo apt-get install -y openssl"
        ;;
      tmux)
        echo "    optional (Ubuntu): sudo apt-get install -y tmux"
        ;;
    esac
    exit 1
  fi
}

# ---------- Commands ----------
cmd_help() {
cat <<'EOF'
Usage: netstack.sh <command> [options]

Commands:
  bootstrap [--prod https://domain] [--rotate-jwt] [--rotate-api-key] [--force]
      Create/merge .env for api/gateway/web. By default does NOT overwrite existing values.
      --prod            set ORIGIN to real domain and COOKIE_SECURE=true
      --rotate-jwt      rotate JWT_SECRET (forces re-login)
      --rotate-api-key  rotate INTERNAL_SHARED_KEY (gateway <-> api)
      --force           overwrite existing values

  up       Install deps and start dev servers: API(8000) Gateway(3000) Web(4000)
  down     Stop background/tmux servers
  status   Show running state
  logs     Tail logs

Examples:
  bash netstack.sh bootstrap
  bash netstack.sh bootstrap --prod https://actual.domain
  bash netstack.sh up
  bash netstack.sh down
EOF
}


cmd_bootstrap() {
  local MODE="dev" PROD_ORIGIN="" ROTATE_JWT=0 ROTATE_API=0 FORCE=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --prod) MODE="prod"; PROD_ORIGIN="${2:-}"; shift 2;;
      --rotate-jwt) ROTATE_JWT=1; shift;;
      --rotate-api-key) ROTATE_API=1; shift;;
      --force) FORCE=1; shift;;
      *) shift;;
    esac
  done
  if [[ "$MODE" == "prod" && -z "$PROD_ORIGIN" ]]; then
    echo "Usage: netstack.sh bootstrap --prod https://actual.domain"; exit 1;
  fi

  local PY_ENV="${NET_DIR}/.env.api"
  local GW_ENV="${GW_DIR}/.env"
  local WEB_ENV="${WEB_DIR}/.env.local"

  export ALLOW_OVERWRITE=0
  [[ $FORCE -eq 1 ]] && ALLOW_OVERWRITE=1

  # unify internal key (single source of truth)
  local EXIST_GW EXIST_API INTERNAL_KEY
  EXIST_GW="$( [[ -f "$GW_ENV" ]] && read_kv "$GW_ENV" INTERNAL_SHARED_KEY || true )"
  EXIST_API="$( [[ -f "$PY_ENV" ]] && read_kv "$PY_ENV" INTERNAL_SHARED_KEY || true )"
  INTERNAL_KEY="${EXIST_GW:-${EXIST_API:-$(gen_secret)}}"
  [[ $ROTATE_API -eq 1 ]] && INTERNAL_KEY="$(gen_secret)"

  # clean old var names (no backup)
  sed -i '/^SERVICE_API_KEY=/d' "$PY_ENV" 2>/dev/null || true
  sed -i '/^API_KEY=/d'         "$GW_ENV" 2>/dev/null || true

  # API env
  ALLOW_OVERWRITE=1
  set_kv "$PY_ENV" "INTERNAL_SHARED_KEY" "$INTERNAL_KEY"
  ALLOW_OVERWRITE=$FORCE
  set_kv "$PY_ENV" "ALLOWED_ORIGINS" ""
  set_kv "$PY_ENV" "DATA_DIR" "./data"

  # Gateway env
  ALLOW_OVERWRITE=1
  set_kv "$GW_ENV" "INTERNAL_SHARED_KEY" "$INTERNAL_KEY"
  ALLOW_OVERWRITE=$FORCE
  set_kv "$GW_ENV" "PORT" "3000"
  set_kv "$GW_ENV" "PY_API" "http://127.0.0.1:8000"
  set_kv "$GW_ENV" "API_BASE" "http://localhost:8000"

  # JWT (sign cookie)
  local EXIST_JWT JWT_SECRET
  EXIST_JWT="$( [[ -f "$GW_ENV" ]] && read_kv "$GW_ENV" JWT_SECRET || true )"
  JWT_SECRET="${EXIST_JWT:-$(gen_secret)}"
  if [[ $ROTATE_JWT -eq 1 ]]; then
    ALLOW_OVERWRITE=1
    set_kv "$GW_ENV" "JWT_SECRET" "$(gen_secret)"
    ALLOW_OVERWRITE=$FORCE
  else
    set_kv "$GW_ENV" "JWT_SECRET" "$JWT_SECRET"
  fi

  set_kv "$GW_ENV" "COOKIE_NAME" "sid"
  local COOKIE_SECURE ORIGIN
  COOKIE_SECURE="$([[ "$MODE" == "prod" ]] && echo true || echo false)"
  ORIGIN="$([[ "$MODE" == "prod" ]] && echo "$PROD_ORIGIN" || echo "http://localhost:4000")"
  set_kv "$GW_ENV" "CORS_ORIGIN" "$ORIGIN"
  set_kv "$GW_ENV" "COOKIE_SECURE" "$COOKIE_SECURE"
  set_kv "$GW_ENV" "COOKIE_SAMESITE" "Lax"
  set_kv "$GW_ENV" "ORIGIN" "$ORIGIN"

  # Web env
  if [[ ! -f "$WEB_ENV" || $FORCE -eq 1 ]]; then
    cat > "$WEB_ENV" <<'EOF'
NEXT_PUBLIC_API_BASE=http://localhost:3000
EOF
  fi

  # consistency check
  local api_key gw_key
  api_key="$(read_kv "$PY_ENV" INTERNAL_SHARED_KEY)"
  gw_key="$(read_kv "$GW_ENV" INTERNAL_SHARED_KEY)"
  if [[ -z "$api_key" || -z "$gw_key" || "$api_key" != "$gw_key" ]]; then
    echo "[WARN] INTERNAL_SHARED_KEY not aligned."
    echo "       api: ${api_key:0:8}..., gw: ${gw_key:0:8}..."
  fi

  echo "[OK] bootstrap complete."
  echo "  api env : $PY_ENV"
  echo "  gw  env : $GW_ENV"
  echo "  web env : $WEB_ENV"
  echo "  mode=${MODE} origin=${ORIGIN} cookie_secure=${COOKIE_SECURE}"
  [[ $ROTATE_API -eq 1 ]] && echo "  Internal key rotated (restart gateway+api)"
  [[ $ROTATE_JWT -eq 1 ]] && echo "  JWT secret rotated (users must re-login)"
}


cmd_up() {
  [[ -f "${NET_DIR}/.env.api" && -f "${GW_DIR}/.env" && -f "${WEB_DIR}/.env.local" ]] || cmd_bootstrap

  need python3
  need npm

  if [[ ! -d "${PY_VENV}" ]]; then
    echo "[info] creating venv at ${PY_VENV}"
    python3 -m venv "${PY_VENV}"
  fi
  # shellcheck disable=SC1091
  source "${PY_VENV}/bin/activate"
  echo "[check] python: $(python -V 2>&1)"
  pip -q install --upgrade pip
  [[ -f "${OH_DIR}/requirements.txt" ]] && pip -q install -r "${OH_DIR}/requirements.txt" || true
  pip -q install fastapi uvicorn sqlmodel python-dotenv pydantic

  echo "[check] node: $(node -v 2>/dev/null || echo missing)"
  echo "[check] npm : $(npm -v 2>/dev/null || echo missing)"

  pushd "${GW_DIR}" >/dev/null
  if [[ -f package-lock.json ]]; then npm ci; else npm i; fi
  popd >/dev/null

  pushd "${WEB_DIR}" >/dev/null
  if [[ -f package-lock.json ]]; then npm ci; else npm i; fi
  popd >/dev/null

  local API_CMD GW_CMD WEB_CMD
  API_CMD="bash -lc 'cd ${OH_DIR} && source ${PY_VENV}/bin/activate && PYTHONPATH=${OH_DIR} uvicorn net.api.main:app --host 127.0.0.1 --port 8000 --reload --env-file ${NET_DIR}/.env.api 2>&1 | tee ${LOG_DIR}/api.log'"
  GW_CMD="bash -lc 'cd ${GW_DIR} && npm run dev 2>&1 | tee ${LOG_DIR}/gateway.log'"
  WEB_CMD="bash -lc 'cd ${WEB_DIR} && npm run dev 2>&1 | tee ${LOG_DIR}/web.log'"

  if command -v tmux >/dev/null 2>&1; then
    # kill old session if exists
    tmux has-session -t "$SESSION_NAME" 2>/dev/null && tmux kill-session -t "$SESSION_NAME" || true
    # create session with 3 windows (api/gateway/web)
    if tmux new-session -d -s "$SESSION_NAME" -n api "$API_CMD"; then
      tmux new-window  -t "$SESSION_NAME" -n gateway "$GW_CMD"
      tmux new-window  -t "$SESSION_NAME" -n web     "$WEB_CMD"
      echo "[OK] tmux session '${SESSION_NAME}' started. Attach: tmux attach -t ${SESSION_NAME}"
    else
      echo "[WARN] tmux failed to start; falling back to background mode."
      nohup bash -c "${API_CMD}" >/dev/null 2>&1 & echo $! > "${LOG_DIR}/api.pid"
      nohup bash -c "${GW_CMD}"  >/dev/null 2>&1 & echo $! > "${LOG_DIR}/gateway.pid"
      nohup bash -c "${WEB_CMD}" >/dev/null 2>&1 & echo $! > "${LOG_DIR}/web.pid"
      echo "PIDs written: ${LOG_DIR}/api.pid gateway.pid web.pid"
    fi
  else
    echo "[WARN] tmux not found. Starting in background; logs at ${LOG_DIR}/"
    nohup bash -c "${API_CMD}" >/dev/null 2>&1 & echo $! > "${LOG_DIR}/api.pid"
    nohup bash -c "${GW_CMD}"  >/dev/null 2>&1 & echo $! > "${LOG_DIR}/gateway.pid"
    nohup bash -c "${WEB_CMD}" >/dev/null 2>&1 & echo $! > "${LOG_DIR}/web.pid"
    echo "PIDs written: ${LOG_DIR}/api.pid gateway.pid web.pid"
  fi
  echo "[OK] dev servers up -> Web: http://localhost:4000"
}

cmd_down() {
  if command -v tmux >/dev/null 2>&1 && tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    tmux kill-session -t "$SESSION_NAME"
    echo "[OK] tmux session '${SESSION_NAME}' stopped."
  fi
  for n in api gateway web; do
    if [[ -f "${LOG_DIR}/${n}.pid" ]]; then
      local PID; PID="$(cat "${LOG_DIR}/${n}.pid")"
      kill "$PID" 2>/dev/null || true
      rm -f "${LOG_DIR}/${n}.pid"
      echo "stopped ${n} (pid ${PID})"
    fi
  done
}

cmd_status() {
  if command -v tmux >/dev/null 2>&1 && tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "[tmux] session '${SESSION_NAME}' running (attach: tmux attach -t ${SESSION_NAME})"
  else
    echo "[tmux] no session"
  fi
  for n in api gateway web; do
    if [[ -f "${LOG_DIR}/${n}.pid" ]]; then
      local PID; PID="$(cat "${LOG_DIR}/${n}.pid")"
      if ps -p "$PID" >/dev/null 2>&1; then echo "[bg] ${n} running (pid ${PID})"; else echo "[bg] ${n} not running"; fi
    else
      echo "[bg] ${n} not running"
    fi
  done
}


cmd_logs() {
  ls -l "${LOG_DIR}"/*.log 2>/dev/null || true
  echo "Tailing logs (Ctrl-C to exit)..."
  tail -n +1 -f "${LOG_DIR}"/*.log 2>/dev/null || echo "no logs yet."
}

# ---------- Entry ----------
CMD="${1:-help}"; shift || true
case "$CMD" in
  help|-h|--help)     cmd_help;;
  bootstrap)          cmd_bootstrap "$@";;
  up)                 cmd_up;;
  down)               cmd_down;;
  status)             cmd_status;;
  logs)               cmd_logs;;
  *) echo "unknown command: $CMD"; cmd_help; exit 1;;
esac
