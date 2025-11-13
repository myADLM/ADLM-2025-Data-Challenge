#

# Team Name: Running RAGged

**Team Members:** Daniel Barry MLS (ASCP)^CM^, Brendan Graham (MS) (CHOP); Peter Ilyin (UPENN)

------------------------------------------------------------------------

Our goal for this challenge was to develop a compliant and accurate RAG model with an interactive chat front end capable of running on a laptop. We achieved this by utilizing the following open-source tooling:

-   [LangChain](https://docs.langchain.com/): an open-source orchestration framework for application development using LLMs

-   [Ollama](www.ollama.com): an open-source framework for running LLMs locally on a laptop

-   [ChromaDB](https://docs.trychroma.com/docs/overview/introduction): an open-source vector database

-   [Streamlit](https://docs.streamlit.io/): an open-source framework for building and sharing interactive web applications

### Development Methodology

Our general development strategy was as follows:

1.  Convert the FDA Docs and Synthetic Procedures PDFs to Markdown, an optimal format for machine readability
2.  "Chunk" each Markdown into smaller, overlapping sections
3.  Create embeddings of each chunk using embedding models retrieved from Ollama and store the embeddings in ChromaDB vector database
    -   The embeddings are numerical representations of text. They encode the meaning of the text in a high-dimensional space so that semantically similar chunks are close together
    -   The ChromaDB vector database is designed to store embeddings and perform similarity search efficiently
4.  Create an interactive application where a 1) a user submits a query, 2) that query is embedded using the same embedding model from step 3, 3) a similarity search is be performed that returns the top 10 most relevant chunks and 4) the most relevant documents are synthesized and interpreted by an LLM which generates the query answer

One of our main assumptions was that the FDA docs were public domain and thus not protected by any IP restrictions, while the Synthetic Procedures may contain copyright material. We elected to use Google Document AI to convert the FDA docs to Markdown, while local Ollama models were used to convert the Synthetic Procedures. Converting the FDA docs using Google Document AI is the only time a non-open-source tool was used. While it is possible to convert the FDA PDFs to Markdown using Local Ollama models, given the time restrictions and likely better performance of Google Document AI (especially for scanned PDFs) we elected to proceed with the commercial option for the FDA documents.

### Quality Control

We tested a number of different embedding models and LLM combinations, and developed a QC-strategy similar to the one described in

> Yang, He S., Li, Jieli, Yi, Xin and Wang, Fei. "Performance evaluation of large language models with chain-of-thought reasoning ability in clinical laboratory case interpretation" *Clinical Chemistry and Laboratory Medicine (CCLM)*, vol. 63, no. 8, 2025, pp. e199-e201. <https://doi.org/10.1515/cclm-2025-0055>

Using `QC-App.py`, we asked the same questions to each combination of embedding model and LLM and scored the results to determine the most accurate pairing which was Qwen3 as the embedding model OpenAI’s gpt-oss as the LLM.

------------------------------------------------------------------------

# Quick Start

## Activate the project environment with UV

-   Install UV if needed: `pip install uv`
-   cd into the directory: `cd Running_RAGged`
-   Synchronize local Python environment with project dependencies: `uv sync` (if you have SSL/TLS issues use `uv sync --native-tls`)
-   activate the virtual env: `.venv\Scripts\activate` (optional: find the venv on your machine for interpreter if needed `dir .venv\Scripts\python.exe`)

## Download companion files

-   Qwen embedding database and Markdown Chunks (for reference for answer verification) are available at: <https://drive.google.com/drive/folders/1xgYDuqeSd6l9IkKQF-E2NUupLi79Bfzo>

-   Note that the app back-end (`embedding_utils/backend.py`) expects these files in specific locations. Save them accordingly, or update the values in the script.\

    ``` python
    # ---- Hardcoded parameters ----
    CHROMA_PATH = "chroma/all-minilm" # vector databse
    DOCS_DIR = "docs/Markdown-Output" # markdown directory
    ```

## Install Ollama & pull models

-   Download Ollama: `https://ollama.com/`
-   Install the LLM in terminal: `ollama pull gpt-oss:20b`

## Run the interactive app locally

-   `streamlit run embedding_utils/app_streamlit_ui.py`

------------------------------------------------------------------------

# Full RAG Development Workflow

Use the following workflow to re-create the RAG locally from scratch

## Working with UV

-   Install UV: `pip install uv`
-   cd into the Team directory: `cd Running_RAGged`
-   activate the virtual env: `.venv\Scripts\activate` (optional: find the venv on your machine for interpreter if needed `dir .venv\Scripts\python.exe`)
-   install needed packages: `uv sync`
-   To add a new package: `uv add package_name` (optionally `uv add package_name --native-tls`)
-   Quick Start when reopening terminal `cd Running_RAGged; .\.venv\Scripts\activate`

## Working with Ollama

-   Download Ollama: https://ollama.com/
-   Install models in terminal:
    -   `ollama pull gpt-oss:20b`
    -   `ollama pull qwen3-embedding`
-   If using alternative models replace model-name with your intended model: `ollama pull model-name`

## Load LabDocs to IDE

Windows Command Line

`curl -L -C - -o LabDocs.zip \     "https://zenodo.org/records/16328490/files/LabDocs.zip?download=1" tar -xf LabDocs.zip`

## Convert PDFs to Markdown

Run each line in order in terminal - make sure to change DATA_PATH parameter to where you saved the PDFs

-   Synthetic Procedures - performed locally using Ollama

    -   `python embedding_utils/populate_database_from_markdown_batch.py`

-   FDA Docs - uses Google Document AI\
    \
    Note: Google Cloud API needed

    -   `python docai_markdown_full.py --pdf path/to/pdfs --o path/to/output`

## Create vector databases

-   `python Running_RAGged\embedding_utils\populate_database_from_markdown_batch.py --model qwen3-embedding --batch-size 128 --persist-every 10`

Alternative models:

-   `python Running_RAGged\embedding_utils\populate_database_from_markdown_batch.py --model all-minilm --batch-size 128 --persist-every 10`

<!-- -->

-   `python Running_RAGged\embedding_utils\populate_database_from_markdown_batch.py --model mxbai-embed-large --batch-size 128 --persist-every 10`

-   `python Running_RAGged\embedding_utils\populate_database_from_markdown_batch.py --model nomic-embed-text --batch-size 128 --persist-every 10`

-   `python Running_RAGged\embedding_utils\populate_database_from_markdown_batch.py --model bge-m3 --batch-size 128 --persist-every 10`

## Query with App

-   `streamlit run embedding_utils/app_streamlit_ui.py`
