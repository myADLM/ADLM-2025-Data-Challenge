"""
FastAPI application for the document search and chat system.

This module sets up the FastAPI server with CORS middleware, builds the database,
loads embeddings and chunk data, and defines the API endpoints for document
download and chat functionality.
"""

import gc
import logging
import os
import sys

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
    """Initialize and run the FastAPI application."""
    # Setup logging
    logger = logging.getLogger("app")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Create FastAPI app
    app = FastAPI()

    # Add CORS middleware - allow both local and Docker environments
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Local development
            "http://127.0.0.1:5173",  # Alternative localhost
            "http://frontend:5173",  # Docker frontend service
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Build database from input data
    zip_path = get_app_root() / "input_data" / "raw_input_data.zip"
    database_path = get_app_root() / "database"
    build_database(input_zip_path=zip_path, database_path=database_path)

    # Load data with memory optimization
    logger.info("Loading parquet data with lazy evaluation...")
    lazy_df = pl.scan_parquet(database_path / "medallions" / "gold.parquet")

    # Extract embeddings (memory intensive operation)
    logger.info("Converting embeddings to numpy array...")
    embeddings = (
        lazy_df.select(
            pl.col("embedding").cast(pl.Array(pl.Float32, 3072)).alias("emb")
        )
        .collect()
        .to_series()
    ).to_numpy()

    # Load chunk data without embeddings
    logger.info("Loading chunk data...")
    chunk_df = lazy_df.drop("embedding").collect()
    gc.collect()  # Force garbage collection

    # Initialize search client
    search_client = Search(chunk_df, embeddings)

    # API endpoints
    @app.get("/ping")
    def ping():
        """Health check endpoint."""
        return {"ok": True}

    @app.get("/api/status")
    def get_api_status():
        """Check if OPENAI_API_KEY is available and what features are enabled."""
        openai_available = bool(os.environ.get("OPENAI_API_KEY"))

        return {
            "openai_available": openai_available,
            "features": {
                "gpt_models": openai_available,
                "vector_search": openai_available,
                "rank_fusion": openai_available,
                "bm25": True,  # BM25 doesn't require OpenAI
            },
        }

    @app.get("/documents/{file_path:path}")
    def download_document(file_path: str):
        """Download a document by file path."""
        return download_document_impl(file_path, database_path)

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest):
        """Process chat request with document search."""
        return chat_impl(request, search_client, database_path)

    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=5174)


if __name__ == "__main__":
    main()
