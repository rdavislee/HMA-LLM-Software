@echo off
echo ============================================================
echo HMA-LLM Software Construction - Development Mode
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import websockets" >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install Python dependencies
        pause
        exit /b 1
    )
)

REM Check if frontend directory exists
if not exist "new_frontend" (
    echo ERROR: Frontend directory not found!
    echo Please ensure the 'new_frontend' directory exists.
    pause
    exit /b 1
)

echo.
echo Frontend Setup Instructions:
echo 1. Open a new command prompt window
echo 2. Navigate to: %CD%\new_frontend
echo 3. Install dependencies: npm install
echo 4. Start the development server: npm run dev
echo 5. Open your browser to the URL shown by Vite
echo.
echo The frontend will automatically connect to the backend WebSocket server.
echo.

echo Starting HMA-LLM Backend Server...
echo WebSocket server will be available at: ws://localhost:8080/ws
echo Generated projects will be saved to: generated_projects/
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the backend server
python scripts/start_dev.py

pause 