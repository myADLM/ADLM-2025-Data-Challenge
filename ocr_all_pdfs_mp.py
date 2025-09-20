import os
import sys
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
import subprocess
from pathlib import Path

RAW_DIR = Path("data_raw")
OUT_DIR = Path("data_ocr_done")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def has_ghostscript() -> bool:
    # ocrmypdf will call Ghostscript; quick probe
    try:
        # gswin64c on most x64 Windows; fall back to gs
        for exe in ("gswin64c", "gs"):
            proc = subprocess.run([exe, "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode == 0 or b"Ghostscript" in proc.stderr + proc.stdout:
                return True
    except FileNotFoundError:
        pass
    return False

def needs_ocr(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return True
    # If output older than source, re-OCR
    return dst.stat().st_mtime < src.stat().st_mtime

def ocr_one(src: Path) -> tuple[str, bool, str]:
    """
    Returns (filename, success_bool, message)
    """
    dst = OUT_DIR / src.name
    if not needs_ocr(src, dst):
        return (src.name, True, "already OCR’d")

    if not has_ghostscript():
        return (src.name, False, "Ghostscript not found; skipping OCR (will still index source PDF).")

    # Run ocrmypdf with safe defaults
    cmd = [
        "ocrmypdf",
        "--skip-text",
        "--rotate-pages",
        "--deskew",
        "-l", "eng",
        str(src),
        str(dst),
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if proc.returncode == 0:
            return (src.name, True, "OCR OK")
        else:
            # If it fails, ensure no partial output blocks later runs
            if dst.exists() and dst.stat().st_size < 1024:
                try:
                    dst.unlink()
                except Exception:
                    pass
            return (src.name, False, f"OCR failed: {proc.stdout[:4000]}")
    except Exception as e:
        return (src.name, False, f"Exception: {e}")

def main():
    pdfs = sorted([p for p in RAW_DIR.glob("**/*.pdf") if p.is_file()])
    if not pdfs:
        print(f"No PDFs found in: {RAW_DIR.resolve()}")
        sys.exit(0)

    print(f"Found {len(pdfs)} PDFs. Starting OCR into {OUT_DIR.resolve()} ...")
    results = []
    with ProcessPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
        futs = [ex.submit(ocr_one, p) for p in pdfs]
        for fut in as_completed(futs):
            results.append(fut.result())
            fn, ok, msg = results[-1]
            print(("[OK] " if ok else "[SKIP] " if "skipping" in msg.lower() else "[ERR] ") + f"{fn} — {msg}")

    oks = sum(1 for _, ok, _ in results if ok)
    errs = sum(1 for _, ok, _ in results if not ok and "skipping" not in results[0][2].lower())
    print(f"\nDone. {oks} OK, {errs} errors. (Skipped are fine; originals will be indexed.)")

if __name__ == "__main__":
    main()
