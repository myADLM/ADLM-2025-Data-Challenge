import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import json

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def extract_text_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    return " ".join(cell.get_text(strip=True) for cell in soup.find_all(["td", "th"]))

def collect_chunks(base_dir, parse_type):
    chunks_with_meta = []
    for root, _, files in os.walk(base_dir):
        for fname in files:
            path = Path(root) / fname
            text = ""

            # Match your actual filenames
            if parse_type == "ocr" and fname.endswith(".jpg.txt"):
                text = path.read_text(encoding="utf-8").strip()
            elif parse_type == "tcr" and fname.endswith(".jpg.html"):
                text = extract_text_from_html(path).strip()
            else:
                continue

            if not text:
                continue

            # Derive doc_id and page from filename
            # Example: CACAO_COCOA_IGE_SERUM.pdf_0.jpg.txt
            base = fname.split(".jpg")[0]  # CACAO_COCOA_IGE_SERUM.pdf_0
            doc_id = base.split(".pdf")[0]  # CACAO_COCOA_IGE_SERUM
            page_match = re.search(r"_(\d+)$", base)
            page = int(page_match.group(1)) if page_match else None

            for i, chunk in enumerate(chunk_text(text)):
                chunks_with_meta.append({
                    "doc_id": doc_id,
                    "page": page,
                    "type": parse_type,
                    "chunk_id": i,
                    "text": chunk,
                    "source": str(path)
                })
    return chunks_with_meta

if __name__ == "__main__":
    ocr_chunks = collect_chunks("/Users/samiratiya/Desktop/Ragflow/OCR_parse", "ocr")
    tcr_chunks = collect_chunks("/Users/samiratiya/Desktop/Ragflow/TCR_parse", "tcr")

    all_chunks = ocr_chunks + tcr_chunks
    print(f"Collected {len(all_chunks)} chunks")

    out_path = Path("/Users/samiratiya/Desktop/Ragflow/ragflow_chunks.jsonl")
    with out_path.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"Chunks written to {out_path}")

