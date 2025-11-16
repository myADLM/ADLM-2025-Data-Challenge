# -*- coding: utf-8 -*-
"""
pairing.py

Identify paired and unpaired FDA PDF files in a directory tree.

A "pair" is defined as:

    BASE.pdf
    BASE_REVIEW.pdf

where:
- BASE is any base filename (case-insensitive),
- BASE_REVIEW is the same base filename with the suffix "_REVIEW" (case-insensitive).

This module scans all subdirectories, groups PDFs by base name, and classifies
them as paired vs unpaired. It also writes a human-readable text report that
summarizes the pairing results and lists files by subdirectory.

Developed by:
    Matthew G. Bayes
    Baylor College of Medicine (BCM) / Texas Children's Hospital

Created: 2025-11-15
Last Updated: 2025-11-15
"""

# Last updated: 2025-11-15

import os
from collections import defaultdict
from typing import Dict, List, Tuple


def find_review_pairs(root_dir: str, output_filename: str):
    """
    Find BASE.pdf and BASE_REVIEW.pdf pairs per directory; write a report.

    This function walks `root_dir`, grouping all *.pdf files by base name
    (with or without a "_REVIEW" suffix). For each directory:

    - If both BASE.pdf and BASE_REVIEW.pdf are present, they are recorded
      as a pair.
    - Any remaining unmatched PDFs are recorded as unpaired.

    A summary report is written to `output_filename`, which includes:
        - Counts of PDFs, paired files, and unpaired files per directory.
        - Per-directory lists of paired and unpaired files.

    Parameters
    ----------
    root_dir : str
        Root of the FDA directory tree to scan.
    output_filename : str
        Path to the text file where the pairing report will be written.

    Returns
    -------
    Tuple[Dict[str, List[Tuple[str, str]]], Dict[str, List[str]]]
        A tuple of:
        - pairs: mapping from directory path to a list of
          (base_pdf_path, review_pdf_path) tuples.
        - unpaired: mapping from directory path to a list of unpaired
          PDF paths.
    """
    def is_pdf(fname: str) -> bool:
        """Return True if the filename is a PDF (case-insensitive)."""
        return fname.lower().endswith(".pdf")

    def split_base_review(fname: str) -> Tuple[str, bool]:
        """
        Split filename into base name and review flag.

        If the filename (without extension) ends in "_review" (case-insensitive),
        return (<base_without_review>, True). Otherwise, return (<base>, False).
        """
        name, _ext = os.path.splitext(fname)
        lower = name.lower()
        if lower.endswith("_review"):
            # Strip the "_review" suffix (7 characters)
            return name[:-7], True
        return name, False

    pairs: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    unpaired: Dict[str, List[str]] = defaultdict(list)

    per_dir_counts = []
    total_pdfs = 0
    total_pairs = 0
    total_unpaired = 0

    # Walk the directory tree and group PDFs by base name and review status
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        pdfs = [f for f in filenames if is_pdf(f)]
        total_pdfs += len(pdfs)

        base_to_main = {}
        base_to_review = {}

        # Build lookups of base -> main/review paths
        for fname in pdfs:
            base, is_review = split_base_review(fname)
            abspath = os.path.abspath(os.path.join(dirpath, fname))
            if is_review:
                base_to_review.setdefault(base, abspath)
            else:
                base_to_main.setdefault(base, abspath)

        dir_pairs: List[Tuple[str, str]] = []
        dir_unpaired: List[str] = []

        # Combine base names seen in both dictionaries
        all_bases = sorted(set(base_to_main.keys()) | set(base_to_review.keys()), key=str.lower)

        for base in all_bases:
            main_path = base_to_main.get(base)
            review_path = base_to_review.get(base)

            if main_path and review_path:
                # We found a BASE/BASE_REVIEW pair
                dir_pairs.append((main_path, review_path))
            else:
                # Anything missing a complement is treated as unpaired
                if main_path and not review_path:
                    dir_unpaired.append(main_path)
                if review_path and not main_path:
                    dir_unpaired.append(review_path)

        # Sort to keep report output stable and predictable
        dir_pairs.sort(key=lambda t: (t[0].lower(), t[1].lower()))
        dir_unpaired.sort(key=str.lower)

        if dir_pairs:
            pairs[dirpath] = dir_pairs
        if dir_unpaired:
            unpaired[dirpath] = dir_unpaired

        per_dir_counts.append((dirpath, len(pdfs), len(dir_pairs) * 2, len(dir_unpaired)))
        total_pairs += len(dir_pairs)
        total_unpaired += len(dir_unpaired)

    # Sort counts by directory path for readability in the report
    per_dir_counts.sort(key=lambda x: x[0])

    # Build the text report
    lines: List[str] = []
    lines.append(f"Output file: {output_filename}")
    lines.append(f"Paired PDF review scan for: {os.path.abspath(root_dir)}")
    lines.append("-" * 80)
    lines.append(f"{'Directory':<50} {'PDFs':>6} {'Paired':>8} {'Unpaired':>9}")
    lines.append("-" * 80)

    for dirpath, pdf_count, paired_files_count, unpaired_count in per_dir_counts:
        lines.append(f"{dirpath:<50} {pdf_count:>6} {paired_files_count:>8} {unpaired_count:>9}")

    lines.append("-" * 80)
    lines.append(f"{'TOTAL PDFs':<50} {total_pdfs:>6}")
    lines.append(f"{'TOTAL PAIRS (files)':<50} {total_pairs * 2:>6}  ({total_pairs} pairs)")
    lines.append(f"{'TOTAL UNPAIRED (files)':<50} {total_unpaired:>6}")
    lines.append("-" * 80)

    # Detailed listing: paired files
    lines.append("\nPAIRED FILES BY SUBDIRECTORY")
    lines.append("-" * 80)
    if pairs:
        for dirpath in sorted(pairs.keys(), key=str.lower):
            lines.append(f"Directory: {dirpath}")
            for left, right in pairs[dirpath]:
                lines.append(f'  "{os.path.basename(left)}", "{os.path.basename(right)}"')
            lines.append("")
    else:
        lines.append("(none)")

    # Detailed listing: unpaired files
    lines.append("\nUNPAIRED FILES BY SUBDIRECTORY")
    lines.append("-" * 80)
    if unpaired:
        for dirpath in sorted(unpaired.keys(), key=str.lower):
            lines.append(f"Directory: {dirpath}")
            for path in unpaired[dirpath]:
                lines.append(f"  {os.path.basename(path)}")
            lines.append("")
    else:
        lines.append("(none)")

    # Write the report to disk
    with open(output_filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return pairs, unpaired
