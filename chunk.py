import os
import csv
import pdfplumber

# Config
pdf_folder = "LabDocs/Synthetic_Procedures"
output_csv = "lab_chunks.csv"
chunk_size = 500  # words per chunk

def extract_chunks_from_pdf(file_path, chunk_size=500):
    filename = os.path.basename(file_path)
    chunks = []
    with pdfplumber.open(file_path) as pdf:
        full_text = ""
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                full_text += f"\n\n[PAGE {page_num}]\n{text}"

        words = full_text.split()
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "filename": filename,
                "chunk_id": i // chunk_size,
                "text": chunk_text
            })
    return chunks

# Collect all chunks from all PDFs
all_chunks = []
for fname in os.listdir(pdf_folder):
    if fname.lower().endswith(".pdf"):
        full_path = os.path.join(pdf_folder, fname)
        try:
            chunks = extract_chunks_from_pdf(full_path, chunk_size)
            all_chunks.extend(chunks)
            print(f"✓ Processed {fname}")
        except Exception as e:
            print(f"✗ Failed to process {fname}: {e}")

# Save to CSV
with open(output_csv, mode="w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["filename", "chunk_id", "text"])
    writer.writeheader()
    for chunk in all_chunks:
        writer.writerow(chunk)

print(f"\n✅ Done. Saved {len(all_chunks)} chunks to {output_csv}")