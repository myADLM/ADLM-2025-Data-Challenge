# FDA_PDF_Functions

Utility library and driver script for working with FDA-related PDF review packets.

This toolkit is designed to:

- Scan an FDA document tree and summarize its contents.
- Identify paired FDA PDFs (e.g., `BASE.pdf` and `BASE_REVIEW.pdf`).
- Merge paired PDFs into a single combined file while mirroring the original directory structure.
- Copy unpaired or failed-merge PDFs into the mirrored output tree.
- Validate all resulting PDFs to confirm they are readable and unencrypted.

---

## Author & Institution

**Author:** Matthew G. Bayes  
**Institution:** Baylor College of Medicine (BCM) / Texas Children's Hospital  
**Created:** 2025-11-15  
**Last Updated:** 2025-11-15  

---

## Repository Structure

```text
FDA_PDF_Functions/
    __init__.py       # Package exports for the library
    copying.py        # Copy unpaired and failed-merge PDFs into mirrored structure
    merge.py          # Merge paired BASE/BASE_REVIEW PDFs
    pairing.py        # Find BASE/BASE_REVIEW pairs and generate a pairing report
    report.py         # Generate baseline and post-merge directory summaries
    validate.py       # Validate PDFs using pypdf

merge_paired_fda_files.py  # End-to-end driver script
README.md                  # This file

** Source LabDocs folder should be placed in the same directory as merge_paired_fda_files.py **
