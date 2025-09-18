from pathlib import Path
from typing import List, Optional
from tqdm import tqdm
from botocore.exceptions import ClientError
from app.src.util.aws import ensure_bucket, get_s3_client


def upload_files_to_s3(
    files_base_dir: Path | str,
    bucket_name: str,
    key_prefix: str,
    force_rebuild: bool = False,
) -> bool:
    """
    Upload all files from a directory to S3, maintaining the directory structure.

    This function recursively finds all files in the specified directory and uploads
    them to S3 with the same relative path structure. Only files (not directories)
    are uploaded.

    Args:
        files_base_dir: Base directory containing files to upload.
        bucket_name: Target S3 bucket name.
        key_prefix: S3 key prefix to prepend to all uploaded files (e.g., "data/processed/").
        force_rebuild: Whether to force rebuild the S3 bucket.

    Returns:
        True if all files uploaded successfully, False otherwise.

    Example:
        >>> upload_files_to_s3(
        ...     files_base_dir="/path/to/data",
        ...     bucket_name="my-bucket",
        ...     key_prefix="processed/",
        ... )
    """
    files_base_dir = Path(files_base_dir)
    ensure_bucket(bucket_name)

    # If force_rebuild is True, delete all objects in the bucket with the key_prefix
    s3_client = get_s3_client()
    if force_rebuild:
        print(f"Deleting all objects in s3://{bucket_name}/{key_prefix}")
        s3_client.delete_objects(
            Bucket=bucket_name, Delete={"Objects": [{"Key": f"{key_prefix}*"}]}
        )

    if not files_base_dir.exists():
        print(f"Error: Directory does not exist: {files_base_dir}")
        return False

    if not files_base_dir.is_dir():
        print(f"Error: Path is not a directory: {files_base_dir}")
        return False

    # Find all files recursively
    all_files = [f for f in files_base_dir.rglob("*") if f.is_file()]

    print("Checking for existing files in S3...")

    if not all_files:
        print(f"No files found in {files_base_dir}.")
        return True

    # Find the files that are not already in S3
    files_to_upload = []
    for file_path in all_files:
        s3_key = f"{key_prefix}{file_path.relative_to(files_base_dir)}".replace(
            "\\", "/"
        )
        files_to_upload.append((file_path, s3_key))

    print(
        f"Found {len(files_to_upload)} files to upload to s3://{bucket_name}/{key_prefix}"
    )

    # Upload each file with TQDM progress bar
    success_count = 0
    failed_files = []

    with tqdm(files_to_upload, desc="Uploading files", unit="file") as pbar:
        for file_path, s3_key in pbar:
            # Calculate the relative path from the base directory
            relative_path = file_path.relative_to(files_base_dir)

            # Update progress bar description with current file
            pbar.set_description(f"Uploading: {file_path.name[:20].ljust(20)}")

            if upload_file_to_s3(file_path, bucket_name, s3_key):
                success_count += 1
            else:
                failed_files.append(file_path)
                pbar.set_postfix_str(f"Failed: {file_path.name}")

    # Print summary
    if failed_files:
        print(f"\nFailed to upload {len(failed_files)} files:")
        for failed_file in failed_files:
            print(f"  - {failed_file}")

    print(
        f"Upload complete: {success_count}/{len(all_files)} files uploaded successfully"
    )
    return success_count == len(all_files)


def upload_file_to_s3(file_path: Path | str, bucket_name: str, object_key: str) -> bool:
    """
    Upload a single file to S3.

    This function uploads a file to the specified S3 bucket with the given object key.
    It can optionally skip uploads if the object already exists.

    Args:
        file_path: Path to the file to upload.
        bucket_name: Target S3 bucket name.
        object_key: S3 object key to store the file under (e.g., "data/file.pdf").

    Returns:
        True on success, False otherwise.

    Example:
        >>> upload_file_to_s3(
        ...     file_path="/path/to/document.pdf",
        ...     bucket_name="my-bucket",
        ...     object_key="documents/document.pdf"
        ... )
    """
    try:
        # Ensure the bucket exists
        ensure_bucket(bucket_name)
        s3_client = get_s3_client()
        s3_client.head_bucket(Bucket=bucket_name)

        # Validate file exists and is not empty
        if not file_path.exists():
            print(f"Error: File does not exist: {file_path}")
            return False

        if not file_path.is_file():
            print(f"Error: Path is not a file: {file_path}")
            return False

        if file_path.stat().st_size == 0:
            print(f"Warning: File is empty: {file_path}")
            return False

        # Upload the file
        s3_client.upload_file(
            Filename=str(file_path), Bucket=bucket_name, Key=object_key
        )

        return True

    except Exception as e:
        print(f"Failed to upload file {file_path}: {e}")
        return False


def download_file_from_s3(bucket_name: str, object_key: str) -> bool:
    s3_client = get_s3_client()
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "NoSuchKey":
            raise FileNotFoundError(f"s3://{bucket_name}/{object_key} not found") from e
        raise
    return obj["Body"].read()


def bucket_exists(bucket_name):
    try:
        get_s3_client().head_bucket(Bucket=bucket_name)
        return True
    except Exception:
        return False
