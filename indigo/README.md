# ADLM 2025 Data Challenge RAG Application

A contextual retrieval application with BM25+Vector Search retrieval for processing and analyzing laboratory documentation from the ADLM 2025 Data Challenge.

## Features

- **PDF Text Extraction**: Automatically extracts text content from PDF documents while preserving directory structure
- **Document Processing**: Processes PDF files in the LabDocs directory
- **Contextual Retrieval**: Combines BM25 search and Vector search with contextual retrieval with rank fusion and reranking for maximum retrieval accuracy.
- **Cloud Hosting**: Data and retrieval functions are hosted in AWS

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Memory**: At least 4GB RAM (8GB+ recommended for large document processing)
- **Storage**: At least 4GB free space for LabDocs and extracted content
- **Internet**: Required for initial LabDocs download

### Required System Tools
- **curl**: For downloading LabDocs from Zenodo
- **unzip**: For extracting the downloaded archive

## Installation by Platform

NOTE: This build process has only been tested on Mac.

### macOS

#### Using Homebrew
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and required tools
brew install python@3.11 curl

# Install Poetry
curl -sSL https://install.python-poetry.org | python3.11 -
```

Add poetry to your PATH

### Linux

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and required tools
sudo apt install python3.11 python3.11-venv python3-pip curl unzip

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### Windows

#### Using Windows Package Manager
```powershell
# Install Python 3.11+ from Microsoft Store or python.org
# Install curl (usually pre-installed on Windows 10/11)
# Install 7-Zip for unzip functionality

# Install Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Add Poetry to PATH (restart terminal after this)
$env:PATH += ";$env:APPDATA\Python\Scripts"
```

## Project Setup

### 1. Clone the Repository
```bash
git clone https://github.com/jonmontg/ADLM-2025-Data-Challenge.git
cd ADLM-2025-Data-Challenge/indigo
```

### 2. Install Dependencies
```bash
# Install all dependencies (including development tools)
poetry install --with dev

# Or install only production dependencies
poetry install
```

## Building and Running the Application

### Data Directory Structure
The application uses a centralized `app/data` directory to organize all data files:

- **`app/data/LabDocs/`**: Contains the downloaded PDF documents from Zenodo
- **`app/data/extracted_docs/`**: Contains the extracted text files from PDFs

This structure keeps your data organized and separate from the application code.

### Automatic Build
The application will automatically download and set up the required LabDocs:

```bash
# This will automatically download LabDocs if not present
poetry run build
```

### Running the Application
```bash
# Run the main RAG application
poetry run main
```

## License

This project is licensed under the MIT License.
