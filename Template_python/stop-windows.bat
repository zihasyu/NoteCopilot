@echo off
chcp 65001 >nul
echo ====================================
echo Stopping SuperBizAgent Services
echo ====================================
echo.

REM Stop FastAPI service
echo [1/4] Stopping FastAPI service...
taskkill /FI "WINDOWTITLE eq SuperBizAgent API*" /F >nul 2>&1
if errorlevel 1 (
    echo [INFO] FastAPI service is not running or already stopped.
) else (
    echo [SUCCESS] FastAPI service stopped.
)
echo.

REM Stop CLS MCP service
echo [2/4] Stopping CLS MCP service...
taskkill /FI "WINDOWTITLE eq CLS MCP Server*" /F >nul 2>&1
if errorlevel 1 (
    echo [INFO] CLS MCP service is not running or already stopped.
) else (
    echo [SUCCESS] CLS MCP service stopped.
)
echo.

REM Stop Monitor MCP service
echo [3/4] Stopping Monitor MCP service...
taskkill /FI "WINDOWTITLE eq Monitor MCP Server*" /F >nul 2>&1
if errorlevel 1 (
    echo [INFO] Monitor MCP service is not running or already stopped.
) else (
    echo [SUCCESS] Monitor MCP service stopped.
)
echo.

REM Stop Docker containers
echo [4/4] Stopping Milvus containers...
docker ps --format "{{.Names}}" | findstr "milvus" >nul 2>&1
if not errorlevel 1 (
    docker compose -f vector-database.yml down
    if errorlevel 1 (
        echo [ERROR] Failed to stop Docker containers.
    ) else (
        echo [SUCCESS] Milvus containers stopped.
    )
) else (
    echo [INFO] Milvus containers are not running.
)
echo.

echo ====================================
echo All services have been stopped!
echo ====================================
echo.
echo Hint:
echo   - To completely clean up Docker data volumes, run:
echo     docker compose -f vector-database.yml down -v
echo.
pause