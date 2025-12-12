import pymupdf4llm
from pathlib import Path
import re

def remove_strikethrough(md_text: str) -> str:
    """
    remove ~~...~~ markers but keep the text inside
    """
    return re.sub(r"~~(.*?)~~", r"\1", md_text, flags=re.DOTALL)

def clean_markdown_headers(text: str) -> str:
    """
    Convert ALL-CAPS lines to Markdown headers (always '##') and
    remove all formatting, numbering, bullets, roman numerals, and letters.
    Collapses multiple blank lines.
    """

    formatted_lines = []

    # Regex to strip leading numbers, letters, roman numerals, bullets, bold
    leading_strip = re.compile(
        r"^(?:\*\*|[0-9]+|[A-Z]|M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3} \d+\.(?=\n\n))[\.\)\-:]*\s*",
        re.I,
    )
    # remove inline bullets, numbering, bold, asterisks, and periods followed by 3+ spaces
    inline_strip = re.compile(
        r"(?:[\*\◦\•]+|\.{1,}(?=\s{3,})|\d+\.(?=\n{2,})|^\s*\d+\.\s*$)", re.M
    )

    for line in text.splitlines():
        stripped = line.strip()

        # Collapse multiple blank lines
        if not stripped:
            if formatted_lines and formatted_lines[-1] != "":
                formatted_lines.append("")
            continue

        # remove bold markup
        stripped = stripped.replace("**", "")

        # detect ALL-CAPS header (heuristic)
        if stripped.isupper() and len(stripped.split()) <= 12:
            # strip leading numbering/letters/bullets
            clean_header = leading_strip.sub("", stripped)
            formatted_lines.append("## " + clean_header)
        else:
            # remove inline bullets/numbers
            clean_line = inline_strip.sub("", stripped)
            formatted_lines.append(clean_line)

    return "\n".join(formatted_lines)

def batch_convert_pdfs(pdf_dir: str, output_dir: str):
    """
    Convert all PDFs under pdf_dir (recursively) to Markdown, writing to output_dir
    while mirroring the subfolder structure.
    """
    pdf_dir = Path(pdf_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in pdf_dir.rglob("*.pdf"):
        rel = pdf_path.relative_to(pdf_dir).with_suffix(".md")
        out_path = output_dir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        md_text = pymupdf4llm.to_markdown(pdf_path)
        no_strikethrough = remove_strikethrough(md_text)
        md_with_headers = clean_markdown_headers(no_strikethrough)
        out_path.write_text(md_with_headers, encoding="utf-8")

#================================================
# CHECK OUTPUT (uncomment to see example output for a file)

# pdf_path = (
#     "Running_RAGged/LabDocs/Synthetic_Procedures/1_3-BETA-D-GLUCAN_FUNGITELL_SERUM.pdf"
#     # "Running_RAGgedTEAM_NAME/LabDocs/Synthetic_Procedures/ZIKA_VIRUS_PCR_MOLECULAR_DETECTION_RANDOM_URINE.pdf"
# )

# md_text = pymupdf4llm.to_markdown(pdf_path)
# print(md_text)

# no_strikethrough = remove_strikethrough(md_text)
# print(no_strikethrough)

# md_with_headers = clean_markdown_headers(no_strikethrough)
# print(md_with_headers)

#================================================

# batch convert to markdownDocs/Synthetic_Procedures directory
batch_convert_pdfs(
    pdf_dir="Running_RAGged/LabDocs/Synthetic_Procedures",
    output_dir="Running_RAGged/markdownDocs/Synthetic_Procedures"
)
