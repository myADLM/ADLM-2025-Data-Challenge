# Quick Start

### Design
See [design.md](backend/design.md) for more details.

### Prerequisites
- **macOS 12+ (Monterey or newer)**:
  - Docker Desktop for Mac
- **Linux (Ubuntu 22.04 LTS typical)**:
  - Docker Engine
  - docker-compose (Compose v1) or Docker Compose plugin (v2)

Verify installation:
```bash
docker --version
docker-compose --version
```

### Start the application
#### IMPORTANT
The backend build process takes a long time and costs some money to generate the embeddings and contextual annotations. I built the database and uploaded it to GitHub so that you don't need to.

Building the database from scratch requires [AWS credentials](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html) with permission to execute the Amazon Nova Lite model in Amazon Bedrock. You do not need to do this to run the application.

If you want to use the vector search capabilities and/or Chat features, you will need to add the following environment variable to the `local_orchestration/.env` file:

```
OPENAI_API_KEY
```

If you just want BM25 search and document retrieval, you don't need set that environment variable (not recommended).

From the project root:
```bash
chmod +x setup.sh
./setup.sh
```
- Builds and starts services via Docker Compose
- If you use a pre-built database, the build process will skip those steps.
- Open `http://localhost:5173`

### Stop the application
From the project root:
```bash
chmod +x teardown.sh
./teardown.sh
```

### Notes
- Ensure Docker Desktop/daemon is running before starting
- If ports are busy, stop conflicting services or adjust `local_orchestration/docker-compose.yml`

## High Level Design

- **Frontend (Vite + React)**
  - Serves the UI at `http://localhost:5173`.
  - Communicates with the backend over HTTP (CORS-enabled).
  - React-based.
  - Almost entirely vibe-coded.

- **Backend (FastAPI + Uvicorn)**
  - Exposes REST endpoints: health (`/ping`), document download (`/documents/{path}`), and chat (`/chat`).
  - On startup, builds a local database from `backend/app/input_data/raw_input_data.zip` into `backend/app/database/medallions` (bronze/silver/gold).
  - Provides search and chat orchestration using BM25 and vector search over chunked documents.
  - For an in-depth description of the search functions and research, see [backend/design.md](backend/design.md)

- **Local Storage (bind mounts)**
  - `backend/app/database` and `backend/app/input_data` are mounted into the backend container for persistence.

- **Local AWS Emulation (LocalStack)**
  - Provides an S3-compatible endpoint for storing/querying objects during development.
  - Backend utilities in `app/src/util/aws.py` and `app/src/util/s3.py` interact with this service.

- **Container Orchestration (Docker Compose)**
  - Services: `frontend`, `backend`, `localstack` on a shared `indigo-network` bridge.
  - Ports: frontend `5173`, backend `5174`, localstack `4566`.

### Data Flow (high-level)
1. Input ZIP placed at `backend/app/input_data/raw_input_data.zip` (or downloaded during the build process).
2. Backend builds medallions (bronze → gold) on startup.
3. Refined data is used to build the BM25-IDF index and vector database.
4. Frontend UI runs at `http://localhost:5173`
5. User submits a query
6. Backend retrieves relevant chunks and returns responses; documents are available to download.
