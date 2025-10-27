"""
ETL (Extract, Transform, Load) functions for database processing.

This module implements the bronze, silver, and gold data processing pipeline
for the document search system.
"""

from pathlib import Path

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

from app.src.database.chunker import chunk_text
from app.src.util.configurations import get_app_root, load_config
from app.src.util.open_ai_api import EmbeddingsAPI
from app.src.util.read_documents import read_documents_as_plaintext


def bronze_database(pdfs_dir: Path, output_path: Path):
    """
    Extract text from PDFs and store in parquet format.
    Bronze Columns:
    - file_path[str]
    - content[str]
    """
    text_files = read_documents_as_plaintext(pdfs_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create parquet table with file paths and extracted content
    schema = pa.schema([("file_path", pa.string()), ("content", pa.string())])
    paths, contents = zip(*text_files)
    table = pa.Table.from_arrays(
        [pa.array(paths, type=pa.string()), pa.array(contents, type=pa.string())],
        schema=schema,
    )
    pq.write_table(table, output_path)


def silver_database(bronze_path: Path, output_path: Path):
    """
    Chunk text and add contextual annotations using LLM.
    Silver Columns:
    - idx[int]
    - file_path[str]
    - chunk_index[int]
    - chunk_text[str]
    - file_path_annotations[str]
    - contextual_annotations[str]
    """
    df = pl.read_parquet(bronze_path)

    # Load chunking configuration and process text
    chunk_annotation_config = load_config("chunk_annotation_patterns.yml")
    df = chunk_text(df, "content", chunk_annotation_config)
    df = df.with_row_index("idx")
    df.write_parquet(output_path)


def gold_database(silver_path: Path, output_path: Path):
    """
    Add embeddings to processed chunks and create final database.
    Gold Columns:
    - idx[int]
    - file_path[str]
    - chunk_index[int]
    - chunk_text[str]
    - file_path_annotations[str]
    - contextual_annotations[str]
    - contextual_chunk[str]
    - embedding[list[f32]]
    """
    openai_client = EmbeddingsAPI()
    df = pl.read_parquet(silver_path)

    # Combine annotations and chunk text for embedding
    df = df.with_columns(
        contextual_chunk=pl.concat_str(
            [
                pl.col("file_path_annotations"),
                pl.col("contextual_annotations"),
                pl.col("chunk_text"),
            ],
            separator="\n\n",
            ignore_nulls=True,
        )
    )
    
    # Generate embeddings for each contextual chunk
    df = df.with_columns(
        embedding=pl.struct(
            ["contextual_chunk", "file_path", "chunk_index"]
        ).map_elements(
            lambda x: openai_client.embed_file(
                x["contextual_chunk"],
                cached=Path(get_app_root())
                / "database"
                / "embeddings"
                / "text-embedding-3-large"
                / x["file_path"][:-4]
                / f"{x['chunk_index']}.npy",
            ),
            return_dtype=pl.List(pl.Float32),
        ),
    )
    df.write_parquet(output_path)
