# FDA Regulatory Intelligence Assistant — Git Documentation

## Overview
This repository contains an **AI-powered regulatory content assistant** designed to support **FDA 510(k) research, device classification analysis, and regulatory intelligence workflows**. The system provides **targeted, citation-level retrieval** of FDA documentation and related regulatory materials.

The assistant specializes in structured **Food and Drug Administration (FDA)** content, including:

- **510(k) summaries**
- **Decision letters**
- **Regulatory classifications**
- **Product codes and device categories**
- **Related regulatory reference materials**

---

## Data Source Optimization
The FDA source directories were **optimized and consolidated** using the included Python tools:

- `FDA_PDF_Functions` library  
- `merge_paired_fda_files.py` automation script  

These utilities were used to **locate and pair FDA REVIEW and BASE submission PDF files**, then **merge them into a single, unified file** under the same base filename for performance and consistency.

Example output filename format:

