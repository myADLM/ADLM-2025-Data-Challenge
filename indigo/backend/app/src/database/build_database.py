import logging
from pathlib import Path
import requests, os

from app.src.database.etl import (bronze_database, gold_database,
                                  silver_database)
from app.src.util.download_data import download_labdocs_zip
from app.src.util.read_documents import extract_zip
from app.src.util.s3 import bucket_exists, upload_files_to_s3

logger = logging.getLogger("app")


def build_database(
    input_zip_path: Path, database_path: Path, force_rebuild: bool = False
):
    """Build the database."""
    pdfs_dir = database_path / "originals"
    bucket_name = "adlm-data-challenge"
    bronze_path = database_path / "medallions" / "bronze.parquet"
    silver_path = database_path / "medallions" / "silver.parquet"
    gold_path = database_path / "medallions" / "gold.parquet"

    # Ensure the database path exists
    database_path.mkdir(parents=True, exist_ok=True)

    # Prepare the PDFs
    if force_rebuild or not pdfs_dir.exists():
        logger.info(f"No pdfs found at {pdfs_dir}. Downloading and extracting...")
        logger.info("Extracting PDFs...")
        # Ensure the input zip file exists
        if not input_zip_path.exists():
            if not download_labdocs_zip(input_zip_path):
                raise RuntimeError(f"Failed to download input zip to {input_zip_path}")
        else:
            logger.info("Input zip already exists. Skipping download...")

        if not extract_zip(input_zip_path, pdfs_dir, force_rebuild):
            raise RuntimeError(f"Failed to extract {input_zip_path} to {pdfs_dir}")
    else:
        logger.info("Pdfs are already extracted. Skipping extraction step...")

    # Upload the PDFs to S3
    if force_rebuild or not bucket_exists(bucket_name):
        upload_files_to_s3(pdfs_dir, bucket_name, "originals/", force_rebuild)
    else:
        logger.info("S3 bucket already exists. Skipping upload...")

    df_exists = lambda p: p.exists() and p.stat().st_size > 0
    # Check the github release files for a published the gold database
    if not force_rebuild and not df_exists(gold_path):
        gold_db_url = "https://github.com/jonmontg/ADLM-2025-Data-Challenge/releases/download/release-v1/gold.parquet"
        logger.info("Trying to retrieve gold database from release files...")
        try:
            head = requests.head(gold_db_url, allow_redirects=True, timeout=10)
            if head.status_code == 200:
                with requests.get(gold_db_url, stream=True, allow_redirects=True, timeout=240) as r:
                    r.raise_for_status()
                    with open(gold_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            if chunk:
                                f.write(chunk)
                logger.info("Gold database retrieved from release files.")
            else:
                logger.info("No gold database found.")
        except requests.RequestException as e:
            logger.info(f"An error occurred while retrieving the gold database: {e}")
            pass
                    

    # Extract the text from the PDFs and store it in a parquet file
    # Expect columns: file_path, content
    if force_rebuild or (not df_exists(bronze_path) and not df_exists(silver_path) and not df_exists(gold_path)):
        logger.info("Building bronze database...")
        bronze_database(pdfs_dir, bronze_path)
        logger.info("Bronze database built successfully.")
    else:
        logger.info("Bronze database already exists or is not required. Skipping construction...")

    # Chunk the text and store it in a parquet file. Add context to the chunks.
    # Expect columns: idx, file_path, chunk_index, file_path_annotations, contextual_annotations, chunk_text
    if force_rebuild or (not df_exists(silver_path) and not df_exists(gold_path)):
        logger.info("Building silver database...")
        silver_database(bronze_path, silver_path)
        logger.info("Silver database built successfully.")
    else:
        logger.info("Silver database already exists or is not required. Skipping construction...")

    # Take fully processed data, add vectors, and store it in a parquet file.
    # Expect columns: idx, file_path, chunk_index, file_path_annotations, contextual_annotations, chunk_text, embedding
    if force_rebuild or not df_exists(gold_path):
        logger.info("Building gold database...")
        gold_database(silver_path, gold_path)
        logger.info("Gold database built successfully.")
    else:
        logger.info("Gold database already exists. Skipping construction...")

    # Done!
