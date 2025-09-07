# ADLM 2025 Data Challenge RAG Application

A contextual retrieval application with BM25+Vector Search retrieval for processing and analyzing laboratory documentation from the ADLM 2025 Data Challenge.

## Features

- **PDF Text Extraction**: Automatically extracts text content from PDF documents while preserving directory structure
- **Document Processing**: Recursively processes PDF files in the LabDocs directory
- **RAG Framework**: Foundation for implementing retrieval-augmented generation capabilities
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Memory**: At least 4GB RAM (8GB+ recommended for large document processing)
- **Storage**: At least 2GB free space for LabDocs and extracted content
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

## Development

### Setting Up Development Environment
```bash
# Install with development dependencies
poetry install --with dev

### Development Commands
```bash
# Format code
poetry run black .

# Lint code
poetry run flake8

# Type checking
poetry run mypy .

# Run pre-commit hooks
poetry run pre-commit run --all-files
```

### Adding Dependencies
```bash
# Add production dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name
```

## Troubleshooting

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python --version

# If wrong version, use pyenv or update PATH
pyenv local 3.11.6
```

#### Poetry Installation Issues
```bash
# Reinstall Poetry
curl -sSL https://install.python-poetry.org | python3 - --uninstall
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH manually
export PATH="$HOME/.local/bin:$PATH"
```

#### Missing System Tools
**macOS**: Install via Homebrew: `brew install curl`
**Windows**: Install 7-Zip and ensure curl is available
**Linux**: Install via package manager: `sudo apt install curl unzip`
```

### Platform-Specific Notes

#### macOS
- Python 3.11+ is recommended (avoid system Python 2.7)
- Homebrew is the preferred package manager
- Xcode Command Line Tools may be required: `xcode-select --install`

#### Windows
- Use PowerShell or Command Prompt (not Git Bash for some operations)
- Ensure Python is added to PATH during installation
- 7-Zip provides unzip functionality
- curl is available in Windows 10/11 by default

#### Linux
- Use your distribution's package manager for system tools
- Python 3.11+ from package manager or pyenv
- Ensure curl and unzip are available

## Project Structure
```
indigo/
├── app/
│   ├── data/              # Data directory for documents and extracted content
│   │   ├── LabDocs/       # Input PDF documents (auto-downloaded)
│   │   └── extracted_docs/ # Extracted text files
│   ├── dbs/               # Database and cache directories
│   │   └── tf_idf/        # TF-IDF search cache files
│   ├── lib/
│   │   ├── extract_pdf.py # PDF extraction utilities
│   │   ├── data_source.py # Data download and management utilities
│   │   ├── tf_idf.py      # TF-IDF search implementation
│   │   └── search.py      # Search interface wrapper
│   ├── main.py            # Main application entry point
│   └── build.py           # Build and setup script
├── tests/                 # Test files
├── pyproject.toml         # Poetry configuration
├── .flake8                # Flake8 linting configuration
└── README.md              # This file
```

**Note**: The `app/data/` directory is automatically created and populated when you run the application. It contains:
- **LabDocs**: Downloaded PDF documents from Zenodo
- **extracted_docs**: Text files extracted from the PDFs

**Cache Directory**: The `app/dbs/tf_idf/` directory stores TF-IDF search indices for fast document retrieval. This cache is automatically managed and only rebuilt when documents change.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests and linting: `poetry run pytest && poetry run black . && poetry run flake8`
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License.
