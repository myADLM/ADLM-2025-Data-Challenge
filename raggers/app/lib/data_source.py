import subprocess
from pathlib import Path
import shutil

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


def download_labdocs(output_dir: Path | str = None):
    """
    Download and extract the LabDocs directory from Zenodo if it doesn't exist.

    Args:
        output_dir: Directory to extract LabDocs to. If None, uses app/data/LabDocs.
    """
    # Check system requirements first
    if not check_system_requirements():
        return False

    # Determine output directory
    if output_dir is None:
        # Go up two levels from lib/ to app/, then into data/
        output_dir = Path(__file__).parent.parent / "data"
    else:
        output_dir = Path(output_dir)

    # Create data directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading LabDocs to {output_dir}...")

    # Define download URL and local paths
    zip_file = output_dir / "LabDocs.zip"

    try:
        # Download the file with curl (resume capability)
        print("Downloading LabDocs.zip...")
        result = subprocess.run(
            ["curl", "-L", "-C", "-", "-o", str(zip_file), DOWNLOAD_URL],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.returncode != 0:
            print(f"Error downloading file: {result.stderr}")
            return False

        # Check if download was successful
        if not zip_file.exists():
            print("Error: Download completed but file not found.")
            return False

        print(
            f"Download completed. File size: {zip_file.stat().st_size / (1024*1024):.1f} MB"
        )

        # Extract the zip file
        print("Extracting LabDocs.zip...")
        result = subprocess.run(
            ["unzip", "-o", str(zip_file), "-d", str(output_dir)],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.returncode != 0:
            print(f"Error extracting file: {result.stderr}")
            return False

        # Clean up the zip file
        zip_file.unlink()
        print("LabDocs.zip cleaned up.")

        # Verify extraction was successful
        if (output_dir / "LabDocs").exists():
            print("LabDocs directory successfully downloaded and extracted.")
            return True
        else:
            print("Error: Extraction completed but LabDocs directory not found.")
            return False

    except subprocess.CalledProcessError as e:
        print(f"Error during download/extraction: {e}")
        if zip_file.exists():
            zip_file.unlink()  # Clean up partial download
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        if zip_file.exists():
            zip_file.unlink()  # Clean up partial download
        return False
