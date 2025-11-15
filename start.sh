#!/bin/bash
# web app startup (macos/linux)

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

echo "Starting Knowledge Graph Web App..."
echo ""

mkdir -p "$REPO_ROOT/logs"

# Verify environment configuration
if [ ! -f ".env" ]; then
    echo "Error: .env file not found"
    echo "Please create .env file with required variables (NEO4J_URI, AWS credentials, etc.)"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Kill existing processes on ports 5001 and 3001
echo "Cleaning up existing processes..."
kill_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    elif command -v fuser >/dev/null 2>&1; then
        fuser -k $port/tcp 2>/dev/null || true
    elif command -v ss >/dev/null 2>&1; then
        ss -lptn "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | cut -d= -f2 | xargs kill -9 2>/dev/null || true
    fi
}
kill_port 5001
kill_port 3001
sleep 1

# Start Flask API
echo "Starting Flask API on port 5001..."
cd "$REPO_ROOT" && uv run python src/api/app.py > "$REPO_ROOT/logs/flask_api.log" 2>&1 &
FLASK_PID=$!

sleep 4
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "[OK] Flask API is running (PID: $FLASK_PID)"
else
    echo "[FAIL] Flask API failed to start. Check $REPO_ROOT/logs/flask_api.log"
    exit 1
fi

# Start frontend
echo "Starting Vite frontend on port 3001..."
cd "$REPO_ROOT/frontend"
npm run dev > "$REPO_ROOT/logs/vite.log" 2>&1 &
VITE_PID=$!
cd "$REPO_ROOT"

sleep 4
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo "[OK] Vite dev server is running (PID: $VITE_PID)"
else
    echo "[FAIL] Vite dev server failed to start. Check $REPO_ROOT/logs/vite.log"
    exit 1
fi

echo ""
echo "=========================================="
echo "Frontend and API are up and running!"
echo "=========================================="
echo "Frontend: http://localhost:3001"
echo "API Health: http://localhost:5001/health"
echo "  Flask: tail -f $REPO_ROOT/logs/flask_api.log"
echo "  Vite: tail -f $REPO_ROOT/logs/vite.log"
echo ""

# Keep it running
wait
