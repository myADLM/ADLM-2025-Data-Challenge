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
echo Starting %SERVICE_NAME% as background service...

REM Check if already running
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    tasklist /FI "PID eq !PID!" 2>nul | find /I "!PID!" >nul
    if !ERRORLEVEL! EQU 0 (
        echo Service is already running (PID: !PID!)
        goto :eof
    )
)

REM Check virtual environment
if not exist "%VENV_PATH%" (
    echo Virtual environment not found. Please run 'service.bat setup' first.
    exit /b 1
)

REM Check virtual environment without activating it
echo Checking dependencies...
"%VENV_PATH%\Scripts\python.exe" -c "import sys; print('Python OK')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Virtual environment Python not working
    exit /b 1
)

REM Install requirements using python -m pip to avoid path issues
echo Installing/updating requirements...
"%VENV_PATH%\Scripts\python.exe" -m pip install -q -r "%SCRIPT_DIR%requirements.txt"

REM Check if langchain_core is installed
"%VENV_PATH%\Scripts\python.exe" -c "import langchain_core" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: 'langchain_core' is not installed! Please add it to requirements.txt and run 'service.bat setup' again.
    exit /b 1
)

REM Set Python path for the batch file we're creating
set PYTHONPATH=%SCRIPT_DIR%modules;%SCRIPT_DIR%;%PYTHONPATH%

REM Start waitress server
echo Starting waitress server...

REM Create a batch file to run waitress in background with proper paths
echo @echo off > "%FLASK_DIR%\run_waitress.bat"
echo echo Starting waitress server... >> "%FLASK_DIR%\run_waitress.bat"
echo echo Working directory: %%CD%% >> "%FLASK_DIR%\run_waitress.bat"
echo cd /d "%FLASK_DIR%" >> "%FLASK_DIR%\run_waitress.bat"
echo echo Changed to: %%CD%% >> "%FLASK_DIR%\run_waitress.bat"
echo set PYTHONPATH=%SCRIPT_DIR%modules;%SCRIPT_DIR% >> "%FLASK_DIR%\run_waitress.bat"
echo echo Python path: %%PYTHONPATH%% >> "%FLASK_DIR%\run_waitress.bat"
echo echo Python executable: "%VENV_PATH%\Scripts\python.exe" >> "%FLASK_DIR%\run_waitress.bat"
echo "%VENV_PATH%\Scripts\python.exe" --version >> "%FLASK_DIR%\run_waitress.bat"
echo "%VENV_PATH%\Scripts\python.exe" -m waitress --host=0.0.0.0 --port=5000 app:app >> "%FLASK_DIR%\run_waitress.bat"

REM Start waitress with proper logging redirection
start /B "" cmd /c ""%FLASK_DIR%\run_waitress.bat" > "%LOG_FILE%" 2>&1"

REM Give the process time to start
timeout /t 3 /nobreak >nul

REM Find the waitress process PID
set FOUND_PID=0
set PID_VALUE=

REM Method 1: Look for python.exe with waitress in command line
for /f "skip=1 tokens=2" %%i in ('wmic process where "name='python.exe' and commandline like '%%waitress%%'" get processid /format:csv 2^>nul ^| findstr /v "Node"') do (
    if not "%%i"=="" (
        set PID_VALUE=%%i
        set FOUND_PID=1
        goto :write_pid
    )
)

REM Method 2: Look for most recent python.exe process
if !FOUND_PID! EQU 0 (
    for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /NH 2^>nul') do (
        set PID_VALUE=%%i
        set FOUND_PID=1
        goto :write_pid
    )
)

:write_pid
if !FOUND_PID! EQU 1 (
    echo !PID_VALUE! > "%PID_FILE%"
)

if !FOUND_PID! EQU 0 (
    echo Failed to start waitress server. Check logs at %LOG_FILE%
    exit /b 1
)

:started
echo Service started successfully!
echo Local Access: http://localhost:5000
echo Network Access: http://[your-ip]:5000  
echo Logs: %LOG_FILE%
if defined PID_VALUE (
    echo PID: !PID_VALUE!
) else (
    echo PID: Check task manager for python.exe process
)

REM Return to original directory
cd /d "%SCRIPT_DIR%"
goto :eof

:stop_service
echo Stopping %SERVICE_NAME%...

REM Kill specific PID if available
if exist "%PID_FILE%" (
    set /p STORED_PID=<"%PID_FILE%"
    if defined STORED_PID (
        echo Stopping process PID: !STORED_PID!
        taskkill /F /PID !STORED_PID! >nul 2>&1
    )
    del "%PID_FILE%" >nul 2>&1
)

REM Kill any remaining python processes running waitress
for /f "skip=1 tokens=2" %%i in ('wmic process where "name='python.exe' and commandline like '%%waitress%%'" get processid 2^>nul ^| findstr /v "Node"') do (
    if not "%%i"=="" (
        echo Stopping waitress process PID: %%i
        taskkill /F /PID %%i >nul 2>&1
    )
)

REM Clean up temporary files
del "%FLASK_DIR%\run_waitress.bat" >nul 2>&1

echo Service stopped successfully!
goto :eof

:restart_service
call :stop_service
timeout /t 2 /nobreak >nul
call :start_service
goto :eof

:status_service
set SERVICE_RUNNING=0

REM Check if PID file exists and process is running
if exist "%PID_FILE%" (
    set /p STORED_PID=<"%PID_FILE%"
    if defined STORED_PID (
        tasklist /FI "PID eq !STORED_PID!" 2>nul | find /I "!STORED_PID!" >nul
        if !ERRORLEVEL! EQU 0 (
            echo Service is running - PID: !STORED_PID!
            set SERVICE_RUNNING=1
        )
    )
)

REM Also check for any python processes running waitress
for /f "skip=1 tokens=2" %%i in ('wmic process where "name='python.exe' and commandline like '%%waitress%%'" get processid 2^>nul ^| findstr /v "Node"') do (
    if not "%%i"=="" (
        echo Waitress service found - PID: %%i
        set SERVICE_RUNNING=1
    )
)

if !SERVICE_RUNNING! EQU 1 (
    echo Local Access: http://localhost:5000
    echo Network Access: http://[your-ip]:5000
    echo Logs: %LOG_FILE%
    
    if exist "%LOG_FILE%" (
        echo.
        echo Recent log entries:
        powershell -Command "Get-Content '%LOG_FILE%' | Select-Object -Last 3"
    )
) else (
    echo Service is not running
    REM Clean up stale PID file
    if exist "%PID_FILE%" del "%PID_FILE%" >nul 2>&1
)
goto :eof

:show_logs
if exist "%LOG_FILE%" (
    echo Showing logs (%LOG_FILE%):
    echo ==================
    type "%LOG_FILE%"
) else (
    echo Log file not found: %LOG_FILE%
)
goto :eof

:setup_environment
echo Setting up environment for %SERVICE_NAME%...

REM Check Python
python --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo    Install Python from https://python.org or Microsoft Store
    exit /b 1
)

REM Check Python version
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info[0])"') do set PYTHON_MAJOR=%%i
if not "%PYTHON_MAJOR%"=="3" (
    echo ERROR: Python 3 is required
    exit /b 1
)

echo Using Python command: python

REM Create virtual environment
if not exist "%VENV_PATH%" (
    echo Creating virtual environment at %VENV_PATH%...
    python -m venv "%VENV_PATH%"
    if !ERRORLEVEL! NEQ 0 (
        echo ERROR: Failed to create virtual environment
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists
)

REM Upgrade pip using full path (no activation needed)
echo Upgrading pip...
"%VENV_PATH%\Scripts\python.exe" -m pip install --upgrade pip -q

REM Install requirements using full path
echo Installing requirements...
"%VENV_PATH%\Scripts\python.exe" -m pip install -r "%SCRIPT_DIR%requirements.txt"

echo Windows environment configured with waitress
echo Environment setup complete!
echo You can now run: service.bat start
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