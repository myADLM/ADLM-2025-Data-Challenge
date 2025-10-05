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
    # Logging
    logger = logging.getLogger("app")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

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

    # Ensure the database is built
    zip_path = get_app_root() / "input_data" / "raw_input_data.zip"
    database_path = get_app_root() / "database"

    build_database(input_zip_path=zip_path, database_path=database_path)

    # Use lazy loading to process data in chunks and reduce memory footprint
    print("Loading parquet data with lazy evaluation...")
    lazy_df = pl.scan_parquet(database_path / "medallions" / "gold.parquet")

    # Extract embeddings first (most memory intensive)
    print("Converting embeddings to numpy array...")
    embeddings = (
        lazy_df.select(
            pl.col("embedding").cast(pl.Array(pl.Float32, 3072)).alias("emb")
        )
        .collect()
        .to_series()
    ).to_numpy()

    # Load chunk data without embeddings
    print("Loading chunk data...")
    chunk_df = lazy_df.drop("embedding").collect()
    gc.collect()  # Force garbage collection

    search_client = Search(chunk_df, embeddings)

    # API Routes
    @app.get("/ping")
    def ping():
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
        return download_document_impl(file_path, database_path)

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest):
        return chat_impl(request, search_client, database_path)

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=5174)


if __name__ == "__main__":
    main()
