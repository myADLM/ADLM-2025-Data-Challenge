from typing import List, Tuple, Dict
import re

def annotate_chunk_from_path(chunks: List[Tuple[str, str]], config: Dict[str, str]) -> List[List[str]]:
    """
    Annotate chunks based on their file path using regex patterns.

    - chunks: list of (chunk_path, chunk_text)
    - config: mapping of regex pattern -> annotation text (string only)

    Returns a list (aligned with input chunks) where each element is a list of
    annotation strings.
    """
    annotations: List[List[str]] = []
    for chunk_path, _ in chunks:
        chunk_annotations: List[str] = []
        for pattern, annotation_text in config.items():
            if re.search(pattern, chunk_path):
                chunk_annotations.append(str(annotation_text))
        annotations.append(chunk_annotations)
    return annotations

def annotate_all_chunks(chunks_dir: Path, config: Dict[str, str]):
    """
    Read all chunk files under chunks_dir, compute path-based annotations using
    regex patterns from config, and prepend the resulting annotation text to each
    chunk file.

    - chunks_dir: root directory containing chunk files (mirrors source structure)
    - config: mapping of regex pattern -> annotation text (string only)

    For each chunk, all matching annotations are joined by newlines and
    inserted as a header before the original chunk content. If the chunk
    already begins with the same annotation header, it is left unchanged.
    """
    chunks = read_text_documents(chunks_dir)
    annotations = annotate_chunk_from_path(chunks, config)
    for (chunk_path, chunk_text), annotation_list in zip(chunks, annotations):
        annotation_string = "\n".join(annotation_list)
        if chunk_text.startswith(annotation_string):
            continue
        with open(chunks_dir / chunk_path, "w") as f:
            f.write(f"{annotation_string}\n\n{chunk_text}")
            