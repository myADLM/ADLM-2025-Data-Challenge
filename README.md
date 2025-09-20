# LabDocs Unlocked – ADLM 2025 Data Science Challenge

## Overview
This project is our submission for the **ADLM 2025 Data Science Challenge**.  

The tool ingests laboratory documentation (synthetic dataset provided by ADLM), builds a searchable index, and allows users to query information efficiently.  
Answers are returned with references to the source documents (file name, page number, and snippet) for transparency and explainability.

---

## Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/<your-username>/ADLM-2025-Data-Challenge.git
cd ADLM-2025-Data-Challenge
pip install -r requirements.txt
```

Python 3.10+ is recommended.

---

## Usage

### Step 1 – Download and Extract Dataset
Download `LabDocs.zip` (~3.5 GB) from [Zenodo](https://zenodo.org/records/16328490) and extract to a folder, e.g. `./LabDocs`.

### Step 2 – Build the Index
```bash
python build_index.py --docs ./LabDocs
```
This parses the documents and creates a vector index for searching.

### Step 3 – Run the App
Run the local query app:
```bash
python app_answer_local.py
```

Ask a question, for example:
```
Q: What is the recommended storage temperature for reagent X?
A: Store at 2–8 °C  
   Source: Protocol_123.pdf · p. 4  
   Snippet: "...Store between 2–8 °C. Do not freeze..."
```

### Logs
Outputs and run history are stored in the `run_logs/` folder.

---

## File Structure

- `build_index.py` → build searchable index from documents  
- `app_answer_local.py` → query interface for local use  
- `index.py` → alternate entry point for running queries  
- `ocr_all_pdfs_mp.py` → OCR pipeline for PDF ingestion  
- `requirements.txt` → list of Python dependencies  
- `config.yaml` → configuration (dataset path, index path, chunk size, etc.)  
- `tests/` → sample evaluation scripts and QA pairs  
- `run_logs/` → logs from runs  
- `www/` → graphical abstract / static assets  

---

## Citations & Explainability
Every answer is returned with:
- **Source file name**
- **Page number (if available)**
- **Snippet of supporting text**

Example:
```
Source: SOP_45.pdf · p. 12
Snippet: "...Centrifuge at 3000 × g for 10 minutes..."
```

---

## Evaluation (Accuracy)
A small evaluation harness is provided in `tests/`.  
Run with:
```bash
python tests/run_eval.py --index ./index_dir --k 5
```
This checks accuracy against a set of sample Q&A pairs.

---

## Deployment
Currently configured for local use. Options:
- **Conda environment**: use `requirements.txt` or `environment.yml`
- **Docker** (optional):
  ```bash
  docker build -t labdocs .
  docker run -v $(pwd)/LabDocs:/app/LabDocs labdocs
  ```
- **Streamlit** (if preferred):
  ```bash
  streamlit run app_answer_local.py
  ```

---

## Reusability
The tool can ingest **any new document store** by updating the `config.yaml` file with the path to your dataset.

---

## Contact
**Team:** cyberkeen  
**Contact:** kayweng.choy@gmail.com
