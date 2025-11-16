# -*- coding: utf-8 -*-
"""
copying.py

Helpers for copying unpaired or failed-merge FDA PDFs into a mirrored output
directory structure. The typical use case is to:

1. Merge successfully paired BASE/BASE_REVIEW PDFs.
2. Copy the PDFs that could not be merged (failed merges).
3. Copy any remaining unpaired PDFs.

This produces a complete, mirror-structured "<root>_Merged" tree that contains:
- successfully merged PDFs,
- original PDFs involved in failed merges,
- and unpaired PDFs.

Developed by:
    Matthew G. Bayes
    Baylor College of Medicine (BCM) / Texas Children's Hospital

Created: 2025-11-15
Last Updated: 2025-11-15
"""

# Last updated: 2025-11-15

import os
import shutil
from typing import Dict, List, Optional, Tuple


def _ensure_output_root(root_dir: str, output_root: Optional[str]) -> str:
    """
    Resolve the absolute path to the output root directory.

    If `output_root` is not explicitly provided, a sibling directory named
    "<root_dir>_Merged" (based on the basename of root_dir) is created/used.

    Parameters
    ----------
    root_dir : str
        Path to the original FDA directory tree.
    output_root : Optional[str]
        Optional explicit path to the output root. If None, a default
        "<root>_Merged" sibling directory is used.

    Returns
    -------
    str
        Absolute path to the output root directory.
    """
    root_abs = os.path.abspath(root_dir)
    parent = os.path.dirname(root_abs)
    root_name = os.path.basename(root_abs)
    return os.path.join(parent, f"{root_name}_Merged") if output_root is None else output_root


def copy_unpaired_files(
    unpaired: Dict[str, List[str]],
    root_dir: str,
    output_root: Optional[str] = None,
    overwrite: bool = False,
) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Copy unpaired PDFs into a mirrored <root>_Merged directory structure.

    This function is intended to be called after `find_review_pairs` has been
    used to identify unpaired PDFs. For each directory key in `unpaired`,
    the list of PDF paths is copied into the corresponding mirrored
    subdirectory under the output root.

    Parameters
    ----------
    unpaired : Dict[str, List[str]]
        Mapping from directory path to a list of unpaired PDF file paths
        (absolute paths).
    root_dir : str
        Root of the source FDA directory tree that was scanned.
    output_root : Optional[str], default None
        Optional path for the mirrored output root. If None, a sibling
        directory "<root>_Merged" is used.
    overwrite : bool, default False
        If False, existing files at the destination are not overwritten
        and are recorded in the `skipped_files` list.

    Returns
    -------
    Tuple[List[str], List[Tuple[str, str]]]
        A tuple of:
        - copied_files: list of destination paths that were successfully copied.
        - skipped_files: list of (source_path, reason) tuples.
    """
    root_abs = os.path.abspath(root_dir)
    output_root = _ensure_output_root(root_dir, output_root)
    os.makedirs(output_root, exist_ok=True)

    copied_files: List[str] = []
    skipped_files: List[Tuple[str, str]] = []

    for dirpath, files in unpaired.items():
        # Determine the relative subdirectory and mirror its structure
        rel_subdir = os.path.relpath(os.path.abspath(dirpath), root_abs)
        dest_dir = output_root if rel_subdir in (".", "") else os.path.join(output_root, rel_subdir)
        os.makedirs(dest_dir, exist_ok=True)

        for src_path in files:
            filename = os.path.basename(src_path)
            dest_path = os.path.join(dest_dir, filename)

            if not overwrite and os.path.exists(dest_path):
                skipped_files.append((src_path, "exists and overwrite=False"))
                continue

            try:
                shutil.copy2(src_path, dest_path)
                copied_files.append(dest_path)
            except Exception as e:
                # Record any I/O or filesystem-related issues
                skipped_files.append((src_path, str(e)))

    return copied_files, skipped_files


def copy_failed_merges(
    failures: List[Tuple[str, str, str]],
    root_dir: str,
    output_root: Optional[str] = None,
    overwrite: bool = False,
) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Copy base/review PDFs for failed merges into a mirrored <root>_Merged tree.

    `failures` should be the list produced by `merge_review_pairs`, where each
    entry is (base_pdf, review_pdf, reason). This function ensures that the
    original PDFs for these failed merges are still preserved in the final
    mirrored output directory structure.

    Parameters
    ----------
    failures : List[Tuple[str, str, str]]
        List of failed merge records: (base_pdf_path, review_pdf_path, reason).
    root_dir : str
        Root of the source FDA directory tree that was scanned.
    output_root : Optional[str], default None
        Optional path for the mirrored output root. If None, a sibling
        directory "<root>_Merged" is used.
    overwrite : bool, default False
        If False, existing files at the destination are not overwritten
        and are recorded in the `skipped_files` list.

    Returns
    -------
    Tuple[List[str], List[Tuple[str, str]]]
        A tuple of:
        - copied_files: list of destination paths that were successfully copied.
        - skipped_files: list of (source_path, reason) tuples.
    """
    root_abs = os.path.abspath(root_dir)
    output_root = _ensure_output_root(root_dir, output_root)
    os.makedirs(output_root, exist_ok=True)

    copied_files: List[str] = []
    skipped_files: List[Tuple[str, str]] = []

    for base_pdf, review_pdf, _reason in failures:
        # Process both base and review paths individually
        for src_path in (base_pdf, review_pdf):
            if not src_path or not os.path.exists(src_path):
                skipped_files.append((src_path or "None", "missing"))
                continue

            rel_subdir = os.path.relpath(os.path.dirname(src_path), root_abs)
            dest_dir = output_root if rel_subdir in (".", "") else os.path.join(output_root, rel_subdir)
            os.makedirs(dest_dir, exist_ok=True)

            dest_path = os.path.join(dest_dir, os.path.basename(src_path))

            if not overwrite and os.path.exists(dest_path):
                skipped_files.append((src_path, "exists and overwrite=False"))
                continue

            try:
                shutil.copy2(src_path, dest_path)
                copied_files.append(dest_path)
            except Exception as e:
                skipped_files.append((src_path, str(e)))

    return copied_files, skipped_files
