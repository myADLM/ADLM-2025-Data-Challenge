# Laboratory Documents Querying System

Welcome to the Laboratory Documents Querying System! This system provides an AI-powered interface for querying Standard Operating Procedures (SOPs) and FDA 510(k) documents using advanced Large Language Model (LLM) technology.

## Prerequisites

- **Git**: For cloning the repository
- **Python 3.8+**: Required for running the application
- **Internet Connection**: For downloading dependencies

## Installation & Setup

### Step 1: Clone the Repository

Choose a suitable location on your system and clone the repository:

```bash
# Navigate to your desired directory (e.g., Desktop, Documents, or home directory)
cd ~/  # or cd C:\Users\YourName\Desktop on Windows

# Clone the repository
git clone https://github.com/NWH-Laboratory-Informatics/aldm_challenge.git

# Navigate to the project directory
cd aldm_challenge
```

### Step 2: Configure API Provider (Required)

**⚠️ IMPORTANT**: You **MUST** configure your OpenAI API key before running the application. The system will not work without proper API configuration.

**Background**: This system was developed using Northwell's internal LLM API, but the Northwell API key is not included in this public release. **You must configure OpenAI to use this system.**

#### Setting Up OpenAI API

**Getting an OpenAI API Key:**
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account (or create one)
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-`)
5. **Important**: Keep this key secure and never share it publicly

**Configuration Options (choose one):**

**Option 1: Set API Key as Environment Variable (Recommended)**
This method is more secure as it keeps your API key out of code files:

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# Windows Command Prompt
set OPENAI_API_KEY=sk-your-openai-api-key-here

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-openai-api-key-here"
```

**Option 2: Set API Key in Configuration File**
1. **Edit the configuration file**:
   ```bash
   # Open the config file in a text editor
   nano modules/config.py
   # or use your preferred editor: vim, code, gedit, etc.
   ```

2. **Add your OpenAI API Key**:
   Find the `OPENAI_CONFIG` section and update the `api_key` field:
   ```python
   OPENAI_CONFIG = {
       "api_key": "sk-your-openai-api-key-here",  # Replace with your actual API key
       "base_url": "https://api.openai.com/v1/chat/completions",
       "default_model": "gpt-4o-mini",
       # ... rest of config
   }
   ```

3. **Change the default provider** (required):
   To make OpenAI the default provider, change:
   ```python
   DEFAULT_PROVIDER: Literal["northwell", "openai"] = "openai"
   ```

### Step 3: Set Up the Environment

The service script will automatically detect your operating system and set up the appropriate environment:

#### Linux/macOS Setup
**Pip Upgrade (Recommended)**: Before running setup, upgrade pip to avoid dependency issues:
```bash
python -m pip install --upgrade pip
```

```bash
# First-time setup (creates virtual environment and installs dependencies)
./service.sh setup
```

#### Windows Setup
**Pip Upgrade (Recommended)**: Before running setup, upgrade pip to avoid dependency issues:
```cmd
python -m pip install --upgrade pip
```

```cmd
# Use Command Prompt or PowerShell  
service.bat setup
```

**Note**: If you encounter permission issues on Windows, run the command from an elevated Command Prompt or PowerShell.

The setup process will automatically:
- Create a Python virtual environment
- Install all required dependencies (including waitress for Windows, gunicorn for Linux/macOS)
- Prepare the system for running

### Step 4: Start the Flask Application

#### Linux/macOS Commands
```bash
# Start the service
./service.sh start

# Check service status  
./service.sh status

# View real-time logs
./service.sh logs

# Stop the service
./service.sh stop

# Restart the service
./service.sh restart
```

#### Windows Commands
```cmd
# Start the service
service.bat start

# Check service status
service.bat status

# View logs
service.bat logs

# Stop the service
service.bat stop

# Restart the service  
service.bat restart
```

**⚠️ Note**: If you haven't configured your API key yet, go back to Step 2. The application requires a valid OpenAI API key to function.

This method is more secure as it keeps your API key out of code files:

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# Windows Command Prompt
set OPENAI_API_KEY=sk-your-openai-api-key-here

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-openai-api-key-here"
```

**Getting an OpenAI API Key:**

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account (or create one)
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-`)
5. **Important**: Keep this key secure and never share it publicly

**Testing Your Configuration:**

After setting up your API key, test the configuration:

```bash
# Test the configuration
cd modules
python config.py

# This will show:
# - Current default provider
# - API key status for both providers
# - Available models
# - Connection test results
```

#### Cost Considerations

**OpenAI API Costs:**
- OpenAI charges per token (input + output)
- Costs vary by model (GPT-4 > GPT-3.5-turbo)
- Monitor usage at [https://platform.openai.com/usage](https://platform.openai.com/usage)
- Recommended to start with `gpt-4o-mini` for cost-effective testing

**Development Note:**
- This system was originally developed using Northwell's internal LLM API
- The Northwell API provides access to multiple model providers but requires internal authentication
- For public release, OpenAI integration provides the most accessible option

### Step 5: Access the Web Interface
Once started, open your web browser and navigate to:

#### Local Access
- **Primary URL**: http://localhost:5000
- **Alternative**: http://127.0.0.1:5000

#### Network Access (from other devices)
- **Find your IP**: Use `ipconfig` (Windows) or `ifconfig` (Linux/macOS) to find your local IP
- **Access URL**: http://[your-ip-address]:5000
- **Example**: http://192.168.1.100:5000

## Platform-Specific Notes

### Windows Users
- The service automatically uses **waitress** (Windows-compatible WSGI server)
- Run commands in **Command Prompt** or **PowerShell** as Administrator if needed
- Use the **service.bat** file for all service management
- **Path separators**: The script handles both `/` and `\` automatically

### Linux/macOS Users  
- The service automatically uses **gunicorn** (production-grade WSGI server)
- Standard terminal or shell environment
- May need `chmod +x service.sh` to make the script executable

## System Architecture

### Frontend (Web Interface)
The **Laboratory Documents Querying System** provides a clean, intuitive web interface built with Flask that allows users to:

- **Choose Query Type**: Select between SOP Query or FDA Query modes
- **Ask Questions**: Submit natural language questions about laboratory procedures or FDA documentation
- **View Responses**: Get comprehensive, AI-generated answers with relevant document excerpts
- **Compare Systems**: Query both SOP and FDA systems simultaneously for comparison
- **Conversation History**: Maintain context across multiple questions in a session

**Key Features:**
- Real-time query processing
- Conversation history tracking
- System status monitoring
- Responsive design for desktop and mobile use

### Backend (AI Query Processing)

The backend consists of two main Python modules that connect to Large Language Models:

#### **SOPQuery.py**
- Processes questions about **Standard Operating Procedures (SOPs)**
- Handles laboratory protocols, safety procedures, equipment instructions
- Uses multi-step LLM processing to enhance queries and provide comprehensive answers
- Searches through processed SOP document summaries

#### **FDAQuery.py** 
- Processes questions about **FDA 510(k) submissions and clearances**
- Handles medical device approvals, regulatory requirements, device specifications
- Uses advanced query enhancement to understand FDA-specific terminology
- Searches through processed FDA document summaries

Both modules use a unified `LLM` class that supports multiple providers:

#### **Supported LLM Providers:**

**OpenAI API (Required for Public Use):**
- Direct integration with OpenAI's platform
- Models: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo, O1 series
- Requires user-provided API key
- Pay-per-use pricing model

**Northwell API (Development Only):**
- Internal enterprise LLM platform used during development
- Access to multiple models: Claude, GPT, Gemini, O1/O3 series
- Not available in public release (requires internal Northwell authentication)
- Code remains for reference and potential internal deployments

The system automatically handles provider-specific API formats and authentication, providing a consistent interface regardless of which LLM provider is configured.

### Document Preprocessing Pipeline

We preprocessed the document store using the following pipeline:

#### **SOP Processing** (`preprocess/SOP_to_es.ipynb`)
1. **PDF to Text Conversion**: Extracted text content from SOP PDF documents
2. **Document Parsing**: Identified key sections like test names, specimen types, equipment requirements
3. **JSON Summary Generation**: Created structured summaries with fields like:
   - Test Name and Purpose
   - Specimen Type and Container requirements  
   - Required Equipment
   - Procedural steps and safety measures
4. **Storage**: Saved processed summaries as JSON files in `LabDocs/es1/sop/`

#### **FDA Processing** (`preprocess/FDA_summary_to_es.ipynb`)
1. **PDF to Markdown Conversion**: Used MinerU to generate clean markdown representations of FDA 510(k) submission PDFs
2. **Document Extraction**: Processed the markdown-formatted FDA documents for structured content analysis
3. **Content Analysis**: Extracted device information, regulatory details, predicate devices from the markdown files
4. **JSON Summary Generation**: Created structured summaries containing:
   - Device name and manufacturer
   - Approved indications and contraindications
   - Technical specifications
   - Regulatory pathway and clearance details
5. **Indexing**: Organized summaries for efficient retrieval during queries

#### **Summary Usage**
The generated JSON summaries serve as a knowledge base that enables:
- **Fast Document Retrieval**: Quickly find relevant documents for each question
- **Contextual Understanding**: AI can understand document content without processing entire PDFs
- **Accurate Responses**: Provides specific, relevant information rather than generic answers
- **Source Attribution**: Links responses back to specific source documents

## Technical Details

- **Framework**: Flask web application with Gunicorn/Waitress for production deployment
- **AI Models**: Unified LLM interface supporting multiple providers (Northwell API, OpenAI)
- **Configuration**: Flexible config system with environment variable support (`modules/config.py`)
- **Document Storage**: JSON-based document summaries for fast retrieval
- **Logging**: Comprehensive logging system for monitoring and debugging
- **Session Management**: Conversation history and context preservation
- **Background Service**: Runs as a daemon process with PID management
- **Security**: API keys managed via environment variables or secure config files

## Directory Structure

```
├── service.sh             # Service management script (project root)
├── flask/                 # Web application
│   ├── app.py            # Main Flask application
│   └── templates/        # HTML templates
├── query/                # Backend query processors
│   ├── SOPQuery.py       # SOP document querying
│   └── FDAQuery.py       # FDA document querying
├── preprocess/           # Document preprocessing
│   ├── SOP_to_es.ipynb   # SOP processing pipeline
│   └── FDA_summary_to_es.ipynb # FDA processing pipeline
└── LabDocs/             # Processed document storage
    ├── es1/sop/         # SOP JSON summaries
    └── FDA/             # FDA document summaries
```

## Troubleshooting

### Common Issues

1. **"Virtual environment not found"**
   - Run `./service.sh setup` or `service.bat setup` first to create the environment
   - Ensure you're in the correct directory (`aldm_challenge/prod`)
   - Check that Python 3.8+ is installed

2. **"Import errors" or "Module not found"**
   - Ensure all dependencies are installed with the setup command
   - Try restarting the service: `./service.sh restart` or `service.bat restart`

3. **"Permission denied" (Windows)**
   - Run Command Prompt or PowerShell as Administrator
   - Ensure Python is added to your system PATH
   - Check that Windows execution policies allow script execution: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

4. **"Port already in use"**
   - Stop the existing service: `./service.sh stop` or `service.bat stop`
   - Check for other applications using port 5000

5. **"Service won't start" or crashes immediately**
   - Check the logs: `./service.sh logs` or `service.bat logs`
   - Verify all dependencies are installed
   - Ensure the virtual environment is properly activated

6. **"API key required" or "Authentication failed"**
   - **This is expected if you haven't configured OpenAI yet** - the system requires API configuration
   - **OpenAI setup**: Ensure your API key is set correctly
     - Verify the key starts with `sk-` and is complete
     - Check if the key is valid at [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
     - Ensure you have sufficient credits/usage quota
   - **Environment variable**: Make sure `OPENAI_API_KEY` is set in your shell
     ```bash
     echo $OPENAI_API_KEY  # Linux/macOS/Git Bash
     echo %OPENAI_API_KEY%  # Windows Command Prompt
     ```
   - **Configuration file**: Check that `modules/config.py` has the correct API key and default provider set to "openai"
   - **Test configuration**: Run `python modules/config.py` to test API connections

7. **"Model not available" or model-related errors**
   - Check available models for your provider in `modules/config.py`
   - Verify the model name matches exactly (case-sensitive)
   - For OpenAI: Ensure your account has access to the requested model
   - Switch to a different model if needed (e.g., `gpt-4o-mini` instead of `gpt-4o`)

### Platform-Specific Troubleshooting

#### Windows Issues
- **Python not found**: Ensure Python is installed and added to PATH
- **Batch file execution**: Use Command Prompt or PowerShell for running service.bat
- **Antivirus interference**: Temporarily disable real-time scanning if needed

#### Linux/macOS Issues
- **Script permissions**: Run `chmod +x service.sh` to make executable
- **Python version**: Ensure `python` command points to Python 3.8+
- **Virtual environment module**: Install with `sudo apt install python3-venv` (Ubuntu) or `brew install python` (macOS)

### Getting Help

If you continue experiencing issues:

1. **Check the logs**: `./service.sh logs` or `service.bat logs` for real-time error information
2. **Verify setup**: Ensure all installation steps were completed
3. **System requirements**: Confirm Python 3.8+, Git, and sufficient disk space
4. **Clean reinstall**: Delete `.venv` directory and run setup again

## Quick Reference

### First Time Setup
```bash
# 1. Clone repository
git clone https://github.com/NWH-Laboratory-Informatics/aldm_challenge.git
cd aldm_challenge/prod

# 2. Setup environment
./service.sh setup          # Linux/macOS
service.bat setup           # Windows

# 3. Configure OpenAI API (REQUIRED)
export OPENAI_API_KEY="sk-your-key-here"  # Set your API key
# Edit modules/config.py to set DEFAULT_PROVIDER = "openai"

# 4. Start service  
./service.sh start          # Linux/macOS
service.bat start           # Windows

# 5. Access application
# Open browser: http://localhost:5000
```

### Daily Usage
```bash
# Check status
./service.sh status         # Linux/macOS  
service.bat status          # Windows

# View logs
./service.sh logs           # Linux/macOS
service.bat logs            # Windows

# Stop service
./service.sh stop           # Linux/macOS
service.bat stop            # Windows
```

### API Configuration
```bash
# Set OpenAI API key (choose one method)
export OPENAI_API_KEY="sk-your-key-here"        # Linux/macOS
set OPENAI_API_KEY=sk-your-key-here             # Windows Command Prompt
$env:OPENAI_API_KEY="sk-your-key-here"          # Windows PowerShell

# Test API configuration
cd modules
python config.py

# Edit configuration file
nano modules/config.py      # Linux/macOS
notepad modules\config.py   # Windows
code modules/config.py      # VS Code (any platform)
```

### System Requirements Summary
- **Git**: For repository cloning
- **Python**: Runtime environment
- **Internet**: For dependency downloads
- **Ports**: 5000 (default, configurable)

## Need Help?

- Check service status: `./service.sh status` (Linux/macOS) or `service.bat status` (Windows)
- View logs: `./service.sh logs` (Linux/macOS) or `service.bat logs` (Windows)
- Restart if needed: `./service.sh restart` (Linux/macOS) or `service.bat restart` (Windows)
