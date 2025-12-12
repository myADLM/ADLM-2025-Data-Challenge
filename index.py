# index.py — robust chunker (bigger chunks + overlap) and FAISS index builder
# Usage:
#   python index.py --data_dir .\data_ocr --index_dir .\index
#   (or use .\data_raw if you didn’t OCR yet)

import argparse, json, pathlib, re
import numpy as np
from tqdm import tqdm

import fitz            # PyMuPDF
import faiss           # faiss-cpu
from sentence_transformers import SentenceTransformer

# -------- text cleaning & chunking --------
def clean_text(s: str) -> str:
    if not s:
        return ""
    # normalize bullets and whitespace
    s = s.replace("\u2022", "*").replace("\uf0b7", "*")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def chunk_page(text: str, chunk_size: int = 1200, overlap: int = 200):
    words = text.split()
    if not words:
        return []
    out, i = [], 0
    while i < len(words):
        out.append(" ".join(words[i:i + chunk_size]))
        if i + chunk_size >= len(words):
            break
        i += max(1, chunk_size - overlap)
    return out

def pdf_to_chunks(pdf_path: str, chunk_size: int, overlap: int):
    doc = fitz.open(pdf_path)
    try:
        for pno in range(len(doc)):
            page = doc[pno]
            text = clean_text(page.get_text("text"))
            if not text:
                continue  # likely scanned page without OCR
            for chunk in chunk_page(text, chunk_size, overlap):
                yield (pno + 1, chunk)
    finally:
        doc.close()

# -------- index builder --------
def build_index(data_dir: pathlib.Path, index_dir: pathlib.Path,
                chunk_size: int = 1200, overlap: int = 200, batch: int = 512):
    index_dir.mkdir(parents=True, exist_ok=True)
    meta_path  = index_dir / "meta.jsonl"
    faiss_path = index_dir / "faiss.index"

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    vectors = []
    metas   = []
    pdfs = sorted(data_dir.rglob("*.pdf"))

    if not pdfs:
        print(f"No PDFs found in {data_dir}.")
        return

    print(f"Scanning {len(pdfs)} PDF(s) from {data_dir} ...")
    for pdf in tqdm(pdfs):
        for page_num, text in pdf_to_chunks(str(pdf), chunk_size, overlap):
            metas.append({"file": pdf.name, "page": page_num, "text": text})

    if not metas:
        print("No extractable text found. Are your PDFs OCR’d?")
        return

    # Embed in batches
    print(f"Embedding {len(metas)} chunks (batch={batch}) ...")
    for i in tqdm(range(0, len(metas), batch)):
        batch_texts = [m["text"] for m in metas[i:i + batch]]
        embs = model.encode(batch_texts, normalize_embeddings=True)
        vectors.append(np.asarray(embs, dtype=np.float32))

    xb = np.vstack(vectors).astype(np.float32)
    index = faiss.IndexFlatIP(xb.shape[1])  # cosine via normalized IP
    index.add(xb)
    faiss.write_index(index, str(faiss_path))

    with open(meta_path, "w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    files_count = len({m["file"] for m in metas})
    print(f"Indexed {len(metas)} chunks from {files_count} file(s).")
    print(f"Wrote: {faiss_path} and {meta_path}")

# -------- CLI --------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", required=True, help="Folder with PDFs (e.g., .\\data_ocr)")
    ap.add_argument("--index_dir", required=True, help="Output folder for index files (e.g., .\\index)")
    ap.add_argument("--chunk_size", type=int, default=1200)
    ap.add_argument("--overlap", type=int, default=200)
    ap.add_argument("--batch", type=int, default=512, help="Embedding batch size")
    args = ap.parse_args()

    build_index(pathlib.Path(args.data_dir), pathlib.Path(args.index_dir),
                chunk_size=args.chunk_size, overlap=args.overlap, batch=args.batch)
