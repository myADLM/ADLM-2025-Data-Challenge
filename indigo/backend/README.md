# ADLM 2025 Data Challenge RAG Application

A contextual retrieval application with BM25+Vector Search retrieval for processing and analyzing laboratory documentation from the ADLM 2025 Data Challenge.

## Features

- **PDF Text Extraction**: Automatically extracts text content from PDF documents while preserving directory structure
- **Document Processing**: Processes PDF files in the LabDocs directory with bronze/silver/gold data pipeline
- **Dual Search Capabilities**: 
  - **BM25 Search**: Fast keyword-based search using rank-bm25
  - **Vector Search**: Semantic search using OpenAI embeddings with FAISS indexing
- **Parallel Processing**: Optimized embedding generation with CPU-based thread pool sizing
- **Caching**: Intelligent caching of embeddings to avoid redundant API calls
- **Cloud Integration**: Data and retrieval functions are hosted in AWS S3

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Memory**: At least 8GB RAM (16GB+ recommended for vector database generation)
- **Storage**: At least 10GB free space for LabDocs, extracted content, and vector database
- **Internet**: Required for initial LabDocs download and OpenAI API calls

### Required System Tools
- **curl**: For downloading LabDocs from Zenodo
- **unzip**: For extracting the downloaded archive

### API Requirements
- **OpenAI API Key**: Required for vector search functionality (costs ~$7 to build the vector database)

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

Add poetry to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

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

### 3. Set Up Environment Variables
```bash
# Required for vector search functionality
export OPENAI_API_KEY="your-openai-api-key-here"

# Optional: Set custom cache directory (default: app/database/embeddings)
export EMBEDDING_CACHE_DIR="/path/to/custom/cache"
```

## Building and Running the Application

### Data Directory Structure
The application uses a centralized `app/database` directory to organize all data files:

- **`app/database/originals/`**: Contains the downloaded PDF documents from Zenodo
- **`app/database/medallions/`**: Contains processed data in bronze/silver/gold format
  - `bronze.parquet`: Raw extracted text from PDFs
  - `silver.parquet`: Chunked and annotated text
  - `gold.parquet`: Vector embeddings (generated during build)
- **`app/database/embeddings/`**: Cached OpenAI embeddings for faster rebuilds

### Build Options

#### Option 1: Build with Pre-compiled Database (Recommended)
If you have access to a pre-compiled database, simply place it in the `app/database/` directory and skip the build process.

#### Option 2: Build from Scratch with OpenAI API
**⚠️ Cost Warning: This will cost approximately $7 in OpenAI API credits**

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Build the complete database including vector embeddings
poetry run build
```

#### Option 3: Build without Vector Search (BM25 only)
```bash
# Build without vector search (no API key required)
poetry run build --no-vectors
```

### Build Process Details

The build process follows a bronze/silver/gold data pipeline:

1. **Bronze Layer**: Downloads and extracts text from PDF documents
2. **Silver Layer**: Chunks text and adds contextual annotations
3. **Gold Layer**: Generates vector embeddings using OpenAI API
4. **Indexing**: Creates FAISS index for fast vector similarity search

### Running the Application

#### Interactive Search Interface
```bash
# Run the main RAG application with interactive CLI
poetry run main
```

#### Available Commands in the CLI:
- **Search Query**: Enter any text to search documents
- **`quit`**: Exit the application
- **`help`**: Show available commands
- **`clear`**: Clear the screen
- **`count`**: Show document count
- **`most_common_terms`**: Show most common terms in the TF-IDF index

#### Programmatic Usage
```python
from app.src.search.search import Search
from app.src.search.vector_search import VectorSearch

# BM25 search only
search = Search("app/database/originals")

# Vector search (requires OpenAI API key)
vector_search = VectorSearch(
    documents=documents,
    embedder="openai-text-embedding-3-small",
    embedding_cache="app/database/embeddings"
)
```

## Configuration

### Embedding Models
The application supports multiple OpenAI embedding models:

- **`openai-text-embedding-3-small`**: Fast and cost-effective (recommended)
- **`openai-text-embedding-3-large`**: Higher quality but more expensive

### Performance Tuning
- **Thread Pool Size**: Automatically determined based on CPU cores (max 8)
- **Cache Management**: Embeddings are cached locally to avoid redundant API calls
- **Memory Usage**: Vector search requires significant RAM for large document sets

## Troubleshooting

### Common Issues

1. **"No extracted documents found"**
   - Run `poetry run build` first to extract PDF content

2. **"OpenAI API key not found"**
   - Set the `OPENAI_API_KEY` environment variable
   - Ensure you have sufficient API credits

3. **"Out of memory" during vector generation**
   - Reduce the number of documents processed at once
   - Increase available RAM or use a machine with more memory

4. **"Rate limit exceeded"**
   - OpenAI API has rate limits; the application includes retry logic
   - Consider using a different embedding model or reducing batch size

### Performance Tips

- **Use SSD storage** for faster I/O operations
- **Allocate sufficient RAM** (16GB+ recommended for full dataset)
- **Enable caching** to avoid regenerating embeddings
- **Use parallel processing** (automatically enabled based on CPU cores)

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black .
poetry run flake8
```

### Type Checking
```bash
poetry run mypy .
```

## Cost Estimation

### OpenAI API Costs (Approximate)
- **Text Embedding 3 Small**: ~$0.02 per 1M tokens
- **Text Embedding 3 Large**: ~$0.13 per 1M tokens
- **Estimated total cost for full dataset**: ~$7 USD

### Storage Requirements
- **Raw PDFs**: ~2GB
- **Extracted text**: ~500MB
- **Vector embeddings**: ~1-2GB
- **Total storage**: ~4-5GB

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the build logs for specific error messages