@echo off
REM Background Waitress Service Script for Windows
REM =============================================

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set FLASK_DIR=%SCRIPT_DIR%flask
cd /d "%FLASK_DIR%"

REM Configuration
set SERVICE_NAME=flask-sop-query
set PID_FILE=%FLASK_DIR%waitress_flask_sop.pid
set LOG_FILE=%FLASK_DIR%waitress_flask_sop.log
set VENV_PATH=%SCRIPT_DIR%.venv

if "%1"=="setup" goto :setup_environment
if "%1"=="start" goto :start_service  
if "%1"=="stop" goto :stop_service
if "%1"=="restart" goto :restart_service
if "%1"=="status" goto :status_service
if "%1"=="logs" goto :show_logs
goto :show_usage

:start_service
echo 🚀 Starting %SERVICE_NAME% as background service...

REM Check if already running
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    tasklist /FI "PID eq !PID!" 2>nul | find /I "!PID!" >nul
    if !ERRORLEVEL! EQU 0 (
        echo 🟢 Service is already running (PID: !PID!)
        goto :eof
    )
)

REM Check virtual environment
if not exist "%VENV_PATH%" (
    echo 📦 Virtual environment not found. Please run 'service.bat setup' first.
    exit /b 1
)

REM Activate virtual environment
call "%VENV_PATH%\Scripts\activate.bat"

REM Install requirements
echo 📋 Installing/updating requirements...
pip install -q -r "%SCRIPT_DIR%requirements.txt"

REM Check if langchain_core is installed
python -c "import langchain_core" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  'langchain_core' is not installed! Please add it to requirements.txt and run 'service.bat setup' again.
    exit /b 1
)

REM Set Python path
set PYTHONPATH=%SCRIPT_DIR%modules;%SCRIPT_DIR%;%PYTHONPATH%

REM Start waitress in background and capture PID
echo 🪟 Starting waitress server...
start /B waitress-serve --host=0.0.0.0 --port=5000 app:app > "%LOG_FILE%" 2>&1

REM Find the PID of the waitress process (approximate method)
timeout /t 2 /nobreak >nul
set FOUND_PID=0
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO table /NH ^| find "python.exe"') do (
    echo %%i > "%PID_FILE%"
    set FOUND_PID=1
    goto :started
)

if !FOUND_PID! EQU 0 (
    echo ❌ Failed to start waitress server. Check logs at %LOG_FILE%
    exit /b 1
)

:started
set /p PID=<"%PID_FILE%"
echo ✅ Service started successfully!
echo 📱 Local Access: http://localhost:5000
echo 🌐 Network Access: http://[your-ip]:5000  
echo 📝 Logs: %LOG_FILE%
echo 🔢 PID: %PID%
goto :eof

:stop_service
if not exist "%PID_FILE%" (
    echo ❌ PID file not found. Service may not be running.
    goto :eof
)

set /p PID=<"%PID_FILE%"
echo 🛑 Stopping %SERVICE_NAME% (PID: %PID%)...

REM Kill waitress processes
taskkill /F /PID %PID% >nul 2>&1
taskkill /F /IM waitress-serve.exe >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq waitress*" >nul 2>&1

del "%PID_FILE%" >nul 2>&1
echo ✅ Service stopped successfully!
goto :eof

:restart_service
call :stop_service
timeout /t 2 /nobreak >nul
call :start_service
goto :eof

:status_service
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    tasklist /FI "PID eq !PID!" 2>nul | find /I "!PID!" >nul
    if !ERRORLEVEL! EQU 0 (
        REM Use quotes to avoid batch parsing errors with parentheses
        echo "🪟 Service is running (PID: !PID!) using waitress"
        echo 📱 Local Access: http://localhost:5000
        echo 🌐 Network Access: http://[your-ip]:5000
        echo 📝 Logs: %LOG_FILE%
        
        if exist "%LOG_FILE%" (
            echo.
            echo 📋 Recent log entries:
            powershell -Command "Get-Content '%LOG_FILE%' | Select-Object -Last 5"
        )
    ) else (
        echo 🔴 Service is not running
        REM Optionally delete stale PID file
        del "%PID_FILE%" >nul 2>&1
    )
) else (
    echo 🔴 Service is not running
)
goto :eof

:show_logs
if exist "%LOG_FILE%" (
    echo 📝 Showing logs (%LOG_FILE%):
    echo ==================
    type "%LOG_FILE%"
) else (
    echo ❌ Log file not found: %LOG_FILE%
)
goto :eof

:setup_environment
echo 🔧 Setting up environment for %SERVICE_NAME%...

REM Check Python
python --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Python is not installed or not in PATH
    echo    Install Python from https://python.org or Microsoft Store
    exit /b 1
)

REM Check Python version
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info[0])"') do set PYTHON_MAJOR=%%i
if not "%PYTHON_MAJOR%"=="3" (
    echo ❌ Python 3 is required
    exit /b 1
)

echo ✅ Using Python command: python

REM Create virtual environment
if not exist "%VENV_PATH%" (
    echo 📦 Creating virtual environment at %VENV_PATH%...
    python -m venv "%VENV_PATH%"
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Failed to create virtual environment
        exit /b 1
    )
    echo ✅ Virtual environment created successfully!
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
call "%VENV_PATH%\Scripts\activate.bat"

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip -q

REM Install requirements
echo 📋 Installing requirements...
pip install -r "%SCRIPT_DIR%requirements.txt"

echo 🪟 Windows environment configured with waitress
echo ✅ Environment setup complete!
echo 📝 You can now run: service.bat start
goto :eof

:show_usage
echo Usage: %0 {setup^|start^|stop^|restart^|status^|logs}
echo.
echo Commands:
echo   setup   - Set up virtual environment and install dependencies
echo   start   - Start the Flask SOP Query service in background
echo   stop    - Stop the running service
echo   restart - Restart the service  
echo   status  - Check if service is running
echo   logs    - Show application logs
echo.
echo First-time setup:
echo   %0 setup    # Set up environment (run this first)
echo   %0 start    # Start service
echo.
echo Regular usage:
echo   %0 status   # Check status
echo   %0 logs     # View logs
echo   %0 stop     # Stop service
exit /b 1