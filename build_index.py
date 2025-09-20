import os
import json
from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader
from tqdm import tqdm
from rank_bm25 import BM25Okapi
import pickle
import re

RAW_DIR = Path("data_raw")
OCR_DIR = Path("data_ocr_done")
INDEX_DIR = Path("index")
INDEX_DIR.mkdir(parents=True, exist_ok=True)

META_PATH = INDEX_DIR / "meta.jsonl"
BM25_PATH = INDEX_DIR / "bm25.pkl"

WORD_RE = re.compile(r"[A-Za-z0-9_]+")

def choose_pdf(original: Path) -> Path:
    ocr_candidate = OCR_DIR / original.name
    if ocr_candidate.exists() and ocr_candidate.stat().st_size > 1024:
        return ocr_candidate
    return original

def extract_pages(pdf_path: Path) -> List[str]:
    pages = []
    try:
        reader = PdfReader(str(pdf_path))
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = text.replace("\x00", " ").strip()
            pages.append(text)
    except Exception as e:
        print(f"[WARN] Failed reading {pdf_path.name}: {e}")
    return pages

def tokenize(text: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(text)]

def main():
    pdfs = sorted([p for p in RAW_DIR.glob("**/*.pdf") if p.is_file()])
    if not pdfs:
        print(f"No PDFs in {RAW_DIR.resolve()}")
        return

    # Clear meta file (rebuild fresh)
    if META_PATH.exists():
        META_PATH.unlink()

    all_docs_tokens: List[List[str]] = []
    meta_records: List[Dict] = []

    with open(META_PATH, "a", encoding="utf-8") as meta_out:
        for src_pdf in tqdm(pdfs, desc="Indexing PDFs"):
            chosen = choose_pdf(src_pdf)
            pages = extract_pages(chosen)
            for page_idx, page_text in enumerate(pages, start=1):
                if not page_text.strip():
                    continue
                record = {
                    "file": src_pdf.name,     # always cite the original filename
                    "page": page_idx,
                    "text": page_text
                }
                meta_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                meta_records.append(record)
                all_docs_tokens.append(tokenize(page_text))

    # Build BM25
    bm25 = BM25Okapi(all_docs_tokens)
    with open(BM25_PATH, "wb") as f:
        pickle.dump({
            "bm25": bm25,
            "doc_count": len(all_docs_tokens),
        }, f)
    print(f"Index built.\n  Meta: {META_PATH}\n  BM25: {BM25_PATH}\n  Docs: {len(all_docs_tokens)}")

if __name__ == "__main__":
    main()
