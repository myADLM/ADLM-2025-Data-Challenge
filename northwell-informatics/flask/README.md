# Flask SOP Query Application

A web-based interface for querying Standard Operating Procedures (SOPs) using AI-enhanced responses.

## Features

- 🔬 **SOP File Selection**: Choose from available JSON extraction files
- 🤖 **LLM-Enhanced Queries**: AI-powered responses with context awareness
- 🌐 **External Access**: Accessible from any device on the network
- 🔒 **HTTPS Support**: Secure connections with self-signed certificates
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🔧 **Debug Mode**: View query processing details
- 📁 **Static Files**: Serve custom assets from www/ directory
- 🪟 **Cross-Platform**: Supports Windows (waitress), Linux/macOS (gunicorn)

## Prerequisites

- **Git**: For cloning the repository
- **Python 3.8+**: Required for running the application
- **Internet Connection**: For downloading dependencies

## Installation & Setup

### Step 1: Clone the Repository

Choose a suitable location on your system and clone the repository:

```bash
# Navigate to your desired directory (e.g., Desktop, Documents, or development folder)
cd ~/Desktop  # or cd C:\Users\YourName\Desktop on Windows

# Clone the repository
git clone https://github.com/NWH-Laboratory-Informatics/aldm_challenge.git

# Navigate to the project directory
cd aldm_challenge/prod
```

**Important**: Make sure to clone to a location where you have write permissions and sufficient disk space.

### Step 2: Set Up the Environment

The service script will automatically detect your operating system and set up the appropriate environment:

#### Linux/macOS Setup
```bash
# First-time setup (creates virtual environment and installs dependencies)
./service.sh setup
```

#### Windows Setup
You have two options for Windows:

**Option 1: Using Git Bash (Recommended)**
```bash
# Use Git Bash terminal and run the same commands as Linux
./service.sh setup
```

**Option 2: Using Windows Batch File**
```cmd
# Use Command Prompt or PowerShell  
service.bat setup
```

**Note**: If you encounter permission issues on Windows, run the command from an elevated Command Prompt or PowerShell.

## Running the Service

### Method 1: Using the Service Script (Recommended)

The service script automatically detects your operating system and uses the appropriate WSGI server:
- **Linux/macOS**: Uses gunicorn for production-grade performance
- **Windows**: Uses waitress for Windows compatibility

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

**Option 1: Git Bash (use same commands as Linux/macOS above)**

**Option 2: Windows Batch File**
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

### Method 2: Platform-Specific Manual Setup

#### Linux/macOS Manual Setup
```bash
cd aldm_challenge/prod/flask

# Activate virtual environment
source ../.venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Set Python path
export PYTHONPATH="../modules:../:$PYTHONPATH"

# Start with gunicorn
gunicorn --config gunicorn.conf.py app:app
```

#### Windows Manual Setup
```bash
cd aldm_challenge\prod\flask

# Activate virtual environment
..\.venv\Scripts\activate

# Install requirements (including waitress)
pip install -r requirements.txt

# Set Python path (PowerShell)
$env:PYTHONPATH="../modules;../;$env:PYTHONPATH"

# Or in Command Prompt
set PYTHONPATH=../modules;../;%PYTHONPATH%

# Start with waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

## Accessing the Application

Once the service is running, you can access it through your web browser:

### Local Access
- **Primary URL**: http://localhost:5000
- **Alternative**: http://127.0.0.1:5000

### Network Access (from other devices)
- **Find your IP**: Use `ipconfig` (Windows) or `ifconfig` (Linux/macOS) to find your local IP
- **Access URL**: http://[your-ip-address]:5000
- **Example**: http://192.168.1.100:5000

### Service Management Commands

#### Linux/macOS or Git Bash (Windows)
```bash
# Check if service is running
./service.sh status

# View real-time application logs
./service.sh logs

# Restart service (useful after making changes)
./service.sh restart

# Stop the service
./service.sh stop
```

#### Windows Command Prompt/PowerShell
```cmd  
# Check if service is running
service.bat status

# View application logs
service.bat logs

# Restart service (useful after making changes)
service.bat restart

# Stop the service
service.bat stop
```

## Platform-Specific Notes

### Windows Users
- The service automatically uses **waitress** (Windows-compatible WSGI server)
- Run commands in **Command Prompt** or **PowerShell** as Administrator if needed
- **Git Bash** is recommended for running shell scripts
- **Path separators**: The script handles both `/` and `\` automatically

### Linux/macOS Users  
- The service automatically uses **gunicorn** (production-grade WSGI server)
- Standard terminal or shell environment
- May need `chmod +x service.sh` to make the script executable

## Configuration Options

The Flask app supports several command-line options when run directly:

```bash
python app.py --help

# Common options:
python app.py --host 0.0.0.0 --port 8080        # Custom host/port
python app.py --no-https                        # Use HTTP instead of HTTPS  
python app.py --debug                           # Enable debug mode
```

**Note**: When using the service script, these options are pre-configured for optimal performance.

## File Structure

```
flask/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── start.sh              # Startup script
├── README.md             # This file
├── templates/            # Jinja2 templates
│   └── index.html        # Main web interface
└── www/                  # Static files (CSS, JS, images)
    └── style.css         # Additional styles
```

## Usage

1. **Start the Application**: Use `./start.sh` or run `python app.py`
2. **Select SOP File**: Choose a JSON file from the dropdown
3. **Load File**: Click "Load SOP File" to initialize the query system
4. **Ask Questions**: Enter your question and click "Ask Question"
5. **View Results**: See AI-enhanced responses with optional debug info

## Example Questions

- "What is the reference range for A1C?"
- "What specimen is required for this test?"
- "What equipment is needed?"
- "What are the procedural steps?"
- "What quality control measures are required?"

## Technical Details

### Dependencies
- **Flask**: Web framework
- **Requests**: HTTP client for API calls
- **OpenAI**: For LLM integration
- **PyOpenSSL**: For HTTPS certificates

### System Requirements
- Python 3.8+
- Virtual environment with project dependencies
- Access to Northwell LLM API (configured in app.py)

### API Endpoints
- `GET /`: Main interface
- `POST /load_file`: Load SOP file
- `POST /query`: Process queries
- `GET /status`: System status
- `GET /static/<path>`: Static file serving

## Security Considerations

- Uses self-signed certificates for HTTPS
- API keys are hardcoded (change for production)
- No authentication required (internal use)
- Accepts connections from any IP (0.0.0.0)

## Troubleshooting

### Common Issues

1. **"Virtual environment not found"**
   - Run `./service.sh setup` first to create the environment
   - Ensure you're in the correct directory (`aldm_challenge/prod`)
   - Check that Python 3.8+ is installed

2. **"Import errors" or "Module not found"**
   - Check that `PYTHONPATH` includes the modules directory
   - Ensure all dependencies are installed with `pip install -r requirements.txt`
   - Try restarting the service: `./service.sh restart`

3. **"No JSON files found"**
   - Run the preprocessing notebooks to generate JSON files
   - Check that files exist in appropriate directories
   - Verify the data extraction process completed successfully

4. **"Permission denied" (Windows)**
   - Run Command Prompt or PowerShell as Administrator
   - Ensure Python is added to your system PATH
   - Check that Windows execution policies allow script execution

5. **"Port already in use"**
   - Stop the existing service: `./service.sh stop`
   - Check for other applications using port 5000
   - Use Task Manager (Windows) or Activity Monitor (macOS) to find processes using the port

6. **"Service won't start" or crashes immediately**
   - Check the logs: `./service.sh logs`
   - Verify all dependencies are installed
   - Ensure the virtual environment is properly activated

### Platform-Specific Troubleshooting

#### Windows Issues
- **PowerShell Execution Policy**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Python not found**: Ensure Python is installed and added to PATH
- **Git Bash recommended**: Use Git Bash for better shell script compatibility
- **Antivirus interference**: Temporarily disable real-time scanning if needed

#### Linux/macOS Issues
- **Script permissions**: Run `chmod +x service.sh` to make executable
- **Python version**: Ensure `python` command points to Python 3.8+
- **Virtual environment module**: Install with `sudo apt install python3-venv` (Ubuntu) or `brew install python` (macOS)

### Debug Mode

Enable debug mode for development:
```bash
python app.py --debug
```

This provides:
- Detailed error messages
- Auto-reload on code changes  
- Flask debug toolbar
- Enhanced logging output

### Getting Help

If you continue experiencing issues:

1. **Check the logs**: `./service.sh logs` for real-time error information
2. **Verify setup**: Ensure all installation steps were completed
3. **System requirements**: Confirm Python 3.8+, Git, and sufficient disk space
4. **Clean reinstall**: Delete `.venv` directory and run `./service.sh setup` again

## Development

### Adding Features

1. **New Routes**: Add to `app.py`
2. **Frontend Changes**: Edit `templates/index.html`
3. **Static Assets**: Add to `www/` directory
4. **Styles**: Edit `www/style.css`

### API Integration

The app integrates with:
- **ExtractionQuerySystem**: Basic search functionality
- **LLMEnhancedQuerySystem**: AI-powered responses
- **Northwell LLM API**: External AI service

## Quick Reference

### First Time Setup
```bash
# 1. Clone repository
git clone https://github.com/NWH-Laboratory-Informatics/aldm_challenge.git
cd aldm_challenge/prod

# 2. Setup environment
./service.sh setup          # Linux/macOS/Git Bash
service.bat setup           # Windows Command Prompt

# 3. Start service  
./service.sh start          # Linux/macOS/Git Bash
service.bat start           # Windows Command Prompt

# 4. Access application
# Open browser: http://localhost:5000
```

### Daily Usage
```bash
# Check status
./service.sh status         # Linux/macOS/Git Bash  
service.bat status          # Windows Command Prompt

# View logs
./service.sh logs           # Linux/macOS/Git Bash
service.bat logs            # Windows Command Prompt

# Stop service
./service.sh stop           # Linux/macOS/Git Bash
service.bat stop            # Windows Command Prompt
```

### System Requirements Summary
- **Git**: For repository cloning
- **Python 3.8+**: Runtime environment
- **Internet**: For dependency downloads
- **Disk Space**: ~500MB for dependencies
- **RAM**: ~512MB minimum for service
- **Ports**: 5000 (default, configurable)

## License

Internal use for Northwell Health laboratory SOP analysis.
