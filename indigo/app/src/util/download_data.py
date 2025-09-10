import subprocess
from pathlib import Path
import shutil
import tempfile
from typing import Optional
from app.src.util.aws import get_s3_client, ensure_bucket

DOWNLOAD_URL = "https://zenodo.org/records/16328490/files/LabDocs.zip?download=1"


def check_system_requirements():
    """Check if required system tools (curl and unzip) are available."""
    required_tools = ["curl", "unzip"]
    missing_tools = []

    for tool in required_tools:
        if shutil.which(tool) is None:
            missing_tools.append(tool)

    if missing_tools:
        print(
            f"Error: Required system tools not found: \
                {', '.join(missing_tools)}"
        )
        print("Please install the missing tools and try again.")
        return False

    return True


def download_labdocs_zip(
    output_path: Path | str, download_url: str = DOWNLOAD_URL
) -> bool:
    """
    Download the LabDocs.zip from Zenodo and write the zip to output_path.

    Args:
        output_path: file path to save the LabDocs.zip to.
        download_url: URL to download the LabDocs zip from.

    Returns:
        True on success, False otherwise.
    """
    # Check system requirements first (curl is required; unzip isn't used but we keep the same check)
    if not check_system_requirements():
        return False

    dest_zip = Path(output_path)
    dest_zip.mkdir(parents=True, exist_ok=True)

    try:
        # If destination already exists, prompt the user before overwriting
        if dest_zip.exists():
            response = (
                input(f"{dest_zip} already exists. Overwrite? [y/N]: ").strip().lower()
            )
            if response not in ("y", "yes"):
                print("Keeping existing file; skipping download.")
                return True

        result = subprocess.run(
            [
                "curl",
                "-L",
                "-C",
                "-",
                "--progress-bar",
                "-S",
                "-o",
                str(dest_zip),
                download_url,
            ],
            check=True,
        )
        if result.returncode != 0:
            print("Error downloading LabDocs.zip")
            return False

        if not dest_zip.exists() or dest_zip.stat().st_size == 0:
            print("Downloaded zip file is missing or empty.")
            return False

        print(f"Saved LabDocs.zip to {dest_zip} (size={dest_zip.stat().st_size} bytes)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during download: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
