# -*- coding: utf-8 -*-
"""
merge_paired_fda_files.py

End-to-end script for:

1. Summarizing a baseline FDA PDF directory.
2. Identifying BASE / BASE_REVIEW pairs.
3. Merging paired PDFs into a mirrored "<root>_Merged" directory tree.
4. Copying PDFs from failed merges into the mirrored tree.
5. Copying unpaired PDFs into the mirrored tree.
6. Summarizing the final merged tree.
7. Validating all PDFs in the merged tree.

This script uses the FDA_PDF_Functions library, developed by
Matthew G. Bayes (Baylor College of Medicine (BCM) / Texas Children's Hospital).

Assumptions
-----------
- The root FDA directory is located at ".\\LabDocs\\FDA".
- BASE/REVIEW pairs follow the naming pattern:
    BASE.pdf
    BASE_REVIEW.pdf

Created: 2025-11-15
Last Updated: 2025-11-15
"""

# Last updated: 2025-11-15

from FDA_PDF_Functions import (
    find_review_pairs,
    merge_review_pairs,
    copy_unpaired_files,
    copy_failed_merges,
    validate_pdfs,
    summarize_directory,
)


def main() -> None:
    """
    Run the full FDA PDF pairing, merging, copying, and validation pipeline.

    Steps
    -----
    1. Summarize the baseline FDA directory.
    2. Find paired/unpaired PDFs.
    3. Merge pairs into "<root>_Merged".
    4. Summarize successful merges.
    5. Copy PDFs involved in failed merges into "<root>_Merged".
    6. Copy any unpaired PDFs into "<root>_Merged".
    7. Summarize the completed merged directory.
    8. Validate all PDFs in "<root>_Merged" and print a summary of results.
    """
    # Root of the original FDA directory (relative to this script)
    fda_root = r".\LabDocs\FDA"

    # 1. Print list and stats of baseline FDA file set
    summarize_directory(fda_root, "FDA_Dir_Baseline_Set.txt")

    # 2. Identify pairs and unpaired PDFs
    pairs, unpaired = find_review_pairs(fda_root, "Pair_Report.txt")

    # 3. Merge pairs to ".\LabDocs\FDA_Merged" (sibling of FDA), preserving subfolders
    outputs, failures = merge_review_pairs(pairs, fda_root, overwrite=True)

    # 4. Log or print failures for review
    print("Merge failures:")
    for base_pdf, review_pdf, reason in failures:
        print(f"  BASE: {base_pdf}")
        print(f"  REVIEW: {review_pdf}")
        print(f"  REASON: {reason}")
        print("-" * 60)

    # 5. Print list and stats of merged FDA file set before moving unpaired files
    summarize_directory(r".\LabDocs\FDA_Merged", "FDA_Only_Successful_Merges.txt")

    # 6. Copy the failed merge files into the mirrored structure
    copied_failed, skipped_failed = copy_failed_merges(failures, fda_root)

    # 7. Copy unpaired PDFs into the mirrored FDA_Merged directory
    copied_unpaired, skipped_unpaired = copy_unpaired_files(unpaired, fda_root)

    # 8. Print list and stats of merged FDA file set including unpaired files
    summarize_directory(r".\LabDocs\FDA_Merged", "FDA_Merged.txt")

    # 9. Check your merged directory structure for valid PDFs
    valid, invalid = validate_pdfs(r".\LabDocs\FDA_Merged")

    # 10. Summarize results to stdout
    print(f"Valid PDFs: {len(valid)}")

    if invalid:
        print("Invalid PDFs found:")
        for path, reason in invalid:
            print(f"  {path} -> {reason}")

    # Optionally, print copy summaries
    if skipped_failed or skipped_unpaired:
        print("\nSkipped copies:")
        for src, reason in skipped_failed + skipped_unpaired:
            print(f"  {src} -> {reason}")


if __name__ == "__main__":
    main()
