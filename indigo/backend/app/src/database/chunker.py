import shutil
import chonkie
from chonkie import SentenceChunker
from app.src.util.read_documents import read_documents_as_plaintext
from app.src.util.configurations import get_app_root
from app.src.util.bedrock import query_model
from typing import List, Dict
import re
from pathlib import Path
from tqdm import tqdm
import polars as pl
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os


def chunk_text(
    df: pl.DataFrame,
    text_column: str,
    file_path_column: str,
    path_annotation_config: Dict[str, str],
) -> pl.DataFrame:
    """
    Chunk the text in `text_column` into ~500-token chunks with no overlap.

    Uses `SentenceChunker` for sentence-aware chunking and `ThreadPoolExecutor`
    to parallelize across rows.

    Returns a new DataFrame with rows expanded per chunk and columns:
      - all original columns (except `text_column` may be dropped in output)
      - `chunk_index`: zero-based index of the chunk for that row
      - `chunk_text`: text content of the chunk
      - `file_path_column`: file path of the original file
      - `path_annotation_config`: configuration for path-based annotations
    """
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in DataFrame")

    # Prepare rows as list of dict for thread-safe processing
    records = df.to_dicts()
    document_store = {}

    def process_record(record: dict) -> list[dict]:
        # Initialize chunker. Target approximately 500 tokens, no overlap
        chunker = SentenceChunker(
            chunk_size=2048,
            chunk_overlap=0,
            min_sentences_per_chunk=1,
            min_characters_per_sentence=10,
        )

        text = record.get(text_column, "") or ""

        # Strip continuous strings of non-alphanumeric characters
        pat = re.compile(r"[\W^_]{5,}", flags=re.UNICODE)
        text = pat.sub(" ", text)

        # Fast path for empty text
        if not text.strip():
            return []

        chunks = normalize_chunks(chunker(text))
        results: list[dict] = []

        for idx, ch in enumerate(chunks):
            out = {
                "chunk_index": idx,
                "chunk_text": ch,
                "file_path_annotations": file_path_annotations(
                    record["file_path"],
                    path_annotation_config,
                ),
            }
            try:
                out["contextual_annotations"] = contextual_annotations(ch, idx, record)
            except Exception as e:
                print(f"Error annotating chunk: {e}")
                out["contextual_annotations"] = ""
            results.append(out)
        return results

    # Multithread processing of rows
    max_workers = min((os.cpu_count() or 1), 8)
    output_rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_record, rec) for rec in records]
        for f in tqdm(
            as_completed(futures), total=len(futures), desc="Chunking rows", unit="row"
        ):
            try:
                output_rows.extend(f.result())
            except Exception as e:
                # Skip problematic rows but continue processing
                print(f"Error processing row: {e}")
                continue

    if not output_rows:
        raise Exception("Failed to generate any output columns.")

    return pl.DataFrame(output_rows)


def normalize_chunks(chunks: List[chonkie.Chunk]) -> list[str]:
    """
    Normalize chunks by removing empty or junk chunks and converting to strings.

    - chunks: list of chunks

    Returns a list of strings
    """
    normalized_chunks = []
    for chunk in chunks:
        chunk_text = chunk.text.strip()
        if not chunk_text:
            continue
        if len(chunk_text) < 100 and normalized_chunks:
            normalized_chunks[-1] += chunk_text
            continue
        normalized_chunks.append(chunk_text)
    return normalized_chunks


def file_path_annotations(
    file_path: str,
    file_path_annotation_config: Dict[str, str],
) -> str:
    """
    Annotate chunks based on their file path using regex patterns.

    - file_path: file path of the original file
    - file_path_annotation_config: mapping of regex pattern -> annotation text (string only)

    Returns the annotated chunk text
    """
    annotations = []
    for pattern, annotation_text in file_path_annotation_config.items():
        if re.search(pattern, file_path):
            annotations.append(annotation_text)
    return "\n".join(annotations)


def contextual_annotations(ch: str, idx: int, record: dict) -> str:
    """
    Get contextual information about a chunk and its place in a file.

    - ch: chunk text
    - idx: chunk index
    - record: bronze medallion record

    Returns the contextualized chunk text
    """
    file_path = record["file_path"]
    whole_document = record["content"]

    # Check the cache
    cache_path = (
        get_app_root()
        / "database"
        / "context"
        / "query_cache"
        / "amazon_nova_lite"
        / Path(file_path).with_suffix("")
        / f"{idx}.txt"
    )
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        with open(cache_path, "r") as f:
            return f.read()

    if whole_document is None:
        raise ValueError(f"Whole document not found for file path: {file_path}")
    result = query_model(
        "",
        f"""
    <document>
    {whole_document}
    </document>
    Here is the chunk we want to situate within the whole document
    <chunk>
    {ch}
    </chunk>
    Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else.
    """,
        model_id="amazon.nova-lite-v1:0",
    )
    with open(cache_path, "w") as f:
        f.write(result)
    return result
