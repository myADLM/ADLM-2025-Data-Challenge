# HOWTO: Complete Workflow from PDF to Knowledge Graph

This guide walks you through the complete process of converting PDF documents to a queryable knowledge graph, from installation to extraction.

> [!tip]
> **Quick Setup**: If you want to get the system running quickly without processing documents from scratch, check out the [Quick Start](../README.md#quick-start) section in the main README. Pre-processed artifacts are available for download to skip the extraction steps.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Environment Setup](#environment-setup)
5. [Using Pre-processed Artifacts (Optional)](#using-pre-processed-artifacts-optional)
6. [Step 1: Parse PDFs to Markdown](#step-1-parse-pdfs-to-markdown)
7. [Step 2: Index Markdown to Vector Database (Optional)](#step-2-index-markdown-to-vector-database-optional)
8. [Step 3: Extract Knowledge Graph](#step-3-extract-knowledge-graph)
9. [Complete Workflow Example](#complete-workflow-example)
10. [Troubleshooting](#troubleshooting)
11. [Next Steps](#next-steps)
12. [Additional Resources](#additional-resources)
13. [Summary](#summary)

---

## Architecture Overview

This system transforms laboratory documents (PDFs) into a queryable knowledge graph. The architecture follows a pipeline approach: documents are parsed, structured entities and relationships are extracted using LLMs, and the resulting knowledge graph is stored in Neo4j for semantic querying.

The system operates in two main phases: **extraction** (building the knowledge graph) and **querying** (retrieving information). The extraction phase processes documents through parsing, entity extraction, and graph loading. The query phase uses semantic search over entity embeddings combined with graph traversal to provide context-aware answers.

### Knowledge Graph Query System Architecture

The core of the system focuses on the knowledge graph pipeline and query layer:

> [!note]
> **Visual Diagrams**: For detailed visual representations of the architecture, see:
> - [System Architecture](docs/diagrams/system_architecture.md) - Complete system overview
> - [Pipeline Flow](docs/diagrams/pipeline_flow.md) - Knowledge graph extraction pipeline
> - [Query Flow](docs/diagrams/query_flow.md) - Query processing flow


```ascii
KNOWLEDGE GRAPH PIPELINE
└─ Markdown → 01_extract.py → JSON → 02_load.py → Neo4j + Vector Store

QUERY FLOW
User Query → Semantic Search → Graph Traversal → LLM Synthesis → Answer
```

### Complete System Architecture

For reference, here's the complete system architecture including all components:

> [!note]
> **Visual Diagrams**: See [System Architecture](docs/diagrams/system_architecture.md) for a detailed visual representation. The ASCII diagram below is provided as an alternative text-based view.

```ascii
SYSTEM COMPONENTS

INPUT: PDF Files
  ↓
Parser (OpenRouter LLM) → Markdown Files
  ↓
Extraction (Bedrock LLM) → JSON Files
  ├─ Entities & Relationships
  ├─ Stored to Vector Store
  └─ Ready for Loading
  ↓
Loader (Neo4j) → Knowledge Graph
  ├─ Nodes (Entities)
  ├─ Edges (Relationships)
  └─ Vector Embeddings

QUERY LAYER
  ├─ kg_api_wrapper → Core KG Module
  ├─ Flask API → HTTP Endpoints
  ├─ Frontend (React) → Chat Interface
  └─ CLI Tools → Interactive Querying

EXTERNAL SERVICES
  ├─ AWS Bedrock (LLM + Embeddings)
  ├─ OpenRouter (PDF Parsing)
  └─ Neo4j (Graph Database)
```

The knowledge graph query system follows a three-step process: **semantic search** finds relevant entities using embeddings, **graph traversal** retrieves relationships and context from Neo4j, and **LLM** generates answers from the retrieved context. This approach combines the precision of structured graph data with the flexibility of semantic search and natural language generation.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **uv** package manager (Python's fast package installer)
- **OpenRouter API key** (for PDF parsing via LLM)
- **AWS credentials** configured (for Bedrock embeddings and LLM)
- **Neo4j server access** (running instance or Docker container)

> [!note]
> **OS Compatibility**: This solution has been tested on recent macOS and Debian-based Linux distributions. Windows support is not guaranteed.

> [!tip]
> **Pre-processed Artifacts**: If you want to skip the document processing steps, pre-processed artifacts (knowledge graph extractions and vector stores) are available for download. See the [Using Pre-processed Artifacts](#using-pre-processed-artifacts-optional) section below for details.

### Installing uv

If you don't have `uv` installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

---

## Installation

1. **Clone the repository** (if you haven't already):
```bash
git clone <repository-url>
cd ADLM-2025-development-v3
```

2. **Install dependencies using uv**:
```bash
uv sync
```

This will:
- Create a virtual environment automatically
- Install all dependencies from `pyproject.toml`
- Set up the project for development

3. **Activate the virtual environment** (if needed):
```bash
# uv automatically manages the environment, but you can activate it:
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

---

## Environment Setup

Create a `.env` file in the project root with the following variables:

```bash
# OpenRouter API (for PDF parsing)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# AWS Credentials (for Bedrock embeddings and LLM)
AWS_PROFILE=your_aws_profile_name
AWS_REGION=us-east-1

# Bedrock Model (optional, defaults shown)
BEDROCK_MODEL_ID=ai21.jamba-1-5-large-v1:0

# Neo4j Connection (for knowledge graph)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=labdocs_kg  # Optional: defaults to "neo4j" if not set
```

### Getting an OpenRouter API Key

1. Go to [https://openrouter.ai/](https://openrouter.ai/)
2. Sign up or log in
3. Navigate to **Keys** section
4. Create a new API key
5. Copy the key to your `.env` file

### Setting up AWS Credentials

You can use either:

**Option A: AWS Profile** (recommended)
```bash
aws configure --profile your_profile_name
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

### Setting up Neo4j with Docker

We'll use Docker to run Neo4j with APOC (Awesome Procedures on Cypher) plugin support.

**Prerequisites:**
- Docker installed and running
- Create directories for data persistence (optional but recommended):
  ```bash
  mkdir -p /workbench/data_neoj4
  mkdir -p /workbench/plugins_neoj4
  ```

**Run Neo4j container:**

```bash
docker run \
  -p 7474:7474 \
  -p 7687:7687 \
  -v /workbench/data_neoj4:/data \
  -v /workbench/plugins_neoj4:/plugins \
  --name neo4j-apoc \
  -e NEO4J_apoc_export_file_enabled=true \
  -e NEO4J_apoc_import_file_enabled=true \
  -e NEO4J_apoc_import_file_use__neo4j__config=true \
  -e NEO4JLABS_PLUGINS='["apoc"]' \
  neo4j:latest
```

**What this command does:**
- `-p 7474:7474` - Exposes Neo4j Browser on port 7474 (HTTP)
- `-p 7687:7687` - Exposes Neo4j Bolt protocol on port 7687 (for connections)
- `-v /workbench/data_neoj4:/data` - Persists database data to host directory
- `-v /workbench/plugins_neoj4:/plugins` - Persists plugins to host directory
- `--name neo4j-apoc` - Names the container for easy reference
- `-e NEO4J_apoc_*` - Enables APOC file import/export features
- `-e NEO4JLABS_PLUGINS='["apoc"]'` - Installs APOC plugin automatically
- `neo4j:latest` - Uses the latest Neo4j image

**First-time setup:**

1. **Start the container** (command above)
2. **Access Neo4j Browser** at [http://localhost:7474](http://localhost:7474)
3. **Set initial password** when prompted (default username: `neo4j`)
4. **Update your `.env` file** with the password:
   ```bash
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password_here
   ```

**Managing the container:**

```bash
# Stop the container
docker stop neo4j-apoc

# Start the container (if already created)
docker start neo4j-apoc

# Remove the container (data persists in volumes)
docker rm neo4j-apoc

# View logs
docker logs neo4j-apoc

# Restart the container
docker restart neo4j-apoc
```

**Note:** The data volumes (`/workbench/data_neoj4` and `/workbench/plugins_neoj4`) persist your database even if you remove the container. To start fresh, remove these directories.

---

## Using Pre-processed Artifacts (Optional)

If you want to skip the document processing steps and get straight to querying, pre-processed artifacts are available for download. These artifacts contain parsed markdown documents, extracted knowledge graph data, and vector embeddings, allowing you to load the system directly into Neo4j without running the full extraction pipeline.

### Available Artifacts

The following pre-processed artifacts are available as compressed archives:

1. **Parsed Markdown Documents** (`parsed_labdocs.md.tar.gz`):
   - Contains 7,681 parsed markdown files from PDF documents
   - Includes both FDA documents (4,457 files) and Procedures documents (3,224 files)
   - Preserves directory structure: `data/parsed/LabDocs/`
   - Size: ~22 MB compressed
   - These are the output of Step 1 (PDF parsing)

2. **Knowledge Graph Extractions** (`graphdb_extractions.tar.gz`):
   - Contains 352 JSON files with extracted entities and relationships
   - Output of `01_extract.py` (Step 3a)
   - Ready for loading into Neo4j
   - Size: ~492 KB compressed
   - Directory structure: `graphdb_unified/extractions/`

3. **Entity Vector Store** (`graphdb_vectorstore.tar.gz`):
   - Contains vector embeddings for semantic search over entities
   - Created by `02_load.py` (Step 3b)
   - Required for the knowledge graph query system
   - Size: ~28 MB compressed
   - Directory structure: `graphdb_vectorstore/`

### Download and Installation

1. **Download the artifacts** from the [Pre-processed Artifacts section](../README.md#pre-processed-artifacts-optional) in the main README

2. **Extract the downloaded archives** to your project root directory:
   ```bash
   # Extract parsed markdown files
   tar -xzf parsed_labdocs.md.tar.gz
   
   # Extract knowledge graph extractions
   tar -xzf graphdb_extractions.tar.gz
   
   # Extract vector store
   tar -xzf graphdb_vectorstore.tar.gz
   ```

3. **Verify the directory structure**:
   ```
   ./data/parsed/LabDocs/          # Parsed markdown files
   ./graphdb_unified/extractions/  # KG extraction JSON files
   ./graphdb_vectorstore/          # Vector store files
   ```

4. **Ensure your Neo4j database is running and configured** (see [Environment Setup](#environment-setup))

5. **Load the artifacts into Neo4j**:
   ```bash
   uv run python pipelines/kg_pipeline/02_load.py --extraction-dir ./graphdb_unified/extractions
   ```
   
   > [!note]
   > The `02_load.py` script will automatically use the existing vector store if it's already present in `./graphdb_vectorstore/`. If you're loading fresh, it will create a new vector store.

> [!note]
> These artifacts are optional. You can still process documents from scratch by following the steps below. The pre-processed artifacts are provided to save time during evaluation and testing.

---

## Step 1: Parse PDFs to Markdown

### Overview

The PDF parsing pipeline converts raw PDF documents into structured Markdown format using large language models (LLMs) accessed through the OpenRouter API. This step is the foundational preprocessing stage that enables subsequent knowledge extraction and indexing operations. The parser employs a vision-capable LLM to interpret PDF content, preserving document structure while converting it to a machine-readable format suitable for downstream processing.

### Methodology

**PDF Processing Architecture**: The parser utilizes an OpenAI-compatible client interface to communicate with OpenRouter, which provides access to multiple LLM providers. PDFs are encoded as base64 data URLs and transmitted to the LLM via a file attachment API, enabling the model to process both text-based and image-based PDF content directly.

**LLM Configuration**: The default model is `google/gemini-2.5-flash`, a vision-capable multimodal model optimized for document understanding tasks. Alternative models can be specified via command-line arguments, including `z-ai/glm-4.5-air:free` and other OpenRouter-compatible models. The parser uses deterministic sampling parameters (temperature=0.0, top_p=1.0) to ensure consistent output across document processing runs.

**PDF Engine Selection**: Three PDF processing engines are available:
- **native**: Default engine using the LLM's built-in vision capabilities for PDF interpretation
- **pdf-text**: Text extraction engine for text-based PDFs
- **mistral-ocr**: OCR-based engine for scanned documents requiring optical character recognition

**Prompt Engineering**: The parsing process employs a structured prompt template (`regulatory_lab_parser.j2`) that instructs the LLM to:
1. Maintain original document structure (headers, sub-headers, lists, tables)
2. Remove extraneous elements (page numbers, repeating headers/footers, form numbers)
3. Convert images and charts to descriptive text placeholders
4. Preserve mathematical notation using LaTeX syntax
5. Extract domain-specific keywords (for FDA documents: 510(k) numbers, device names, regulatory classifications, analytical performance metrics, etc.)

**Metadata Tracking**: Each parsed document includes a standardized metadata header containing:
- Generation timestamp
- Source PDF filename
- LLM model identifier
- Provider information (OpenRouter)
- PDF engine used
- Sampling parameters (temperature, top_p)

**Incremental Processing**: The parser implements skip logic to avoid reprocessing existing files. It checks for corresponding `.md` files in the output directory and only processes PDFs that lack corresponding markdown outputs, enabling efficient batch processing and resumption of interrupted processing runs.

**Rate Limiting**: To comply with API rate limits and prevent service interruptions, the parser implements configurable delays between requests (default: 50 seconds). This ensures stable processing of large document collections while respecting provider constraints.

### Basic Usage

```bash
uv run python -m labdocs.parser.pdf_parser \
  --input-folder /path/to/your/pdfs \
  --output-folder /path/to/output/markdown
```

### Example

```bash
# Process all PDFs in a folder
uv run python -m labdocs.parser.pdf_parser \
  --input-folder ./data/raw/LabDocs \
  --output-folder ./data/parsed/LabDocs
```

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input-folder` | **Required.** Path to folder containing PDF files | - |
| `--output-folder` | **Required.** Path where Markdown files will be saved | - |
| `--model` | LLM model name | `google/gemini-2.5-flash` |
| `--api-key` | OpenRouter API key (or set `OPENROUTER_API_KEY` env var) | - |
| `--base-url` | API base URL | `https://openrouter.ai/api/v1` |
| `--prompt-template` | Prompt template name (without .j2 extension) | `regulatory_lab_parser` |
| `--max-docs` | Maximum documents to process (0 = unlimited) | `0` |
| `--pdf-engine` | PDF engine: `native`, `pdf-text`, or `mistral-ocr` | `native` |
| `--rate-limit-delay` | Delay between requests in seconds | `50` |

### Advanced Examples

**Process first 5 PDFs with a custom model:**
```bash
uv run python -m labdocs.parser.pdf_parser \
  --input-folder ./data/raw/LabDocs \
  --output-folder ./data/parsed/LabDocs \
  --model z-ai/glm-4.5-air:free \
  --max-docs 5
```

**Use OCR engine for scanned PDFs:**
```bash
uv run python -m labdocs.parser.pdf_parser \
  --input-folder ./data/raw/LabDocs \
  --output-folder ./data/parsed/LabDocs \
  --pdf-engine mistral-ocr
```

**Process with rate limiting (for API quotas):**
```bash
uv run python -m labdocs.parser.pdf_parser \
  --input-folder ./data/raw/LabDocs \
  --output-folder ./data/parsed/LabDocs \
  --rate-limit-delay 60
```

### Output

The parser generates structured Markdown files with the following characteristics:
- **File naming**: Each PDF is converted to a corresponding `.md` file with the same base name
- **Structure preservation**: Document hierarchy (headers, sections, lists) is maintained
- **Metadata headers**: Standardized metadata block at the top of each file
- **Content cleaning**: Removal of page numbers, headers, footers, and other non-content elements
- **Image handling**: Visual content replaced with descriptive text placeholders
- **Mathematical notation**: Equations preserved in LaTeX format

Example output structure:
```
./data/parsed/LabDocs/
├── FDA/
│   ├── Clinical Chemistry/
│   │   ├── K220916.md
│   │   └── K220421.md
│   └── Pathology/
│       └── K192259.md
└── Procedures/
    ├── 1_25-DIHYDROXYVITAMIN_D_SERUM.md
    └── 1_3-BETA-D-GLUCAN_FUNGITELL_SERUM.md
```

## Extract Knowledge Graph


The knowledge graph extraction is a **two-step process**:
1. **Extract** entities and relationships from markdown documents to JSON files
2. **Load** JSON files into Neo4j graph database (creates its own entity vector store for KG querying)

### Step 1: Extract Entities and Relationships

Extract entities and relationships from markdown documents using Bedrock LLM.

```bash
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/markdown \
  --output-dir ./graphdb_extractions
```

**Note on command syntax:** 
- `labdocs.parser.pdf_parser` uses `-m` because it's part of an installed Python package (`src/labdocs/`)
- `pipelines/kg_pipeline/01_extract.py` uses a file path because it's a standalone script (not an installed package)
- Both work with `uv run`, but the syntax differs based on whether it's a package module or a script file

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input-folder` | **Required.** Directory containing markdown documents | - |
| `--output-dir` | **Required.** Output directory for JSON extraction files | - |
| `--max-docs` | Limit number of documents to process (0 = all) | `0` |

### Example: Extract from Markdown Files

```bash
# Extract all documents
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/markdown \
  --output-dir ./graphdb_extractions

# Extract first 10 documents (for testing)
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/markdown \
  --output-dir ./graphdb_extractions \
  --max-docs 10
```

### Output

The extraction creates JSON files (one per document):
```
./graphdb_extractions/
├── document1.json
├── document2.json
└── document3.json
```

Each JSON file contains:
- Extracted entities with types and properties
- Relationships between entities
- Source text references

### Load into Neo4j

Load extracted JSON files into Neo4j graph database with entity deduplication.

```bash
uv run python pipelines/kg_pipeline/02_load.py \
  --extraction-dir ./graphdb_extractions
```

### Features

- **Entity deduplication**: Automatically merges similar entities (similarity threshold: 0.85)
- **Relationship creation**: Creates edges between entities in Neo4j
- **Database isolation**: Uses database specified in `NEO4J_DATABASE` env var (or default `neo4j`)

### Output

**Neo4j Database:**
- Entities as nodes (with types and properties)
- Relationships as edges (with source text)
- Metadata preserved for traceability

---

## Complete Workflow Example

Here's a complete example from start to finish:

```bash
# 1. Install dependencies
uv sync

# 2. Set up environment variables
# (Create .env file with API keys and credentials)

# 2a. Start Neo4j Docker container (if not already running)
docker start neo4j-apoc || docker run \
  -p 7474:7474 -p 7687:7687 \
  -v /workbench/data_neoj4:/data \
  -v /workbench/plugins_neoj4:/plugins \
  --name neo4j-apoc \
  -e NEO4J_apoc_export_file_enabled=true \
  -e NEO4J_apoc_import_file_enabled=true \
  -e NEO4J_apoc_import_file_use__neo4j__config=true \
  -e NEO4JLABS_PLUGINS='["apoc"]' \
  neo4j:latest

# 3. Parse PDFs to Markdown
uv run python -m labdocs.parser.pdf_parser \
  --input-folder ./data/pdfs \
  --output-folder ./data/parsed/markdown \
  --max-docs 10

# 4. (Optional) Index Markdown to Vector Database for RAG querying
# Skip this if you only want knowledge graph extraction
uv run python -m labdocs.indexer \
  --input-folder ./data/parsed/markdown \
  --persist-dir ./vectordb

# 5a. Extract entities and relationships (reads markdown files directly)
uv run python pipelines/kg_pipeline/01_extract.py \
  --input-folder ./data/parsed/markdown \
  --output-dir ./graphdb_extractions

# 5b. Load into Neo4j
uv run python pipelines/kg_pipeline/02_load.py \
  --extraction-dir ./graphdb_extractions
```

---

## Additional Resources

- **PDF Parser README**: `src/labdocs/parser/README.md`
- **[Extraction Guide](./EXTRACTION_GUIDE.md)** - Unified ontology extraction process
- **[Unified Graph Guide](./UNIFIED_GRAPH_GUIDE.md)** - Graph queries and exploration
- **[Quick Start](./QUICK_START.md)** - Quick reference guide

---
