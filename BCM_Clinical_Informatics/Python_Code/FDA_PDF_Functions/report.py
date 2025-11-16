# -*- coding: utf-8 -*-
"""
report.py

Generate a simple text summary of all files within a directory tree.

This is useful for:
- Capturing the "baseline" state of an FDA document collection before
  any merges or transformations.
- Comparing pre- and post-merge directory structures.

Developed by:
    Matthew G. Bayes
    Baylor College of Medicine (BCM) / Texas Children's Hospital

Created: 2025-11-15
Last Updated: 2025-11-15
"""

# Last updated: 2025-11-15

import os


def summarize_directory(root_dir: str, output_filename: str) -> None:
    """
    Summarize directory contents (counts per folder + detailed listing).

    The summary includes:
    - A table of directory paths and file counts.
    - A total file count across the entire tree.
    - A detailed listing of filenames by directory at the end of the report.

    Parameters
    ----------
    root_dir : str
        Root of the directory tree to summarize.
    output_filename : str
        Path to the text file where the summary report will be written.

    Returns
    -------
    None
    """
    summary = []
    total_files = 0

    # First pass: collect counts per directory
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        count = len(filenames)
        total_files += count
        summary.append((dirpath, count))

    # Sort by directory path to keep report stable
    summary.sort(key=lambda x: x[0])

    summary_lines = [
        f"Output file: {output_filename}",
        f"Directory summary for: {os.path.abspath(root_dir)}",
        "-" * 60,
        f"{'Directory':<50} {'File Count':>10}",
        "-" * 60,
    ]
    for dirpath, count in summary:
        summary_lines.append(f"{dirpath:<50} {count:>10}")
    summary_lines.append("-" * 60)
    summary_lines.append(f"{'TOTAL FILES':<50} {total_files:>10}")

    # Write the header and table
    with open(output_filename, "w", encoding="utf-8") as f:
        for line in summary_lines:
            f.write(line + "\n")

        # Second pass: detailed listing of all files
        for dirpath, _dirnames, filenames in os.walk(root_dir):
            if filenames:
                f.write(f"\nDirectory: {dirpath}\n")
                for fname in filenames:
                    f.write(f"  {fname}\n")
