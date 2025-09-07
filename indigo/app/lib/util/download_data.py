import subprocess
from pathlib import Path
import shutil
import tempfile

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


def download_labdocs(output_dir: Path | str):
    """
    Download and extract the LabDocs directory from Zenodo.

    Args:
        output_dir: Directory to extract LabDocs to.
    """
    # Check system requirements first
    if not check_system_requirements():
        return False

    # Convert to Path object
    output_dir = Path(output_dir)
    print(output_dir)

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading LabDocs to {output_dir}...")

    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_file = temp_path / "LabDocs.zip"

        try:
            # Download the file with curl (resume capability)
            print("Downloading LabDocs.zip (this may take a while)...")
            result = subprocess.run(
                ["curl", "-L", "-C", "-", "-sS", "-o", str(zip_file), DOWNLOAD_URL],
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

            # Extract the zip file to temporary directory
            print("Extracting LabDocs.zip to temporary directory...")
            result = subprocess.run(
                ["unzip", "-o", str(zip_file), "-d", str(temp_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            if result.returncode != 0:
                print(f"Error extracting file: {result.stderr}")
                return False

            # Discover the extracted root directory dynamically
            candidates = [p for p in temp_path.iterdir() if p.is_dir()]

            # Prefer a folder that looks like "LabDocs*"; otherwise fall back to single dir
            extracted_labdocs = None
            for p in candidates:
                if p.name.lower().startswith("labdocs"):
                    extracted_labdocs = p
                    break
            if extracted_labdocs is None and len(candidates) == 1:
                extracted_labdocs = candidates[0]

            if extracted_labdocs is None:
                print("Error: Could not determine extracted LabDocs directory.")
                return False

            # Move all contents from LabDocs to output_dir
            print(f"Moving contents from {extracted_labdocs} to {output_dir}...")
            for item in extracted_labdocs.iterdir():
                dest_path = output_dir / item.name
                if item.is_dir():
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.move(str(item), str(dest_path))
                else:
                    if dest_path.exists():
                        dest_path.unlink()
                    shutil.move(str(item), str(dest_path))

            print("LabDocs contents successfully moved to output directory.")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error during download/extraction: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
