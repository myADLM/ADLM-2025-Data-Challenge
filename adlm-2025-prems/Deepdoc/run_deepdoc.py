#!/usr/bin/env python3
import subprocess
import os
import sys
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

# === Configuration ===
INPUT_DIR = "/Users/samiratiya/Desktop/Ragflow/LabDocs"
OCR_OUT = "/Users/samiratiya/Desktop/Ragflow/OCR_parse"
TSR_OUT = "/Users/samiratiya/Desktop/Ragflow/TCR_parse"
LAYOUT_OUT = "/Users/samiratiya/Desktop/Ragflow/Layout_parse"

BATCH_SIZE = 25
THRESHOLD = "0.2"

# === Utilities ===
def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def log(msg):
    print(msg, flush=True)

def has_expected_outputs(stage, out_dir: Path) -> bool:
    if stage == "ocr":
        return any(out_dir.glob("*.jpg.txt"))
    elif stage == "tsr":
        return any(out_dir.glob("*.jpg.html"))
    elif stage == "layout":
        return any(out_dir.glob("*.jpg"))
    return False

def safe_run(cmd):
    try:
        result = subprocess.run(cmd)
        return (result.returncode == 0, result.returncode)
    except Exception as e:
        log(f"  ⚠️ Subprocess error: {e}")
        return (False, -1)

def run_stage(stage, cmd, target_dir: Path, expected_suffix: str, fname: str, failures: list):
    """Run a DeepDoc stage into a temp dir, then move outputs into target_dir."""
    if has_expected_outputs(stage, target_dir):
        log(f"  ⏭️ {stage.upper()} already done: {fname}")
        return

    log(f"  -> {stage.upper()} {fname}")
    with tempfile.TemporaryDirectory() as tmpdir:
        ok, code = safe_run(cmd + ["--output_dir", tmpdir])
        # Move outputs into target_dir
        for out_file in Path(tmpdir).glob("*"):
            shutil.move(str(out_file), str(target_dir))

    if not ok or not has_expected_outputs(stage, target_dir):
        log(f"  ⚠️ {stage.upper()} failed on {fname} (exit {code})")
        failures.append(fname)

# === Main ===
def main():
    ensure_dirs(OCR_OUT, TSR_OUT, LAYOUT_OUT)

    # Collect PDFs recursively (case-insensitive)
    pdf_files = [str(p) for p in Path(INPUT_DIR).rglob("*.[pP][dD][fF]")]
    total = len(pdf_files)
    log(f"Discovered {total} PDF files under {INPUT_DIR}")
    if total == 0:
        return

    start_time = datetime.now()
    failed_ocr, failed_tsr, failed_layout = [], [], []

    try:
        for i in range(0, total, BATCH_SIZE):
            batch = pdf_files[i:i+BATCH_SIZE]
            batch_id = i // BATCH_SIZE + 1
            log(f"\n--- Processing batch {batch_id} ({len(batch)} files) ---")

            # Create per-batch output dirs
            ocr_dir = Path(OCR_OUT) / f"batch_{batch_id}"
            tsr_dir = Path(TSR_OUT) / f"batch_{batch_id}"
            layout_dir = Path(LAYOUT_OUT) / f"batch_{batch_id}"
            ocr_dir.mkdir(parents=True, exist_ok=True)
            tsr_dir.mkdir(parents=True, exist_ok=True)
            layout_dir.mkdir(parents=True, exist_ok=True)

            for f in batch:
                fname = os.path.basename(f)

                # OCR
                run_stage(
                    "ocr",
                    [sys.executable, "ragflow/deepdoc/vision/t_ocr.py", "--inputs", f],
                    ocr_dir,
                    ".jpg.txt",
                    fname,
                    failed_ocr,
                )

                # TSR
                run_stage(
                    "tsr",
                    [
                        sys.executable,
                        "ragflow/deepdoc/vision/t_recognizer.py",
                        "--inputs", f,
                        "--threshold", THRESHOLD,
                        "--mode", "tsr",
                    ],
                    tsr_dir,
                    ".jpg.html",
                    fname,
                    failed_tsr,
                )

                # Layout
                run_stage(
                    "layout",
                    [
                        sys.executable,
                        "ragflow/deepdoc/vision/t_recognizer.py",
                        "--inputs", f,
                        "--threshold", THRESHOLD,
                        "--mode", "layout",
                    ],
                    layout_dir,
                    ".jpg",
                    fname,
                    failed_layout,
                )

        duration = datetime.now() - start_time
        log(f"\n🎉 Done in {duration}.")

        if failed_ocr or failed_tsr or failed_layout:
            log("\nSummary of failures:")
            if failed_ocr: log(f"  OCR failures: {len(failed_ocr)}")
            if failed_tsr: log(f"  TSR failures: {len(failed_tsr)}")
            if failed_layout: log(f"  Layout failures: {len(failed_layout)}")
        else:
            log("✅ No failures recorded.")

    except KeyboardInterrupt:
        log("\n⏹️ Interrupted. Resume by rerunning — completed outputs will be skipped.")

if __name__ == "__main__":
    main()
