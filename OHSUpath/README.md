# OHSUpath Reader

A Retrieval-Augmented Generation (RAG) system for querying medical documentation, developed by Team OHSUpath for the ADLM 2025 Data Challenge.

## Table of Contents

- [Overview](#overview)
  - [Highlights](#highlights)
  - [Key Features](#key-features)
- [About ADLM 2025 Data Challenge](#about-adlm-2025-data-challenge)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Quick Command Reference](#quick-command-reference)
- [Architecture](#architecture)
  - [System Architecture](#system-architecture)
  - [How RAG Pipeline Works](#how-rag-pipeline-works)
  - [How Web Application Works](#how-web-application-works)
- [Configuration](#configuration)
- [Privacy & Security](#privacy--security)
- [Citation and Document Access](#citation-and-document-access)
- [Hardware Requirements](#hardware-requirements)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)
- [License](#license)
- [Team](#team)

## Overview

**OHSUpath Reader** is an AI-powered tool that helps users search and retrieve information from medical documentation. It uses open-source language models and runs entirely without Public Network access to protect Protected Health Information (PHI).

### Highlights

- **Pre-Processed Indexing**: Fast queries with multi-core parallel processing, incremental updates, and crash-safe atomic writes
- **Private Network Ready**: Run on internal networks without Public Network access
- **Hybrid Retrieval**: Combines keyword search (BM25S) and semantic search (FAISS) with n-gram reranking
- **Multi-Platform**: Streamlit (single-user) and web interface (multi-user with auth)
- **Mobile Ready**: Responsive design for desktop, tablet, and mobile
- **Source Citations**: All answers include page numbers with click-to-view PDF access

See [CHANGELOG.md](CHANGELOG.md) for version history.

### Key Features

- **Offline Operation**: Runs locally without needing public internet connectivity to ensure PHI security
- **Configurable Models**: Choose any Ollama-compatible LLM and embedding model via `config.yaml`
- **Multi-Interface Support**: Available as both Streamlit app for single users and modern web interface for team collaboration
- **Intelligent Search**: Uses hybrid retrieval combining keyword search and semantic search with n-gram reranking for accurate results
- **Citation Support**: Provides source references with page numbers for every answer
  - **Click to View**: Click citation bubbles to view source documents in a new browser tab
  - **Auto-scroll to Page**: Automatically jumps to the cited page in the PDF
  - **Browser PDF Viewer**: Uses the browser's native PDF viewer for simple document viewing
  - **No Embedded Viewers**: Clean, straightforward file access without complex in-page PDF rendering
- **Collaborative Features**: Share conversations with team members (web interface)
- **Modular Architecture**: Fully configurable RAG pipeline and network server with swappable components

## About ADLM 2025 Data Challenge

This project was developed by **Team OHSUpath** for the Association for Diagnostics & Laboratory Medicine (ADLM) 2025 Data Challenge. The challenge focuses on creating innovative solutions for medical documentation analysis while maintaining strict privacy and security standards for Protected Health Information (PHI).

**Key Design Goals:**
- Complete no Public Network access operation to protect sensitive medical data
- User-friendly interface accessible to medical professionals without technical expertise
- Accurate information retrieval with source citation for verification
- Scalable architecture supporting both individual and team use cases

## Prerequisites

Before installation, ensure you have:

- **Operating System**: Linux (Ubuntu 20.04+ recommended) or Windows with WSL2
  - Windows native support available on branch `1-use-GCR-pipeline` (version 0.2.0) with limited features
- **Hardware**: See [Hardware Requirements](#hardware-requirements) section
- **Disk Space**: At least 30GB free (50GB+ recommended for GPU models)
- **Public Network Access**: Required only for initial setup to download dependencies and models

## Quick Start

### Windows Users

> **Note**: For full functionality (hybrid retrieval, web hosting, etc.), use Linux. Windows users should use branch `1-use-GCR-pipeline` (version 0.2.0).

1. Double-click `Windows_Click_Me_To_Setup_The_Computer.bat` and follow steps 1-6
2. Double-click `Windows_Click_Me_To_Run_The_App.bat` to start the application

If setup fails, check the log files and retry.

### Linux Users (Recommended)

**Initial Setup** (required for both options below):

```bash
# 1. Clone the repository
git clone https://github.com/lzc2046/ADLM-2025-Data-Challenge.git
cd OHSUpath

# 2. Run automated setup
make setup-machine

# 3. Add your PDF files to the data folder
# cp your-files/*.pdf data/
# only pdfs will be processed, other files such as zip will not be processed. Also, please only delete pdf in this directory when you know these are not included otherwise those removed pdfs will also be removed from database.
```

#### Option A: Single User (Streamlit)

For personal use or testing:

```bash
# Start Streamlit admin console
make start-admin
```

Open http://localhost:8501 in your browser. Wait for the progress bar (top-left) to show "Completed", then start asking questions.

#### Option B: Multi-User Web Application

For team collaboration:

**Step 1: Initial Setup with Streamlit**

```bash
make start-admin
```

In Streamlit (http://localhost:8501):

1. **Wait for indexing**: Progress bar shows "Completed"
2. **Test the system**: Ask a question to verify citations appear
3. **Create user accounts**: Go to "Users" tab and create accounts for your team

**Step 2: Start Web Server**

```bash
# Stop Streamlit
make stop-admin

# Start web services
make start-server
```

Access at http://localhost:4000 and login with created accounts.

**Services Running:**
- FastAPI backend (port 8000)
- Node.js gateway (port 3000)
- Next.js frontend (port 4000)

## Installation

### Automated Setup

The `make setup-machine` command handles all installation automatically:

**What Gets Installed:**
- **Python 3.11+** with virtual environment
- **Node.js 20+** for gateway and web interface
- **Ollama** for LLM inference
- **Python packages**: FastAPI, Streamlit, langchain, faiss-cpu, sentence-transformers, PyMuPDF
- **Node.js packages**: Express (gateway), Next.js (frontend)
- **Default AI Models**: deepseek-r1-8b-int8 (LLM), all-MiniLM-L6-v2 (embeddings)

**Using Different Models:**

```bash
# Pull desired model
ollama pull qwen2.5

# Edit config.yaml and change llm.model to "qwen2.5"
```

### Environment Configuration

**Local Development:**
```bash
make update-local-env
```

**Production/Server Deployment:**
```bash
make update-server-env DOMAIN=https://your-domain.com
```

## Usage

### Streamlit Interface (Admin Console)

```bash
make start-admin
```

This launches the Streamlit interface at http://localhost:8501

To stop:
```bash
make stop-admin
```

### Web Interface (Multi-User)

```bash
# Start all services (FastAPI backend, Node.js gateway, Next.js frontend)
make start-server
```

Access the web UI at http://localhost:4000

Services running:
- **FastAPI Backend** (port 8000): RAG service and database
- **Node.js Gateway** (port 3000): Authentication and API routing
- **Next.js Frontend** (port 4000): Web interface

#### Other Server Commands

```bash
# Stop all services
make stop-server

# Restart all services
make restart-server

# Check server status
make show-server-status

# View server logs
make show-server-logs
```

## Quick Command Reference

| Task | Command |
|------|---------|
| **First Time Setup** | `make setup-machine` |
| **Configure Environment** | `make update-local-env` |
| **Start Web Interface** | `make start-server` |
| **Stop Web Interface** | `make stop-server` |
| **Start Streamlit (Admin)** | `make start-admin` |
| **Stop Streamlit** | `make stop-admin` |
| **Check Status** | `make show-server-status` |
| **View Logs** | `make show-server-logs` |
| **See All Commands** | `make` |

## Architecture

### Default Models

The system ships with these default models (configurable in `config.yaml`):

- **LLM**: deepseek-r1-8b-int8 (8B parameter reasoning model)
- **Embeddings**: all-MiniLM-L6-v2 (384-dimensional sentence transformer)

**Alternative Models:**
You can switch to other models by editing `config.yaml`:
- **LLM**: Any Ollama-compatible model (qwen, llama3, mistral, etc.)
- **Embeddings**: Instructor-XL (768-dimensional, higher precision) or other sentence-transformers

**To change models:**
1. Edit `config.yaml`
2. Update `llm.model` for the language model
3. Update `embedding.model_name` for the embeddings model
4. Restart the application: `make restart-server`

### Components

- **app.py**: Streamlit frontend for quick testing and demo
- **net/**: Modern web application stack
  - **api/**: FastAPI backend with RAG service integration
  - **gateway/**: Node.js API gateway for authentication and routing
  - **web/**: Next.js frontend with real-time updates
- **rag/**: Modular RAG pipeline
  - PDF loaders with parallel processing
  - Hybrid retrieval (keyword-based + semantic)
  - Vector and keyword indexes (FAISS + BM25S)
  - Character n-gram reranking
- **config.yaml**: User-facing configuration
- **config.py**: Developer defaults

### System Architecture

```
                    ┌─────────────────────────────────┐
                    │   TWO DEPLOYMENT OPTIONS:       │
                    └─────────────────────────────────┘

     ┌──────────────────────────┐            ┌───────────────────────────┐
     │  Option A: Streamlit     │            │  Option B: Web App        │
     │  (Single User)           │            │  (Multi-User)             │
     │  (Admin for Multi-User)  │            │                           │
     │  ┌────────────────────┐  │            │  ┌────────────────────┐   │
     │  │ Streamlit UI       │  │            │  │ Next.js Frontend   │   │
     │  │ Port: 8501         │  │            │  │ Port: 4000         │   │
     │  │ (Direct import)    │  │            │  └─────────┬──────────┘   │
     │  └─────────┬──────────┘  │            │            │        ▲     │
     │            │             │            │            ▼        │     │
     │            │             │            │  ┌──────────────────┴─┐   │
     └────────────┼─────────────┘            │  │ Node.js Gateway    │   │
          ▲       │                          │  │ Port: 3000         │   │
          │       │                          │  │ • Authentication   │   │
          │       │                          │  │ • API Routing      │   │
          │       │                          │  └─────────┬──────────┘   │
          │       │                          │            │        ▲     │
          │       │                          │            ▼        │     │
          │       │                          │  ┌──────────────────┴─┐   │
          │       │                          │  │ FastAPI Backend    │   │
          │       │                          │  │ Port: 8000         │   │
          │       │                          │  │ • REST Endpoints   │   │
          │       │                          │  └─────────┬──────────┘   │
          │       │                          │            │        ▲     │
          │       │                          │            │        │     │
          │       │                          └────────────┼────────┼─────┘
          │       └─────────────────┬─────────────────────┘        │
          │                         │                              │
          │                         ▼                              │
          │       ┌────────────────────────────────────────┐       │
          │       │         RAG Pipeline Engine            │       │
          │       │  ┌──────────────────────────────────┐  │       │
          │       │  │  1. Query Processing             │  │       │
          │       │  └──────────────┬───────────────────┘  │       │
          │       │                 ▼                      │       │
          │       │  ┌──────────────────────────────────┐  │       │
          │       │  │  2. Hybrid Retrieval             │  │       │
          │       │  │     • BM25S (Keyword Search)     │  │       │
          │       │  │     • FAISS (Semantic Search)    │  │       │
          │       │  │     • N-gram Reranking           │  │       │
          │       │  └──────────────┬───────────────────┘  │       │
          │       │                 ▼                      │       │
          │       │  ┌──────────────────────────────────┐  │       │
          │       │  │  3. Document Retrieval           │  │       │
          │       │  │     Top-K relevant chunks        │  │       │
          │       │  └──────────────┬───────────────────┘  │       │
          │       │                 ▼                      │       │
          │       │  ┌──────────────────────────────────┐  │       │
          │       │  │  4. LLM Generation (Ollama)      │  │       │
          │       │  │     Model: deepseek-r1-8b-int8   │  │       │
          │       │  └──────────────┬───────────────────┘  │       │
          │       │                 ▼                      │       │
          │       │  ┌──────────────────────────────────┐  │       │
          │       │  │  5. Response Formatting          │  │       │
          │       │  │     Answer + Citations + Pages   │  │       │
          │       │  └──────────────┬───────────────────┘  │       │
          │       └─────────────────┼──────────────────────┘       │
          │                         │                              │
          │                         │                              │
          └─────────────────────────┴──────────────────────────────┘



                 ┌────────────────────────────────────────┐
                 │         Data Storage Layer             │
                 │  • PDF Documents (data/)               │
                 │  • FAISS Vector Index (.rag_store/)    │
                 │  • BM25S Keyword Index (.rag_store/)   │
                 │  • SQLite Database (users, chat)       │
                 └────────────────────────────────────────┘

```

### How RAG Pipeline Works

The RAG (Retrieval-Augmented Generation) pipeline processes user queries through five stages to provide accurate, cited answers:

**1. Document Indexing (One-time Setup)**
   - **PDF Loading**: Parallel processing of PDF documents from the `data/` folder
   - **Text Extraction**: PyMuPDF extracts text while preserving page numbers and structure
   - **Chunking**: Documents split into semantic chunks (default: 500 tokens with 100 token overlap)
   - **Embedding Generation**: Each chunk converted to 384-dimensional vectors using all-MiniLM-L6-v2
   - **Index Creation**:
     - FAISS vector index for semantic similarity search
     - BM25S keyword index for exact term matching
   - **Storage**: Indexes saved to `.rag_store/` for fast loading

**2. Query Processing**
   - User query normalized and prepared for retrieval
   - Query embedding generated using the same model (all-MiniLM-L6-v2)
   - Query analyzed for both semantic meaning and keywords

**3. Hybrid Retrieval**
   - **Keyword Search (BM25S)**: Finds documents matching query terms exactly
   - **Semantic Search (FAISS)**: Finds documents similar in meaning
   - **Fusion**: Results from both methods combined and deduplicated
   - **N-gram Reranking**: Character-level n-grams rescore results for better relevance
   - **Top-K Selection**: Best 12 chunks selected (configurable in `config.yaml`)

**4. Context Building**
   - Retrieved chunks formatted with source information
   - Page numbers and file names preserved for citations
   - Chunks combined into context prompt for LLM

**5. LLM Generation**
   - **Model**: deepseek-r1-8b-int8 (or configured model) via Ollama
   - **Prompt**: Includes context chunks + user query + instruction to cite sources
   - **Generation**: Model generates answer based on retrieved context
   - **Citation Extraction**: Page numbers and sources parsed from LLM response
   - **Response Formatting**: Answer + citations returned to user

**Why Hybrid Retrieval?**
- **Keyword search (BM25S)** catches exact medical terms, drug names, codes
- **Semantic search (FAISS)** understands meaning, handles synonyms and paraphrasing
- **N-gram reranking** improves precision by matching character patterns
- **Combined**: Better accuracy than either method alone

### How Web Application Works

The web application (`net/`) provides multi-user access with authentication and conversation management:

**1. Frontend Layer (Next.js - Port 4000)**
   - **Technology**: React with TypeScript, Next.js 14
   - **Features**:
     - Real-time chat interface with streaming responses
     - Citation bubbles that link to source documents
     - Conversation history and management
     - User authentication UI
   - **Communication**: Sends requests to Gateway via REST API

**2. Gateway Layer (Node.js - Port 3000)**
   - **Technology**: Express.js with TypeScript
   - **Responsibilities**:
     - **Authentication**: JWT-based session management
     - **Authorization**: Verifies user permissions for each request
     - **API Routing**: Forwards authenticated requests to FastAPI backend
     - **Security**: CORS handling, request validation
   - **Why Gateway?**: Separates auth logic from Python backend, enables future scaling

**3. Backend Layer (FastAPI - Port 8000)**
   - **Technology**: Python FastAPI framework
   - **Core Services**:
     - **Query Endpoint** (`/api/query`): Processes user questions through RAG pipeline
     - **Conversation API**: CRUD operations for conversation history
     - **User Management**: User creation, authentication (used by gateway)
     - **File Serving**: Secure PDF access with authentication checks
   - **Database**: SQLite for users and conversation storage
   - **RAG Integration**: Direct access to pipeline for query processing

**4. Data Flow Example**

User asks: *"What is the normal range for hemoglobin A1c?"*

```
1. User types question → Next.js frontend
2. Frontend → POST /api/query → Node.js Gateway
3. Gateway validates JWT → checks user session
4. Gateway → forwards to FastAPI → /api/query
5. FastAPI → RAG Pipeline processes query
   - Retrieves relevant chunks about HbA1c
   - LLM generates answer with citations
6. FastAPI → returns {answer, citations, pages}
7. Gateway → forwards response to Frontend
8. Frontend → displays answer with citation bubbles
9. User clicks citation → opens PDF at cited page
```

**Single-User Mode (Streamlit)**
- Streamlit app **directly imports** the RAG pipeline (Python import, no API calls)
- Bypasses FastAPI entirely - talks directly to `rag.pipeline.RagPipeline`
- Shares only the database models with FastAPI (for user/conversation storage)
- No authentication or gateway layer needed
- Simpler deployment for personal use
- Same RAG pipeline, just different access method

**Why This Architecture?**
- **Separation of Concerns**: Auth, API, and RAG logic separated
- **Scalability**: Can scale each layer independently
- **Security**: Authentication handled before reaching RAG system
- **Flexibility**: Easy to swap frontend or add new interfaces
- **Development**: Frontend and backend teams can work independently

## Configuration

All configuration is done through `config.yaml`. After making changes, restart the application.

### Common Configuration Tasks

**Change the LLM Model:**
```yaml
llm:
  model: "deepseek-r1-8b-int8"  # Change to any Ollama model
  # Examples: "qwen2.5", "llama3", "mistral", "gemma2"
```

**Change the Embedding Model:**
```yaml
embedding:
  model_name: "./models/all-MiniLM-L6-v2"
  embedding_dim: 384  # Must match your model's dimensions
  # For Instructor-XL: use "./models/InstructorXL" and embedding_dim: 768
```
*Note: Changing the embedding model requires rebuilding indexes. Delete `.rag_store/` and restart.*

**Adjust Retrieval Settings:**
```yaml
retrieval:
  mode: hybrid  # Options: dense, hybrid, sparse
  hybrid:
    final_k: 12  # Number of documents to retrieve
```

**Change Data Location:**
```yaml
paths:
  data_dir: "data"  # Path to your PDF documents
```

### All Configuration Options

- **Data paths**: Location of PDF documents and indexes
- **Model settings**: Which LLM and embedding models to use
- **Retrieval parameters**: Search mode, number of results, ranking weights
- **LLM settings**: Provider, model name, request timeouts, temperature
- **Performance**: Batch sizes, GPU usage, number of workers

See `config.yaml` for all available options and detailed comments.

## Privacy & Security

This system is designed with PHI protection in mind:

- **Local Execution**: All processing happens on-device, no core data leaves your machine
- **No Public Internet Required**: Works completely offline after initial setup
- **Secure Document Access**: All file downloads require authentication and are restricted to the configured data directory

## Citation and Document Access

The web interface displays citation bubbles for all AI responses. These citations reference the source documents used to generate the answer.

**Citation Bubble Behavior:**
- **Click**: Opens the source document in a new browser tab using the browser's built-in PDF viewer
- **Auto-scroll**: Automatically jumps to the cited page number when available
- **No Embedded Viewers**: The system does not include in-page PDF preview, thumbnails, or highlight overlays for simplicity

**File Viewing API:**
- Endpoint: `GET /api/files/{file_path}/download`
- Serves files with `Content-Disposition: inline` (displays in browser tab)
- Requires authentication for all file access
- Files are restricted to the configured data directory

This approach ensures:
- Simple, predictable document access
- No client-side PDF rendering dependencies
- Better performance for large documents

## Hardware Requirements

### Minimum Requirements

**CPU-only (Search and retrieval only, no LLM generation):**
- 16GB RAM
- 8-core modern CPU
- 30GB disk space

**With GPU (Full functionality):**
- 16-core modern CPU
- 16GB+ RAM, 16GB RAM might cause the program crashes unexpectly.
- NVIDIA GPU with 8GB+ VRAM, 12GB+ recommended.
- 50GB disk space
- CUDA-compatible GPU (Recommend CUDA 12.8)

### Recommended Configuration
- 24+ core CPU
- 32GB+ RAM
- NVIDIA GPU with 12GB+ VRAM
- 50GB+ SSD storage
- Ubuntu 20.04+ or similar Linux distribution

### Reference System

**Development and testing were performed on:**
- **Laptop**: Dell Precision 7770
- **CPU**: Intel i7-12850HX (16 cores)
- **RAM**: 32GB DDR5
- **GPU**: NVIDIA RTX A3000 (12GB VRAM)
- **Storage**: 512GB NVMe SSD
- **OS**: Ubuntu 22.04 LTS (via WSL2)

## Development

### Project Structure

```
OHSUpath/
├── app.py               # Streamlit application
├── config.yaml          # User configuration
├── config.py            # Default configuration
├── rag/                 # RAG pipeline modules
│   ├── pipeline.py      # Main pipeline orchestrator
│   ├── retriever.py     # Hybrid retrieval logic
│   ├── loaders/         # PDF loaders
│   ├── chunkers/        # Text chunking
│   ├── embedders/       # Embedding generation
│   ├── vectorstores/    # Vector and keyword indexes
│   └── rerankers/       # Result reranking
├── net/                 # Web application
│   ├── api/             # FastAPI backend
│   ├── gateway/         # Node.js gateway
│   └── web/             # Next.js frontend
├── data/                # PDF documents
└── bootstrap/           # Setup scripts
```

### Available Make Commands

View all available commands:
```bash
make
```

Key commands:
- `make setup-machine` - Initial setup (run once)
- `make update-local-env` - Setup environment for local development
- `make start-server` - Start web interface
- `make stop-server` - Stop web interface
- `make restart-server` - Restart web interface
- `make start-admin` - Start Streamlit admin console
- `make stop-admin` - Stop Streamlit admin console
- `make show-server-status` - Check if services are running
- `make show-server-logs` - View server logs
- `make rotate-jwt` - Rotate JWT secret (forces user re-login)
- `make rotate-api-key` - Rotate internal API key

### Running Tests

```bash
# Test Streamlit interface
make start-admin

# Test web interface
make start-server
```

### Building Indexes

The system automatically builds indexes on first run. To rebuild:

```bash
# Delete existing indexes
rm -rf .rag_store/

# Restart the application (indexes will rebuild)
```
Or you can choose to go to streamlit, click on the factory reset on the bottom of the control panel, then restart the services.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and feature updates.

## Troubleshooting

### Common Issues

**"Module not found" or import errors:**
```bash
# Ensure you're in the virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Ollama connection errors:**
```bash
# Check if Ollama is running
ollama list

# If not installed, setup will install it
make setup-machine

# Manually start Ollama (if needed)
ollama serve
```

**Port already in use:**
```bash
# Check what's using the port
sudo lsof -i :8000  # or :3000, :4000

# Kill the process or stop the server
make stop-server
```

**Slow indexing or queries:**
- Check available RAM and disk space
- For large document sets (>1000 PDFs), consider:
  - Using CPU-only mode if GPU memory is limited
  - Adjusting batch sizes in `config.yaml`
  - Increasing system swap space

**Citations not appearing:**
- Ensure PDFs are properly indexed (progress bar shows "Completed")
- Rebuild indexes: `rm -rf .rag_store/ && make restart-server`
- Check `config.yaml` retrieval settings

**Web interface login issues:**
- Verify users were created in Streamlit admin console
- Check `net/gateway/.env` for correct API endpoints
- Review gateway logs: `tail -f net/logs/gateway.log`

### Log Files

- **Web Interface**: `net/logs/` directory
  - `fastapi.log` - Backend API logs
  - `gateway.log` - Authentication and routing logs
- **Streamlit**: Terminal output when running `make start-admin`

## Known Limitations

- **Windows Support**: Limited features on native Windows (use WSL2 or Linux for full functionality)
- **Document Types**: Currently supports PDF files only
- **Language**: Optimized for English medical documentation
- **Concurrent Users**: Multi-user mode has not been stress-tested for large teams (>20 simultaneous users)
- **Model Size**: Default model requires 8GB+ GPU VRAM for optimal performance

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

### Why AGPL-3.0?

This project uses [PyMuPDF](https://pymupdf.readthedocs.io/), which is licensed under AGPL-3.0. As a result, this entire project must also be distributed under AGPL-3.0 to comply with PyMuPDF's license terms.

### Key Points

- **Free to Use**: You can use, modify, and distribute this software freely
- **Share Alike**: Any modifications or derivative works must also be licensed under AGPL-3.0
- **Network Use**: If you run a modified version on a server (network use), you must make the source code available to users
- **No Warranty**: This software is provided as-is, without warranty of any kind

### Full License

See the [LICENSE](LICENSE) file for the complete AGPL-3.0 license text, or visit:
https://www.gnu.org/licenses/agpl-3.0.en.html

### Project Context

This project was developed by Team OHSUpath for the ADLM 2025 Data Challenge.

## Team

Team OHSUpath. Contact Email: luzh@ohsu.edu

---

For technical questions, please refer to the project documentation or contact the development team.
