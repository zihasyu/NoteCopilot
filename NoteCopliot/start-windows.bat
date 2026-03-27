@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ====================================
echo 启动 NoteCopilot 服务
echo ====================================
echo.

REM 检查 uv 是否安装
echo [1/7] 检查包管理器...
where uv >nul 2>&1
if errorlevel 1 (
    echo [信息] uv 未安装，将使用传统 pip 方式
    echo [提示] 安装 uv 可提升速度：pip install uv
    set USE_UV=0
) else (
    echo [成功] 检测到 uv 包管理器
    set USE_UV=1
)
echo.

REM 确保 Python 版本正确
echo [2/7] 配置 Python 版本...
if exist .python-version (
    set /p PYTHON_VERSION=<.python-version
    echo [信息] 当前配置版本: !PYTHON_VERSION!
) else (
    echo [信息] 创建 .python-version 文件...
    echo 3.11> .python-version
)
echo.

REM 创建或同步虚拟环境
echo [3/7] 创建/同步虚拟环境...
if exist .venv\Scripts\python.exe (
    echo [信息] 虚拟环境已存在
    .venv\Scripts\python.exe -m pip install -e . -q
) else (
    echo [信息] 创建新的虚拟环境...
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install --upgrade pip -q
    .venv\Scripts\python.exe -m pip install -e . -q
)
echo [成功] 虚拟环境就绪
echo.

REM 设置 Python 命令
set PYTHON_CMD=.venv\Scripts\python.exe

REM 启动 Docker Compose
echo [4/7] 启动 Milvus 向量数据库...
docker ps --format "{{.Names}}" | findstr "milvus-standalone" >nul 2>&1
if not errorlevel 1 (
    echo [信息] Milvus 容器已在运行
) else (
    docker compose -f vector-database.yml up -d
    if errorlevel 1 (
        echo [错误] Docker 启动失败，请确保 Docker Desktop 已启动
        pause
        exit /b 1
    )
    echo [信息] 等待 Milvus 启动（10秒）...
    timeout /t 10 /nobreak >nul
)
echo [成功] Milvus 数据库就绪
echo.

REM 启动 MCP 服务
echo [5/7] 启动 MCP 工具服务...

start "NoteSearch MCP" /min %PYTHON_CMD% mcp_servers/note_search_server.py
timeout /t 2 /nobreak >nul
echo [成功] NoteSearch MCP 服务已启动 (端口 8003)

start "PaperEnhance MCP" /min %PYTHON_CMD% mcp_servers/paper_enhance_server.py
timeout /t 2 /nobreak >nul
echo [成功] PaperEnhance MCP 服务已启动 (端口 8004)

start "BlogUpload MCP" /min %PYTHON_CMD% mcp_servers/blog_upload_server.py
timeout /t 2 /nobreak >nul
echo [成功] BlogUpload MCP 服务已启动 (端口 8005)
echo.

REM 启动 FastAPI 服务
echo [6/7] 启动 FastAPI 服务...
start "NoteCopilot API" %PYTHON_CMD% -m uvicorn app.main:app --host 0.0.0.0 --port 9900
echo [信息] 等待服务启动（15秒）...
timeout /t 15 /nobreak >nul
echo.

REM 检查服务状态并上传文档
echo.
echo [7/7] 检查服务状态...
curl -s http://localhost:9900/api/health >nul 2>&1
if errorlevel 1 (
    echo [警告] 服务可能还未完全启动，请稍等片刻
) else (
    echo [成功] FastAPI 服务运行正常
    echo.

    REM 调用 API 上传 notes 文档到向量数据库
    echo [信息] 上传笔记到向量数据库...
    for %%f in (notes\experiments\*.md) do (
        echo   上传: %%~nxf
        curl -s -X POST http://localhost:9900/api/upload -F "file=@%%f" >nul 2>&1
    )
    for %%f in (notes\papers\*.md) do (
        echo   上传: %%~nxf
        curl -s -X POST http://localhost:9900/api/upload -F "file=@%%f" >nul 2>&1
    )
    echo [成功] 笔记上传完成
)

echo.
echo ====================================
echo NoteCopilot 服务启动完成！
echo ====================================
echo Web 界面: http://localhost:9900
echo API 文档: http://localhost:9900/docs
echo.
echo 查看日志:
echo   - FastAPI: logs\app_*.log
echo   - NoteSearch MCP: type mcp_note_search.log
echo   - PaperEnhance MCP: type mcp_paper_enhance.log
echo   - BlogUpload MCP: type mcp_blog_upload.log
echo 停止服务: stop-windows.bat
echo ====================================
pause
