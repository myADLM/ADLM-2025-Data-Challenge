import subprocess
from app.src.util.read_documents import extract_zip
from pathlib import Path
from app.src.util.s3 import upload_files_to_s3, bucket_exists
from app.src.database.etl import bronze_database, silver_database, gold_database
from app.src.util.download_data import download_labdocs_zip


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
    if force_rebuild or not (pdfs_dir.exists() and any(f for f in pdfs_dir.iterdir())):
        # Ensure the input zip file exists
        if not input_zip_path.exists():
            download_labdocs_zip(input_zip_path)
        else:
            print("Input zip already exists. Skipping download...")

        extract_zip(input_zip_path, pdfs_dir, force_rebuild)
    else:
        print("Pdfs are already extracted. Skipping extraction step...")

    # Upload the PDFs to S3
    if force_rebuild or not bucket_exists(bucket_name):
        upload_files_to_s3(pdfs_dir, bucket_name, "originals/", force_rebuild)
    else:
        print("S3 bucket already exists. Skipping upload...")

    # Extract the text from the PDFs and store it in a parquet file
    # Expect columns: file_path, content
    if force_rebuild or not bronze_path.exists():
        bronze_database(pdfs_dir, bronze_path)
    else:
        print("Bronze database already exists. Skipping construction...")

    # Chunk the text and store it in a parquet file. Add context to the chunks.
    # Expect columns: idx, file_path, chunk_index, file_path_annotations, contextual_annotations, chunk_text
    if force_rebuild or not silver_path.exists():
        silver_database(bronze_path, silver_path)
    else:
        print("Silver database already exists. Skipping construction...")

    # Take fully processed data, add vectors, and store it in a parquet file.
    # Expect columns: idx, file_path, content, chunk_index, annotations, chunk_text, vector
    if force_rebuild or not gold_path.exists():
        # gold_database(silver_path, gold_path)
        pass
    else:
        print("Gold database already exists. Skipping construction...")

    # Done!
