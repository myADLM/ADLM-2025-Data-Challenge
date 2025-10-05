#!/bin/bash

# Exit on any error
set -e

# Start the local orchestration
echo "Starting the application..."
cd local_orchestration

# If OPENAI_API_KEY is set, write it to a local .env so docker-compose passes it through
if [ -n "$OPENAI_API_KEY" ]; then
  echo "Passing OPENAI_API_KEY to backend container via .env"
  echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
else
  echo "OPENAI_API_KEY is not set; backend will not have OpenAI access"
fi

# Build and start all services
echo "Building and starting services..."
if ! docker-compose up --build -d; then
  echo "ERROR: Failed to build or start services with docker-compose"
  exit 1
fi

# Wait for backend container to be fully built and running
echo "Waiting for backend container to be ready..."
timeout=60  # 60 second timeout
elapsed=0
until docker-compose ps backend | grep -q "Up"; do
  # Check if backend container has exited with an error
  if docker-compose ps backend | grep -q "Exited"; then
    echo "ERROR: Backend container has exited. Checking logs..."
    docker-compose logs backend
    echo "ERROR: Backend container failed to start properly"
    exit 1
  fi
  
  if [ $elapsed -ge $timeout ]; then
    echo "ERROR: Timeout waiting for backend container to start (${timeout}s)"
    echo "Backend container status:"
    docker-compose ps backend
    echo "Backend container logs:"
    docker-compose logs backend
    exit 1
  fi
  
  sleep 1
  elapsed=$((elapsed + 1))
done

# Wait for backend health endpoint
echo "Waiting for backend to be ready at http://localhost:5174/ping ..."
echo "This may take a few minutes while the backend initializes..."

# Wait for health check without streaming logs
timeout=120  # 2 minute timeout for health check
elapsed=0
while true; do
  # Check if backend container is still running
  if ! docker-compose ps backend | grep -q "Up"; then
    echo "ERROR: Backend container stopped unexpectedly"
    echo "Backend container status:"
    docker-compose ps backend
    echo "Backend container logs:"
    docker-compose logs backend
    exit 1
  fi
  
  # Use curl with proper error handling to avoid script exit
  if response=$(curl -s http://localhost:5174/ping 2>/dev/null); then
    echo "[${elapsed}s] Response: $response"
    
    # Check if response contains "ok":true (with or without spaces)
    if echo "$response" | grep -q '"ok" *: *true'; then
      echo "Backend is healthy!"
      break
    else
      echo "Backend not ready yet, waiting..."
    fi
  else
    echo "Backend not responding yet, waiting... [${elapsed}s]"
  fi
  
  if [ $elapsed -ge $timeout ]; then
    echo "ERROR: Timeout waiting for backend health check (${timeout}s)"
    echo "Backend container status:"
    docker-compose ps backend
    echo "Backend container logs:"
    docker-compose logs backend
    exit 1
  fi
  
  echo "Waiting for backend initialization..."
  sleep 2
  elapsed=$((elapsed + 2))
done

# Final check that backend is still running
if ! docker-compose ps backend | grep -q "Up"; then
  echo "ERROR: Backend container stopped after health check"
  echo "Backend container status:"
  docker-compose ps backend
  echo "Backend container logs:"
  docker-compose logs backend
  exit 1
fi

# Wait a moment to ensure backend is fully initialized
sleep 2

echo "Services started!"
echo "Go to http://localhost:5173 to access the application."
exit 0
