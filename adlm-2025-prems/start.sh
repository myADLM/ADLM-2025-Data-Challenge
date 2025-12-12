#!/bin/bash

# Start both Django and React as background processes
# This script runs both services in the same container

set -e

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $DJANGO_PID $REACT_PID 2>/dev/null || true
    wait
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

echo "Starting Django API server on port 8000..."
cd /app/chat_api_dj
uv run uvicorn chat_web_dj.asgi:application --host 0.0.0.0 --port 8000 --workers 4 &
DJANGO_PID=$!

echo "Starting React development server on port 3000..."
cd /app/chat_web
HOST=${HOST:-0.0.0.0} npm start &
REACT_PID=$!

echo "Both services started:"
echo "  - Django API: http://localhost:8000"
echo "  - React App: http://localhost:3000"
echo "  - Django Admin: http://localhost:8000/admin"
echo "  - API Docs: http://localhost:8000/api/docs"

# Wait for both processes
wait $DJANGO_PID $REACT_PID
