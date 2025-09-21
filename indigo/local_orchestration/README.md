# Local Orchestration

This directory contains the Docker-based local orchestration for the Indigo application.

## Services

- **Frontend**: React app served by nginx on port 5173
- **Backend**: FastAPI app on port 5174
- **LocalStack**: AWS services emulation on port 4566

## Quick Start

1. Make sure Docker and Docker Compose are installed
2. Run the orchestration:
   ```bash
   ./start.sh
   ```
   
   Or manually:
   ```bash
   docker-compose up --build
   ```

## Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5174
- **LocalStack**: http://localhost:4566

## Architecture

- Frontend and backend are containerized and communicate via Docker network
- Frontend nginx proxies `/api/*` requests to the backend service
- All services share the `indigo-network` Docker network
- Backend database and input data are mounted as volumes for persistence

## Development

To rebuild services after code changes:
```bash
docker-compose up --build
```

To stop all services:
```bash
docker-compose down
```

To view logs:
```bash
docker-compose logs -f [service-name]
```
