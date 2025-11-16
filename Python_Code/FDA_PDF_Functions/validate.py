# -*- coding: utf-8 -*-
"""
validate.py

Validate PDFs in a directory tree using pypdf.

This module is typically used after merging and copying operations to
confirm that all resulting PDFs are readable and unencrypted.

Developed by:
    Matthew G. Bayes
    Baylor College of Medicine (BCM) / Texas Children's Hospital

Created: 2025-11-15
Last Updated: 2025-11-15
"""

# Last updated: 2025-11-15

import os
from typing import List, Tuple

from pypdf import PdfReader


def validate_pdfs(root_dir: str) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Recursively validate PDFs in `root_dir` using pypdf.

    Each PDF is opened and its first page is accessed (if present) to verify
    that it can be read without errors. Encrypted PDFs are reported as invalid.

    Parameters
    ----------
    root_dir : str
        Root of the directory tree to validate.

    Returns
    -------
    Tuple[List[str], List[Tuple[str, str]]]
        A tuple of:
        - valid_files: list of PDF paths that opened and read successfully.
        - invalid_files: list of (path, reason) tuples where `reason` is
          a short description (e.g., "encrypted" or an exception string).
    """
    valid_files: List[str] = []
    invalid_files: List[Tuple[str, str]] = []

    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if not fname.lower().endswith(".pdf"):
                # Skip non-PDF files
                continue

            pdf_path = os.path.join(dirpath, fname)
            try:
                with open(pdf_path, "rb") as f:
                    reader = PdfReader(f)
                    if reader.is_encrypted:
                        invalid_files.append((pdf_path, "encrypted"))
                        continue

                    # Accessing the first page is a simple sanity check
                    _ = reader.pages[0] if reader.pages else None

                valid_files.append(pdf_path)
            except Exception as e:
                invalid_files.append((pdf_path, str(e)))

    return valid_files, invalid_files
