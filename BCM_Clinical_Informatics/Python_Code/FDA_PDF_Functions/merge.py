# -*- coding: utf-8 -*-
"""
merge.py

Merge paired FDA PDFs (e.g., BASE.pdf and BASE_REVIEW.pdf) into a single
combined PDF file while mirroring the directory structure of the source tree.

The typical workflow:

1. Use `find_review_pairs` to identify (BASE, BASE_REVIEW) pairs.
2. Pass the resulting `pairs` dictionary to `merge_review_pairs`.
3. Use the returned `outputs` (successes) and `failures` to drive
   subsequent copying and validation steps.

Developed by:
    Matthew G. Bayes
    Baylor College of Medicine (BCM) / Texas Children's Hospital

Created: 2025-11-15
Last Updated: 2025-11-15
"""

# Last updated: 2025-11-15

import os
from typing import Dict, List, Optional, Tuple

from pypdf import PdfReader, PdfWriter


def merge_review_pairs(
    pairs: Dict[str, List[Tuple[str, str]]],
    root_dir: str,
    output_root: Optional[str] = None,
    overwrite: bool = True,
):
    """
    Merge (BASE.pdf, BASE_REVIEW.pdf) into one PDF, mirroring folder structure.

    For each directory in `pairs`, this function creates a corresponding
    subdirectory within the output root (e.g., "<root>_Merged") and writes a
    merged PDF that contains:

        [all pages from BASE.pdf] + [all pages from BASE_REVIEW.pdf]

    The merged PDF is named using the basename of the base PDF.

    Parameters
    ----------
    pairs : Dict[str, List[Tuple[str, str]]]
        Mapping of directory path to a list of (base_pdf, review_pdf) tuples,
        as returned by `find_review_pairs`.
    root_dir : str
        Root of the source FDA directory tree that was scanned.
    output_root : Optional[str], default None
        Optional path for the mirrored output root. If None, a sibling
        directory "<root>_Merged" is used.
    overwrite : bool, default True
        If False and a destination file already exists, the pair is not
        merged and is recorded as a failure.

    Returns
    -------
    Tuple[List[str], List[Tuple[str, str, str]]]
        A tuple of:
        - outputs: list of merged PDF paths successfully written.
        - failures: list of (base_pdf, review_pdf, reason) tuples detailing
          merge failures (I/O or PDF parsing issues, existing file when
          overwrite=False, etc.).
    """
    root_abs = os.path.abspath(root_dir)
    parent = os.path.dirname(root_abs)
    root_name = os.path.basename(root_abs)

    if output_root is None:
        output_root = os.path.join(parent, f"{root_name}_Merged")

    os.makedirs(output_root, exist_ok=True)

    outputs: List[str] = []
    failures: List[Tuple[str, str, str]] = []

    for dirpath, pair_list in pairs.items():
        # Mirror source directory structure under the output root
        rel_subdir = os.path.relpath(os.path.abspath(dirpath), root_abs)
        dest_dir = output_root if rel_subdir in (".", "") else os.path.join(output_root, rel_subdir)
        os.makedirs(dest_dir, exist_ok=True)

        for base_pdf, review_pdf in pair_list:
            base_name = os.path.basename(base_pdf)
            out_path = os.path.join(dest_dir, base_name)

            if (not overwrite) and os.path.exists(out_path):
                failures.append((base_pdf, review_pdf, "exists and overwrite=False"))
                continue

            try:
                writer = PdfWriter()

                # Append pages from the base PDF
                with open(base_pdf, "rb") as f1:
                    base_reader = PdfReader(f1)
                    for page in base_reader.pages:
                        writer.add_page(page)

                # Append pages from the review PDF
                with open(review_pdf, "rb") as f2:
                    rev_reader = PdfReader(f2)
                    for page in rev_reader.pages:
                        writer.add_page(page)

                # Write combined PDF to destination
                with open(out_path, "wb") as out_f:
                    writer.write(out_f)

                outputs.append(out_path)
            except Exception as e:
                # Record any parsing or I/O failures with a reason string
                failures.append((base_pdf, review_pdf, str(e)))

    return outputs, failures
