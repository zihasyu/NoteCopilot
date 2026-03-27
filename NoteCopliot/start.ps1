# NoteCopilot 启动脚本 (PowerShell)
# 功能: 启动 Milvus、MCP 服务和 FastAPI 主服务

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

# 设置 UTF-8 编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "启动 NoteCopilot 服务" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 检查 uv 是否安装
Write-Host "[1/7] 检查包管理器..." -ForegroundColor Yellow
$useUv = $false
try {
    $uvVersion = uv --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] 检测到 uv 包管理器: $uvVersion" -ForegroundColor Green
        $useUv = $true
    }
} catch {
    Write-Host "[INFO] uv 未安装，将使用传统 pip 方式" -ForegroundColor Gray
    Write-Host "[TIP] 安装 uv 可提升速度: pip install uv" -ForegroundColor Gray
}
Write-Host ""

# 确保 Python 版本正确
Write-Host "[2/7] 配置 Python 版本..." -ForegroundColor Yellow
if (Test-Path ".python-version") {
    $pythonVersion = Get-Content ".python-version" -Raw
    Write-Host "[INFO] 当前配置版本: $pythonVersion" -ForegroundColor Gray
} else {
    Write-Host "[INFO] 创建 .python-version 文件..." -ForegroundColor Gray
    "3.11" | Out-File -FilePath ".python-version" -Encoding utf8
}
Write-Host ""

# 创建或同步虚拟环境
Write-Host "[3/7] 创建/同步虚拟环境..." -ForegroundColor Yellow
$venvPython = ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "[INFO] 虚拟环境已存在" -ForegroundColor Gray
    & $venvPython -m pip install -e . -q
} else {
    Write-Host "[INFO] 创建新的虚拟环境..." -ForegroundColor Gray
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] 虚拟环境创建失败" -ForegroundColor Red
        exit 1
    }
    & $venvPython -m pip install --upgrade pip -q
    & $venvPython -m pip install -e . -q
}
Write-Host "[OK] 虚拟环境就绪" -ForegroundColor Green
Write-Host ""

# 设置 Python 命令
$pythonCmd = $venvPython

# 启动 Docker Compose
Write-Host "[4/7] 启动 Milvus 向量数据库..." -ForegroundColor Yellow
$dockerPs = docker ps --format "{{.Names}}" 2>$null
if ($dockerPs -match "milvus-standalone") {
    Write-Host "[INFO] Milvus 容器已在运行" -ForegroundColor Gray
} else {
    docker compose -f vector-database.yml up -d
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker 启动失败，请确保 Docker Desktop 已启动" -ForegroundColor Red
        exit 1
    }
    Write-Host "[INFO] 等待 Milvus 启动（10秒）..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
}
Write-Host "[OK] Milvus 数据库就绪" -ForegroundColor Green
Write-Host ""

# 启动 MCP 服务
Write-Host "[5/7] 启动 MCP 工具服务..." -ForegroundColor Yellow

# NoteSearch MCP
$noteSearchJob = Start-Process -FilePath $pythonCmd -ArgumentList "mcp_servers/note_search_server.py" -WindowStyle Minimized -PassThru
Write-Host "[OK] NoteSearch MCP 服务已启动 (端口 8003, PID: $($noteSearchJob.Id))" -ForegroundColor Green
Start-Sleep -Seconds 2

# PaperEnhance MCP
$paperEnhanceJob = Start-Process -FilePath $pythonCmd -ArgumentList "mcp_servers/paper_enhance_server.py" -WindowStyle Minimized -PassThru
Write-Host "[OK] PaperEnhance MCP 服务已启动 (端口 8004, PID: $($paperEnhanceJob.Id))" -ForegroundColor Green
Start-Sleep -Seconds 2

# BlogUpload MCP
$blogUploadJob = Start-Process -FilePath $pythonCmd -ArgumentList "mcp_servers/blog_upload_server.py" -WindowStyle Minimized -PassThru
Write-Host "[OK] BlogUpload MCP 服务已启动 (端口 8005, PID: $($blogUploadJob.Id))" -ForegroundColor Green
Write-Host ""

# 启动 FastAPI 服务
Write-Host "[6/7] 启动 FastAPI 服务..." -ForegroundColor Yellow
$fastapiJob = Start-Process -FilePath $pythonCmd -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9900" -WindowStyle Normal -PassThru
Write-Host "[INFO] 等待服务启动（15秒）..." -ForegroundColor Gray
Start-Sleep -Seconds 15
Write-Host ""

# 检查服务状态并上传文档
Write-Host "[7/7] 检查服务状态..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:9900/api/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] FastAPI 服务运行正常" -ForegroundColor Green
    Write-Host ""

    # 上传笔记到向量数据库
    Write-Host "[INFO] 上传笔记到向量数据库..." -ForegroundColor Gray
    $experimentFiles = Get-ChildItem -Path "notes\experiments\*.md" -ErrorAction SilentlyContinue
    $paperFiles = Get-ChildItem -Path "notes\papers\*.md" -ErrorAction SilentlyContinue

    foreach ($file in $experimentFiles) {
        Write-Host "  上传: $($file.Name)" -ForegroundColor Gray
        try {
            $form = @{ file = $file }
            Invoke-RestMethod -Uri "http://localhost:9900/api/upload" -Method POST -Form $form -TimeoutSec 10 | Out-Null
        } catch {
            Write-Host "  [WARN] 上传 $($file.Name) 失败: $_" -ForegroundColor Yellow
        }
    }

    foreach ($file in $paperFiles) {
        Write-Host "  上传: $($file.Name)" -ForegroundColor Gray
        try {
            $form = @{ file = $file }
            Invoke-RestMethod -Uri "http://localhost:9900/api/upload" -Method POST -Form $form -TimeoutSec 10 | Out-Null
        } catch {
            Write-Host "  [WARN] 上传 $($file.Name) 失败: $_" -ForegroundColor Yellow
        }
    }

    Write-Host "[OK] 笔记上传完成" -ForegroundColor Green
} catch {
    Write-Host "[WARN] 服务可能还未完全启动，请稍等片刻: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "NoteCopilot 服务启动完成！" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host "Web 界面: http://localhost:9900" -ForegroundColor Cyan
Write-Host "API 文档: http://localhost:9900/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看日志:" -ForegroundColor Gray
Write-Host "  - FastAPI: logs\app_*.log" -ForegroundColor Gray
Write-Host "  - MCP 服务: 查看对应终端窗口" -ForegroundColor Gray
Write-Host ""
Write-Host "停止服务: .\stop.ps1" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan

# 保存进程ID到文件，方便停止脚本使用
@{
    FastAPI = $fastapiJob.Id
    NoteSearch = $noteSearchJob.Id
    PaperEnhance = $paperEnhanceJob.Id
    BlogUpload = $blogUploadJob.Id
} | ConvertTo-Json | Out-File -FilePath ".service_pids.json" -Encoding utf8

# 等待用户按键
Read-Host "按 Enter 键关闭此窗口"
