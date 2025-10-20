# net/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, auth, conversations, query

# Initialize database at startup (create missing tables)
from .db import init_db
init_db()

app = FastAPI(title="OHSUpath API")

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
