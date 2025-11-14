#!/bin/bash

# Background Gunicorn Service Script
# =================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLASK_DIR="$SCRIPT_DIR/flask"
cd "$FLASK_DIR"

# Configuration
SERVICE_NAME="flask-sop-query"
PID_FILE="$FLASK_DIR/gunicorn_flask_sop.pid"
LOG_FILE="$FLASK_DIR/gunicorn_flask_sop.log"
VENV_PATH="$SCRIPT_DIR/.venv"

# Functions
start_service() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "🟢 Service is already running (PID: $(cat $PID_FILE))"
        return 0
    fi
    
    echo "🚀 Starting $SERVICE_NAME as background service..."
    
    # Check and create virtual environment if needed
    if [ ! -d "$VENV_PATH" ]; then
        echo "📦 Virtual environment not found. Please run './service.sh setup' first to create the environment."
        exit 1
    fi
    
    # Activate virtual environment (handle both Unix and Windows)
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
    elif [ -f "$VENV_PATH/Scripts/activate" ]; then
        source "$VENV_PATH/Scripts/activate"
    else
        echo "❌ Could not find virtual environment activation script"
        exit 1
    fi
    
    # Install requirements
    echo "📋 Installing/updating requirements..."
    pip install -q -r requirements.txt
    
    # Set Python path
    export PYTHONPATH="$SCRIPT_DIR/modules:$SCRIPT_DIR:$PYTHONPATH"
    
    # Ensure log file exists and is writable
    touch "$LOG_FILE" 2>/dev/null || LOG_FILE="$FLASK_DIR/gunicorn_flask_sop.log"
    
    # Detect platform and use appropriate WSGI server
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]] || command -v waitress-serve &> /dev/null && ! command -v gunicorn &> /dev/null; then
        echo "🪟 Windows detected, using waitress..."
        # Start waitress in background
        nohup waitress-serve --host=0.0.0.0 --port=5000 app:app > "$LOG_FILE" 2>&1 &
    else
        echo "🐧 Unix-like system detected, using gunicorn..."
        # Start Gunicorn in background
        nohup gunicorn --config gunicorn.conf.py app:app > "$LOG_FILE" 2>&1 &
    fi
    
    # Save PID
    echo $! > "$PID_FILE"
    
    echo "✅ Service started successfully!"
    echo "📱 Access: http://localhost:5000"
    echo "🌐 Network Access: http://[your-ip]:5000"
    echo "📝 Logs: $LOG_FILE"
    echo "🔢 PID: $(cat $PID_FILE)"
}

stop_service() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ PID file not found. Service may not be running."
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "🛑 Stopping $SERVICE_NAME (PID: $PID)..."
        kill "$PID"
        
        # Wait for process to stop
        sleep 2
        
        if kill -0 "$PID" 2>/dev/null; then
            echo "⚠️  Process still running, force killing..."
            kill -9 "$PID"
        fi
        
        rm -f "$PID_FILE"
        echo "✅ Service stopped successfully!"
    else
        echo "❌ Process not running (PID: $PID)"
        rm -f "$PID_FILE"
    fi
}

restart_service() {
    stop_service
    sleep 1
    start_service
}

status_service() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        PID=$(cat "$PID_FILE")
        
        # Detect which server is likely running
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
            SERVER_TYPE="waitress"
            PLATFORM_ICON="🪟"
        else
            SERVER_TYPE="gunicorn"
            PLATFORM_ICON="�"
        fi
        
        echo "$PLATFORM_ICON Service is running (PID: $PID) using $SERVER_TYPE"
        echo "📱 Local Access: http://localhost:5000"
        echo "🌐 Network Access: http://[your-ip]:5000"
        echo "📝 Logs: $LOG_FILE"
        
        # Show recent log entries
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo "📋 Recent log entries:"
            tail -n 5 "$LOG_FILE"
        fi
    else
        echo "🔴 Service is not running"
    fi
}

show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo "📝 Showing logs ($LOG_FILE):"
        echo "=================="
        tail -f "$LOG_FILE"
    else
        echo "❌ Log file not found: $LOG_FILE"
    fi
}

setup_environment() {
    echo "🔧 Setting up environment for $SERVICE_NAME..."
    
    # Check if python is available and is Python 3
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed or not in PATH"
        echo "   On Windows: Install Python from https://python.org or Microsoft Store"
        echo "   On Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-venv python3-pip"
        echo "   On CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "   On macOS: brew install python3"
        exit 1
    fi
    
    # Check if this python is Python 3
    PYTHON_VERSION=$(python -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo "0")
    if [ "$PYTHON_VERSION" != "3" ]; then
        echo "❌ Python 3 is required but Python $PYTHON_VERSION was found"
        echo "   Please ensure 'python' command points to Python 3"
        exit 1
    fi
    
    echo "✅ Using Python command: python"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_PATH" ]; then
        echo "📦 Creating virtual environment at $VENV_PATH..."
        python -m venv "$VENV_PATH"
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create virtual environment"
            echo "   Make sure you have venv module installed:"
            echo "   On Windows: Should be included with Python installation"
            echo "   On Ubuntu/Debian: sudo apt install python3-venv"
            exit 1
        fi
        echo "✅ Virtual environment created successfully!"
    else
        echo "✅ Virtual environment already exists at $VENV_PATH"
    fi
    
    # Activate virtual environment (handle both Unix and Windows)
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
    elif [ -f "$VENV_PATH/Scripts/activate" ]; then
        source "$VENV_PATH/Scripts/activate"
    else
        echo "❌ Could not find virtual environment activation script"
        exit 1
    fi
    
    # Upgrade pip
    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip -q
    
    # Install requirements
    echo "📋 Installing requirements..."
    pip install -r requirements.txt
    
    # Platform-specific information
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        echo "🪟 Windows environment detected"
        echo "   Using waitress as WSGI server (Windows compatible)"
    else
        echo "🐧 Unix-like environment detected"
        echo "   Using gunicorn as WSGI server (production-grade)"
    fi
    
    echo "✅ Environment setup complete!"
    echo "📝 You can now run: ./service.sh start"
}

# Main script logic
case "$1" in
    setup)
        setup_environment
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {setup|start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  setup   - Set up virtual environment and install dependencies"
        echo "  start   - Start the Flask SOP Query service in background"
        echo "  stop    - Stop the running service"
        echo "  restart - Restart the service"
        echo "  status  - Check if service is running"
        echo "  logs    - Show real-time logs"
        echo ""
        echo "First-time setup:"
        echo "  $0 setup    # Set up environment (run this first)"
        echo "  $0 start    # Start service"
        echo ""
        echo "Regular usage:"
        echo "  $0 status   # Check status"
        echo "  $0 logs     # View logs"
        echo "  $0 stop     # Stop service"
        exit 1
        ;;
esac