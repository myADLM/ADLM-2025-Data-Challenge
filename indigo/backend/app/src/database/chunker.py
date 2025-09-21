import shutil
import chonkie
from chonkie import SentenceChunker
from app.src.util.read_documents import read_documents_as_plaintext
from app.src.util.bedrock import query_model
from typing import List, Tuple, Dict
import re
from pathlib import Path
from tqdm import tqdm
import polars as pl
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os


def fast_chunk_text(
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
    lock = threading.Lock()
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

        # Ensure the whole document is in the document store
        with lock:
            document_store[record[file_path_column]] = record[text_column]

        for idx, ch in enumerate(chunks):
            out = {k: v for k, v in record.items()}
            out["chunk_index"] = idx
            out["chunk_text"] = ch
            try:
                out["annotations"] = chunk_annotations(
                    ch,
                    record[file_path_column],
                    path_annotation_config,
                    lock,
                    document_store,
                )
            except Exception as e:
                print(f"Error annotating chunk: {e}")
                out["annotations"] = ""
            results.append(out)
        return results

    # Multithread processing of rows
    max_workers = min(32, (os.cpu_count() or 4))
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

    # Build output DataFrame; ensure consistent column order
    if not output_rows:
        return pl.DataFrame(
            {
                **{k: [] for k in df.columns if k != text_column},
                "chunk_index": [],
                "chunk_text": [],
            }
        )

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


def chunk_annotations(
    chunk: str,
    file_path: str,
    file_path_annotation_config: Dict[str, str],
    lock: threading.Lock,
    document_store: dict[str, str],
) -> str:
    """
    Annotate chunks based on their file path using regex patterns.

    - chunk: chunk text
    - file_path: file path of the original file
    - file_path_annotation_config: mapping of regex pattern -> annotation text (string only)
    - lock: lock for the document store
    - document_store: store of whole documents

    Returns the annotated chunk text
    """
    contextual = ""  # TODO: Uncomment this when the LLM is available
    # contextual = contextual_annotations(chunk, file_path, lock, document_store)
    annotations = []
    for pattern, annotation_text in file_path_annotation_config.items():
        if re.search(pattern, file_path):
            annotations.append(annotation_text)
    return "{}\n\n{}".format("\n".join(annotations), contextual)


def contextual_annotations(
    chunk: str, file_path: str, lock: threading.Lock, document_store: dict[str, str]
) -> str:
    """
    Get contextual information about a chunk and its place in a file.

    - chunk: chunk text
    - file_path: file path of the original file
    - lock: lock for the document store
    - document_store: store of whole documents

    Returns the contextualized chunk text
    """
    with lock:
        whole_document = document_store.get(file_path, None)
    if whole_document is None:
        raise ValueError(f"Whole document not found for file path: {file_path}")
    return query_model(
        "",
        """
    <document>
    {whole_document}
    </document>
    Here is the chunk we want to situate within the whole document
    <chunk>
    {chunk}
    </chunk>
    Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else.
    """.format(
            whole_document=whole_document, chunk=chunk
        ),
    )
