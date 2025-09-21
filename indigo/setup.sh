#!/bin/bash

# Start the local orchestration
echo "Starting the application..."
cd local_orchestration

# Build and start all services
docker-compose up --build -d

echo "Services started!"
echo Go to http://localhost:5173 to access the application.
