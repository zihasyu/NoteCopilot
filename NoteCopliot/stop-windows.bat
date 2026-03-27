@echo off
chcp 65001 >nul
echo ====================================
echo 停止 NoteCopilot 服务
echo ====================================
echo.

REM Stop FastAPI service
echo [1/5] 停止 FastAPI 服务...
taskkill /FI "WINDOWTITLE eq NoteCopilot API*" /F >nul 2>&1
if errorlevel 1 (
    echo [信息] FastAPI 服务未运行或已停止
) else (
    echo [成功] FastAPI 服务已停止
)
echo.

REM Stop MCP services
echo [2/5] 停止 NoteSearch MCP 服务...
taskkill /FI "WINDOWTITLE eq NoteSearch MCP*" /F >nul 2>&1
if errorlevel 1 (
    echo [信息] NoteSearch MCP 服务未运行
) else (
    echo [成功] NoteSearch MCP 服务已停止
)
echo.

echo [3/5] 停止 PaperEnhance MCP 服务...
taskkill /FI "WINDOWTITLE eq PaperEnhance MCP*" /F >nul 2>&1
if errorlevel 1 (
    echo [信息] PaperEnhance MCP 服务未运行
) else (
    echo [成功] PaperEnhance MCP 服务已停止
)
echo.

echo [4/5] 停止 BlogUpload MCP 服务...
taskkill /FI "WINDOWTITLE eq BlogUpload MCP*" /F >nul 2>&1
if errorlevel 1 (
    echo [信息] BlogUpload MCP 服务未运行
) else (
    echo [成功] BlogUpload MCP 服务已停止
)
echo.

REM Stop Docker containers
echo [5/5] 停止 Milvus 容器...
docker ps --format "{{.Names}}" | findstr "milvus" >nul 2>&1
if not errorlevel 1 (
    docker compose -f vector-database.yml down
    if errorlevel 1 (
        echo [错误] 停止 Docker 容器失败
    ) else (
        echo [成功] Milvus 容器已停止
    )
) else (
    echo [信息] Milvus 容器未运行
)
echo.

echo ====================================
echo 所有服务已停止！
echo ====================================
echo.
echo 提示:
echo   - 如需完全清理 Docker 数据卷，运行:
echo     docker compose -f vector-database.yml down -v
echo.
pause
