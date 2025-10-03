#!/bin/bash

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
docker-compose up --build -d

# Wait for backend container to be fully built and running
echo "Waiting for backend container to be ready..."
until docker-compose ps backend | grep -q "Up"; do
  sleep 1
done

# Wait for backend health endpoint
echo "Waiting for backend to be ready at http://localhost:5174/ping ..."

# Wait for health check without streaming logs
while true; do
  echo $(curl -s http://localhost:5174/ping)
  if curl -s http://localhost:5174/ping 2>/dev/null | grep -q '"ok": true'; then
    echo "Backend is healthy!"
    break
  fi
  echo "Waiting for backend initialization..."
  sleep 2
done

# Wait a moment to ensure backend is fully initialized
sleep 2

echo "Services started!"
echo "Go to http://localhost:5173 to access the application."
exit 0
