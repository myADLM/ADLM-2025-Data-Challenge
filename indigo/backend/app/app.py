from pathlib import Path

import polars as pl
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.src.api.api_methods import *
from app.src.api.api_objects import ChatRequest, ChatResponse
from app.src.database.build_database import build_database
from app.src.search.search import Search
from app.src.util.configurations import get_app_root


def main():
    app = FastAPI()

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Ensure the database is built
    zip_path = get_app_root() / "input_data" / "raw_input_data.zip"
    database_path = get_app_root() / "database"

    build_database(input_zip_path=zip_path, database_path=database_path)
    search_client = Search(
        pl.read_parquet(
            database_path / "medallions" / "gold.parquet"
        )
    )

    # API Routes
    @app.get("/ping")
    def ping():
        return {"ok": True}

    @app.get("/documents/{file_path:path}")
    def download_document(file_path: str):
        return download_document_impl(file_path, database_path)

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest):
        return chat_impl(request, search_client, database_path)

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=5174)


if __name__ == "__main__":
    main()
