@echo off
chcp 65001 >nul 2>&1
echo ==========================================
echo NoteCopilot One-Click Starter
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found. Please install Docker Desktop
    pause
    exit /b 1
)

REM Create virtual environment
if not exist .venv (
    echo [1/6] Creating virtual environment...
    python -m venv .venv
) else (
    echo [1/6] Virtual environment exists
)

REM Activate and install dependencies
echo [2/6] Installing dependencies...
call .venv\Scripts\activate.bat >nul 2>&1
python -m pip install --upgrade pip 
pip install -r requirements.txt 

REM Create directories
echo [3/6] Setting up directories...
if not exist notes mkdir notes
if not exist checkpoints mkdir checkpoints

REM Check .env file
if not exist .env (
    echo [4/6] Creating .env file from template...
    copy .env.example .env >nul
    echo [WARN] Please edit .env and add your API keys!
    notepad .env
)

REM Start Docker services
echo [5/6] Starting Milvus...
docker-compose up -d --quiet-pull 

echo [INFO] Waiting for Milvus to start (30s)...
timeout /t 30 /nobreak >nul

REM Initialize database and ingest notes
echo [6/6] Initializing database and ingesting notes...
python main.py --mode init

REM Check if notes exist
python -c "import os; n=len([f for f in os.listdir('notes') if f.endswith('.md')]); print(f'[INFO] Found {n} markdown files')" 2>nul

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Starting chat mode...
echo.

REM Start chat mode
python main.py --mode chat
