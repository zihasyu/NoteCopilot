@echo off
chcp 65001 >nul 2>&1
echo ==========================================
echo NoteCopilot Windows Setup
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found. Please install Docker Desktop
    exit /b 1
)

REM Create virtual environment
if not exist .venv (
    echo [1/5] Creating virtual environment...
    python -m venv .venv
) else (
    echo [1/5] Virtual environment already exists
)

REM Activate and install dependencies
echo [2/5] Installing dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create notes directory
echo [3/5] Setting up directories...
if not exist notes mkdir notes
if not exist checkpoints mkdir checkpoints

REM Start Docker services
echo [4/5] Starting Milvus with Docker...
docker-compose up -d

echo.
echo Waiting for Milvus to be ready...
timeout /t 10 /nobreak >nul

REM Check Milvus health
echo [5/5] Checking Milvus status...
docker exec milvus-standalone curl -s http://localhost:9091/health >nul 2>&1
if errorlevel 1 (
    echo [WARN] Milvus may still be starting, please wait 30s and try again
) else (
    echo [OK] Milvus is ready
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo   1. Copy .env.example to .env and add your API keys
echo   2. Add your markdown notes to the 'notes' folder
echo   3. Run: .venv\Scripts\python.exe main.py --mode init
echo   4. Run: .venv\Scripts\python.exe main.py --mode chat
echo.
echo Services:
echo   - Milvus: localhost:19530
echo   - Att UI: http://localhost:8000
echo.
pause
