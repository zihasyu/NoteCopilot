@echo off
echo ==========================================
echo NoteCopilot Launcher
echo ==========================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

if "%1"=="" (
    echo Usage: run.bat [chat^|init^|mcp]
    echo.
    echo Modes:
    echo   chat - Interactive chat mode ^(default^)
    echo   init - Initialize database only
    echo   mcp  - MCP server mode
    echo.
    echo Examples:
    echo   run.bat chat
    echo   run.bat init
    goto :end
)

if "%1"=="chat" (
    echo Starting Chat Mode...
    python main.py --mode chat
    goto :end
)

if "%1"=="init" (
    echo Initializing Database...
    python main.py --mode init
    goto :end
)

if "%1"=="mcp" (
    echo Starting MCP Server Mode...
    python main.py --mode mcp
    goto :end
)

echo Unknown mode: %1
echo Use: chat, init, or mcp

:end
pause
