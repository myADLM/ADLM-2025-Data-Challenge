# -*- coding: utf-8 -*-
"""
FDA_PDF_Functions package.

Utility functions for working with FDA-related PDF review packets, including:

- Scanning a directory tree and summarizing contents.
- Identifying paired FDA PDFs (e.g., BASE.pdf and BASE_REVIEW.pdf).
- Merging paired PDFs while mirroring directory structure.
- Copying unpaired or failed-merge files into a mirrored output tree.
- Validating PDFs after processing.

Developed by:
    Matthew G. Bayes
    Baylor College of Medicine (BCM) / Texas Children's Hospital

Created: 2025-11-15
Last Updated: 2025-11-15
"""

# Last updated: 2025-11-15

from .report import summarize_directory
from .pairing import find_review_pairs
from .merge import merge_review_pairs
from .copying import copy_unpaired_files, copy_failed_merges
from .validate import validate_pdfs

__all__ = [
    "summarize_directory",
    "find_review_pairs",
    "merge_review_pairs",
    "copy_unpaired_files",
    "copy_failed_merges",
    "validate_pdfs",
]
