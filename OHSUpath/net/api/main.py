# net/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, auth, conversations, query, files

# Initialize database at startup (create missing tables)
from .db import init_db
init_db()

app = FastAPI(title="OHSUpath API")

# Initialize RAG service at startup
@app.on_event("startup")
async def startup_event():
    from .rag_service import get_rag_service
    import os

    # Get config path relative to project root
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config.yaml"
    )

    rag = get_rag_service()
    rag.initialize(yaml_path=config_path, use_yaml=True)

# CORS (can be relaxed when colocated with the gateway)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(query.router)
app.include_router(files.router)
