import re
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import json

# ==== CONFIG: fill these in ====
PROJECT_ID = ""
LOCATION = "us"

LAYOUT_PROCESSOR_ID = ""  # DocOCR

FORM_PROCESSOR_ID = ""


SERVICE_ACCOUNT_JSON = """"""
# ================================

from google.oauth2 import service_account
from google.cloud import documentai_v1 as documentai

# ---------- Helpers ----------
def text_from_anchor(doc: documentai.Document, anchor: documentai.Document.TextAnchor) -> str:
    """Primary extractor: use text_anchor indices into doc.text."""
    if not anchor or not anchor.text_segments:
        return ""
    parts = []
    for seg in anchor.text_segments:
        s = int(seg.start_index) if seg.start_index is not None else 0
        e = int(seg.end_index) if seg.end_index is not None else 0
        parts.append(doc.text[s:e])
    return "".join(parts).strip()

def bbox_mid_y(layout: documentai.Document.Page.Layout) -> float:
    if not layout.bounding_poly or not layout.bounding_poly.normalized_vertices:
        return layout.bounding_poly.vertices[0].y if layout.bounding_poly.vertices else 0.0
    vs = layout.bounding_poly.normalized_vertices
    return sum(v.y for v in vs) / max(1, len(vs))

def _within(norm_box, x, y) -> bool:
    """Point-in-rect for normalized bounding boxes (assumes axis-aligned)."""
    xs = [v.x for v in norm_box.normalized_vertices]
    ys = [v.y for v in norm_box.normalized_vertices]
    return (min(xs) - 1e-4) <= x <= (max(xs) + 1e-4) and (min(ys) - 1e-4) <= y <= (max(ys) + 1e-4)

def cell_text_robust(doc: documentai.Document, page_index: int, cell: documentai.Document.Page.Table.TableCell) -> str:
    """
    Robust cell text:
    1) Try text_anchor (normal case)
    2) Fallback: collect tokens on the same page whose centers fall inside the cell box.
    """
    # 1) normal path
    txt = text_from_anchor(doc, cell.layout.text_anchor)
    if txt:
        return txt

    # 2) fallback via tokens
    page = doc.pages[page_index]
    if not page.tokens or not cell.layout or not cell.layout.bounding_poly or not cell.layout.bounding_poly.normalized_vertices:
        return ""  # nothing we can do

    words: List[Tuple[float, float, str]] = []
    for tok in page.tokens:
        if not tok.layout or not tok.layout.bounding_poly or not tok.layout.bounding_poly.normalized_vertices:
            continue
        # token center
        vs = tok.layout.bounding_poly.normalized_vertices
        cx = sum(v.x for v in vs) / len(vs)
        cy = sum(v.y for v in vs) / len(vs)
        if _within(cell.layout.bounding_poly, cx, cy):
            w = text_from_anchor(doc, tok.layout.text_anchor)
            if w:
                words.append((cy, cx, w))

    if not words:
        return ""
    # sort by y, then x
    words.sort()
    # simple line join – you can make this fancier if needed
    out = []
    last_y = None
    for cy, cx, w in words:
        if last_y is not None and abs(cy - last_y) > 0.008:  # new line threshold
            out.append("\n")
        out.append(w)
        last_y = cy
    return " ".join(part for part in out if part != "\n").strip()

# ---------- Markdown emitters ----------
def table_to_markdown(doc: documentai.Document, table: documentai.Document.Page.Table, page_index: int) -> str:
    # headers
    headers: List[str] = []
    if table.header_rows:
        headers = [cell_text_robust(doc, page_index, c) for c in table.header_rows[0].cells]
        # merge multiple header rows if present
        for extra in table.header_rows[1:]:
            merged = [cell_text_robust(doc, page_index, c) for c in extra.cells]
            w = max(len(headers), len(merged))
            headers = [
                ((headers[i] if i < len(headers) else "") +
                 (" " if (i < len(headers) and i < len(merged) and headers[i] and merged[i]) else "") +
                 (merged[i] if i < len(merged) else "")).strip()
                for i in range(w)
            ]
    # body
    rows = []
    for r in table.body_rows:
        rows.append([cell_text_robust(doc, page_index, c) for c in r.cells])

    # Debug preview (helps if something is still empty)
    if rows:
        preview = " | ".join(rows[0][: min(5, len(rows[0]))])
        print(f"DEBUG table p{page_index+1}: rows={len(rows)} preview: {preview[:120]}")

    md = []
    if headers:
        md.append("| " + " | ".join(h if h.strip() else f"Col{i+1}" for i, h in enumerate(headers)) + " |")
        md.append("| " + " | ".join("---" for _ in headers) + " |")
    elif rows:
        cols = len(rows[0])
        md.append("| " + " | ".join(f"Col{i+1}" for i in range(cols)) + " |")
        md.append("| " + " | ".join("---" for _ in range(cols)) + " |")
    for r in rows:
        md.append("| " + " | ".join(r) + " |")
    return "\n".join(md) if md else "> *(Empty table)*"

LIST_BULLETS = r"^[\-\u2022\u2023\u25E6\u2043\u2219\*•●▪‣]+(\s+|$)"
LIST_NUMBERED = r"^((\d+|[A-Za-z]+)[\.\)]|\(\d+\)|\([A-Za-z]+\))\s+"

def lines_to_markdown_paragraphs(raw_text: str) -> str:
    lines = [ln.rstrip() for ln in raw_text.splitlines() if ln.strip()]
    out: List[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if re.match(LIST_BULLETS, ln):
            buf = []
            while i < len(lines) and re.match(LIST_BULLETS, lines[i]):
                item = re.sub(LIST_BULLETS, "", lines[i]).strip()
                buf.append(f"- {item}"); i += 1
            out.append("\n".join(buf)); continue
        if re.match(LIST_NUMBERED, ln):
            buf = []
            while i < len(lines) and re.match(LIST_NUMBERED, lines[i]):
                item = re.sub(LIST_NUMBERED, "", lines[i]).strip()
                buf.append(f"1. {item}"); i += 1
            out.append("\n".join(buf)); continue
        para = [ln]; i += 1
        while i < len(lines) and not lines[i].endswith((".", "?", "!", ":", ";")) and \
              not re.match(LIST_BULLETS, lines[i]) and not re.match(LIST_NUMBERED, lines[i]):
            para.append(lines[i]); i += 1
        out.append(" ".join(para))
    return "\n\n".join(out)

# ---------- Document AI ----------
def get_client():
    creds = service_account.Credentials.from_service_account_info(
        json.loads(SERVICE_ACCOUNT_JSON),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return documentai.DocumentProcessorServiceClient(credentials=creds)

def process_with_processor(client, processor_id: str, pdf_bytes: bytes) -> documentai.ProcessResponse:
    name = client.processor_path(PROJECT_ID, LOCATION, processor_id)
    return client.process_document(
        request=documentai.ProcessRequest(
            name=name,
            raw_document=documentai.RawDocument(content=pdf_bytes, mime_type="application/pdf"),
        )
    )

# ---------- Build Markdown (DocOCR text + Form tables interleaved) ----------
def build_markdown_with_form(
    layout_doc: documentai.Document,
    form_doc: Optional[documentai.Document] = None
) -> str:
    """
    Interleave DocOCR blocks with tables. Label tables clearly and make sure
    we extract cell text from the SAME source doc the table came from.
    """
    md_parts: List[str] = []

    for p_idx, lp in enumerate(layout_doc.pages, start=1):
        md_parts.append(f"# Page {p_idx}")

        items: List[Tuple[float, str, object, documentai.Document, str]] = []

        # DocOCR blocks (text)
        for b in lp.blocks:
            items.append((bbox_mid_y(b.layout), "block", b, layout_doc, "DocOCR"))

        # Prefer Form Parser tables
        form_tables = []
        if form_doc and (p_idx - 1) < len(form_doc.pages):
            form_tables = list(form_doc.pages[p_idx - 1].tables)

        if form_tables:
            for t in form_tables:
                items.append((bbox_mid_y(t.layout), "table", t, form_doc, "FormParser"))
        else:
            for t in lp.tables:
                items.append((bbox_mid_y(t.layout), "table", t, layout_doc, "DocOCR"))

        items.sort(key=lambda x: x[0])

        # Per-page table counter
        table_no = 0

        for _, kind, obj, src_doc, src_name in items:
            if kind == "table":
                table_no += 1
                md_parts.append("")  # ensure blank line before tables
                md_parts.append(f"## Table {table_no} (page {p_idx}, {src_name})")
                md_parts.append("")
                md_parts.append(table_to_markdown(src_doc, obj, page_index=p_idx-1))
                md_parts.append("")  # ensure blank line after tables
            else:
                txt = text_from_anchor(src_doc, obj.layout.text_anchor)
                if txt:
                    md_parts.append("")
                    md_parts.append(lines_to_markdown_paragraphs(txt))

        md_parts.append("")

    return "\n".join(p for p in md_parts if p.strip())

# ---------- Main driver ----------
def convert_pdf_to_markdown(pdf_path: str, output_md: str):
    client = get_client()
    pdf_bytes = Path(pdf_path).read_bytes()

    # DocOCR for layout
    layout_resp = process_with_processor(client, LAYOUT_PROCESSOR_ID, pdf_bytes)
    layout_doc = layout_resp.document
    print("LAYOUT (DocOCR)  -> pages:", len(layout_doc.pages))
    for i, p in enumerate(layout_doc.pages, 1):
        print(f"  page {i}: tables={len(p.tables)} blocks={len(p.blocks)} paragraphs={len(p.paragraphs)}")

    # Form Parser for tables (optional)
    form_doc = None
    if FORM_PROCESSOR_ID and FORM_PROCESSOR_ID.strip():
        form_resp = process_with_processor(client, FORM_PROCESSOR_ID, pdf_bytes)
        form_doc = form_resp.document
        print("FORM (FormParser)-> pages:", len(form_doc.pages))
        for i, p in enumerate(form_doc.pages, 1):
            print(f"  page {i}: tables={len(p.tables)}")

    # If no pages (edge case), emit text-only fallback
    if not layout_doc.pages:
        full_text = (layout_doc.text or "").strip()
        if full_text:
            Path(output_md).write_text(lines_to_markdown_paragraphs(full_text) + "\n", encoding="utf-8")
            print("No pages in response; wrote text-only Markdown fallback.")
            return
        raise RuntimeError("DocAI returned no pages and no text. Check processor IDs and region.")

    # Build Markdown with interleaved tables (uses robust cell extractor)
    md = build_markdown_with_form(layout_doc, form_doc)
    Path(output_md).write_text(md.strip() + "\n", encoding="utf-8")
    print(f"Wrote {Path(output_md).resolve()}")

def main():
    ap = argparse.ArgumentParser(description="Convert a PDF to Markdown (tables + lists) using Google Document AI.")
    ap.add_argument("pdf", help="Path to input PDF")
    ap.add_argument("-o", "--output", help="Output .md (default: <pdfname>.md)")
    args = ap.parse_args()

    in_pdf = Path(args.pdf)
    out_md = Path(args.output) if args.output else in_pdf.with_suffix(".md")
    convert_pdf_to_markdown(str(in_pdf), str(out_md))

if __name__ == "__main__":
    main()
