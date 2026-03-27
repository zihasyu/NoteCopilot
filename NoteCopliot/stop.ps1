# NoteCopilot 停止脚本 (PowerShell)
# 功能: 停止所有 NoteCopilot 相关服务

$ErrorActionPreference = "SilentlyContinue"

# 设置 UTF-8 编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "停止 NoteCopilot 服务" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 从文件读取进程ID
$pidsFile = ".service_pids.json"
$servicePids = $null
if (Test-Path $pidsFile) {
    try {
        $servicePids = Get-Content $pidsFile -Raw | ConvertFrom-Json
        Write-Host "[INFO] 读取服务进程信息" -ForegroundColor Gray
    } catch {
        Write-Host "[WARN] 无法读取进程信息文件" -ForegroundColor Yellow
    }
}

# 停止 FastAPI 服务
Write-Host "[1/5] 停止 FastAPI 服务..." -ForegroundColor Yellow
if ($servicePids -and $servicePids.FastAPI) {
    $process = Get-Process -Id $servicePids.FastAPI -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $servicePids.FastAPI -Force
        Write-Host "[OK] FastAPI 服务已停止 (PID: $($servicePids.FastAPI))" -ForegroundColor Green
    } else {
        Write-Host "[INFO] FastAPI 服务未运行" -ForegroundColor Gray
    }
} else {
    # 尝试通过窗口标题查找
    $fastapiProcess = Get-Process | Where-Object { $_.MainWindowTitle -like "*NoteCopilot*" -or $_.MainWindowTitle -like "*uvicorn*" }
    if ($fastapiProcess) {
        $fastapiProcess | ForEach-Object { Stop-Process -Id $_.Id -Force }
        Write-Host "[OK] FastAPI 服务已停止" -ForegroundColor Green
    } else {
        Write-Host "[INFO] FastAPI 服务未运行或已停止" -ForegroundColor Gray
    }
}
Write-Host ""

# 停止 MCP 服务
Write-Host "[2/5] 停止 NoteSearch MCP 服务..." -ForegroundColor Yellow
if ($servicePids -and $servicePids.NoteSearch) {
    $process = Get-Process -Id $servicePids.NoteSearch -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $servicePids.NoteSearch -Force
        Write-Host "[OK] NoteSearch MCP 服务已停止 (PID: $($servicePids.NoteSearch))" -ForegroundColor Green
    } else {
        Write-Host "[INFO] NoteSearch MCP 服务未运行" -ForegroundColor Gray
    }
} else {
    Write-Host "[INFO] 未找到 NoteSearch MCP 进程信息" -ForegroundColor Gray
}
Write-Host ""

Write-Host "[3/5] 停止 PaperEnhance MCP 服务..." -ForegroundColor Yellow
if ($servicePids -and $servicePids.PaperEnhance) {
    $process = Get-Process -Id $servicePids.PaperEnhance -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $servicePids.PaperEnhance -Force
        Write-Host "[OK] PaperEnhance MCP 服务已停止 (PID: $($servicePids.PaperEnhance))" -ForegroundColor Green
    } else {
        Write-Host "[INFO] PaperEnhance MCP 服务未运行" -ForegroundColor Gray
    }
} else {
    Write-Host "[INFO] 未找到 PaperEnhance MCP 进程信息" -ForegroundColor Gray
}
Write-Host ""

Write-Host "[4/5] 停止 BlogUpload MCP 服务..." -ForegroundColor Yellow
if ($servicePids -and $servicePids.BlogUpload) {
    $process = Get-Process -Id $servicePids.BlogUpload -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $servicePids.BlogUpload -Force
        Write-Host "[OK] BlogUpload MCP 服务已停止 (PID: $($servicePids.BlogUpload))" -ForegroundColor Green
    } else {
        Write-Host "[INFO] BlogUpload MCP 服务未运行" -ForegroundColor Gray
    }
} else {
    Write-Host "[INFO] 未找到 BlogUpload MCP 进程信息" -ForegroundColor Gray
}
Write-Host ""

# 停止 Python 进程 (备用方案 - 停止所有相关 Python 进程)
Write-Host "[INFO] 检查并停止其他相关 Python 进程..." -ForegroundColor Gray
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*note_search_server*" -or
    $_.CommandLine -like "*paper_enhance_server*" -or
    $_.CommandLine -like "*blog_upload_server*" -or
    $_.CommandLine -like "*uvicorn*app.main*"
}
if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Host "  停止 Python 进程 (PID: $($_.Id))" -ForegroundColor Gray
    }
}
Write-Host ""

# 停止 Docker 容器
Write-Host "[5/5] 停止 Milvus 容器..." -ForegroundColor Yellow
$dockerPs = docker ps --format "{{.Names}}" 2>$null
if ($dockerPs -match "milvus") {
    docker compose -f vector-database.yml down
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Milvus 容器已停止" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] 停止 Docker 容器失败" -ForegroundColor Red
    }
} else {
    Write-Host "[INFO] Milvus 容器未运行" -ForegroundColor Gray
}
Write-Host ""

# 清理 PID 文件
if (Test-Path $pidsFile) {
    Remove-Item $pidsFile -Force
    Write-Host "[INFO] 清理进程信息文件" -ForegroundColor Gray
}

Write-Host "====================================" -ForegroundColor Green
Write-Host "所有服务已停止！" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "提示:" -ForegroundColor Gray
Write-Host "  - 如需完全清理 Docker 数据卷，运行:" -ForegroundColor Gray
Write-Host "    docker compose -f vector-database.yml down -v" -ForegroundColor Yellow
Write-Host ""
Write-Host "  - 重新启动服务:" -ForegroundColor Gray
Write-Host "    .\start.ps1" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan

# 等待用户按键
Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
