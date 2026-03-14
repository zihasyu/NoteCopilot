@echo off
chcp 65001 >nul
echo ====================================
echo 启动 LangChain Agent 服务
echo ====================================
echo.

REM 检查 Docker 是否运行
echo [1/3] 检查 Docker...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)
echo [成功] Docker 运行正常
echo.

REM 启动 Milvus 向量数据库
echo [2/3] 启动 Milvus 向量数据库...
docker ps --format "{{.Names}}" | findstr "milvus-standalone" >nul 2>&1
if not errorlevel 1 (
    echo [信息] Milvus 容器已在运行
) else (
    echo [信息] 正在启动 Milvus...
    docker compose -f vector-database.yml up -d
    if errorlevel 1 (
        echo [错误] Milvus 启动失败
        pause
        exit /b 1
    )
    echo [信息] 等待 Milvus 启动（15秒）...
    timeout /t 15 /nobreak >nul
)
echo [成功] Milvus 数据库就绪
echo.

REM 检查虚拟环境
echo [3/3] 检查 Python 环境...
if not exist .venv (
    echo [信息] 创建虚拟环境...
    python -m venv .venv
    echo [信息] 安装依赖...
    .venv\Scripts\python.exe -m pip install --upgrade pip -q
    .venv\Scripts\python.exe -m pip install -r requirements.txt -q
)
echo [成功] Python 环境就绪
echo.

echo ====================================
echo 服务启动完成！
echo ====================================
echo.
echo 运行测试脚本:
echo   .venv\Scripts\python.exe simple_demo.py
echo.
echo 或启动 API 服务:
echo   .venv\Scripts\python.exe -m uvicorn app.main:app --reload
echo.
echo 停止 Milvus:
echo   docker compose -f vector-database.yml down
echo ====================================
pause
