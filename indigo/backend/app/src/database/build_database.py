import subprocess
from app.src.util.read_documents import extract_zip
from pathlib import Path
from app.src.util.s3 import upload_files_to_s3, bucket_exists
from app.src.database.etl import bronze_database, silver_database, gold_database


def build_database(
    input_zip_path: Path, database_path: Path, force_rebuild: bool = False
):
    """Build the database."""
    pdfs_dir = database_path / "originals"
    extract_zip(input_zip_path, pdfs_dir, force_rebuild)
    bucket_name = "adlm-data-challenge"

    if force_rebuild or not bucket_exists(bucket_name):
        upload_files_to_s3(pdfs_dir, bucket_name, "originals/", force_rebuild)

    bronze_path = database_path / "medallions" / "bronze.parquet"
    silver_path = database_path / "medallions" / "silver.parquet"
    gold_path = database_path / "medallions" / "gold.parquet"

    # Extract the text from the PDFs and store it in a parquet file
    if force_rebuild or not bronze_path.exists():
        # Expect columns: file_path, content
        bronze_database(pdfs_dir, bronze_path)

    # Chunk the text and store it in a parquet file. Add context to the chunks.
    if force_rebuild or not silver_path.exists():
        # Expect columns: idx, file_path, content, chunk_index, annotations, chunk_text
        silver_database(bronze_path, silver_path)

    # Take fully processed data, add vectors, and store it in a parquet file.
    if force_rebuild or not gold_path.exists():
        # Expect columns: idx, file_path, content, chunk_index, annotations, chunk_text, vector
        # gold_database(silver_path, gold_path)
        pass

    # Build the BM25 database
    # Store the gold database and BM25 database in S3
    # TODO: Implement
    # Done!
