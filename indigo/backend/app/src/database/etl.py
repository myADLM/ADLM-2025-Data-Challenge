from pathlib import Path
from time import perf_counter

import numpy as np
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

from app.src.database.chunker import chunk_text
from app.src.util.configurations import get_app_root, load_config
from app.src.util.open_ai_api import OpenAIAPI
from app.src.util.read_documents import read_documents_as_plaintext
from app.src.util.s3 import get_s3_client


def bronze_database(pdfs_dir: Path, output_path: Path):
    # Extract the text from the PDFs and store it in a parquet file
    text_files = read_documents_as_plaintext(pdfs_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    schema = pa.schema([("file_path", pa.string()), ("content", pa.string())])
    paths, contents = zip(*text_files)
    table = pa.Table.from_arrays(
        [pa.array(paths, type=pa.string()), pa.array(contents, type=pa.string())],
        schema=schema,
    )
    pq.write_table(table, output_path)


def silver_database(bronze_path: Path, output_path: Path):
    # Chunk the text and store it in a parquet file.
    # Use LLM to add context to the chunks.
    # Use file path to add context to the chunks.
    df = pl.read_parquet(bronze_path)

    chunk_annotation_config = load_config("chunk_annotation_patterns.yml")
    # Chunk the text
    df = chunk_text(df, "content", chunk_annotation_config)
    df = df.with_row_index("idx")
    df.write_parquet(output_path)


def gold_database(silver_path: Path, output_path: Path):
    # Take fully processed data, add vectors, and store it in a parquet file.
    openai_client = OpenAIAPI()
    df = pl.read_parquet(silver_path)

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
                dtype=np.float32,
            ),
            return_dtype=pl.List(pl.Float32),
        ),
    )
    df.write_parquet(output_path)
