# NoteCopilot Stop Script (PowerShell)
# Usage: .\stop-en.ps1

$ErrorActionPreference = "SilentlyContinue"

Write-Host "===================================="
Write-Host "Stopping NoteCopilot Services"
Write-Host "===================================="
Write-Host ""

$pidsFile = ".service_pids.json"
$servicePids = $null
if (Test-Path $pidsFile) {
    try {
        $servicePids = Get-Content $pidsFile -Raw | ConvertFrom-Json
        Write-Host "[INFO] Loaded service PIDs"
    } catch {
        Write-Host "[WARN] Cannot read PID file"
    }
}

# Stop FastAPI
Write-Host "[1/5] Stopping FastAPI..."
if ($servicePids -and $servicePids.FastAPI) {
    $proc = Get-Process -Id $servicePids.FastAPI -ErrorAction SilentlyContinue
    if ($proc) {
        Stop-Process -Id $servicePids.FastAPI -Force
        Write-Host "[OK] FastAPI stopped (PID: $($servicePids.FastAPI))"
    } else {
        Write-Host "[INFO] FastAPI not running"
    }
} else {
    $procs = Get-Process | Where-Object { $_.MainWindowTitle -like "*NoteCopilot*" -or $_.MainWindowTitle -like "*uvicorn*" }
    if ($procs) {
        $procs | ForEach-Object { Stop-Process -Id $_.Id -Force }
        Write-Host "[OK] FastAPI stopped"
    } else {
        Write-Host "[INFO] FastAPI not running"
    }
}
Write-Host ""

# Stop MCP services
Write-Host "[2/5] Stopping NoteSearch MCP..."
if ($servicePids -and $servicePids.NoteSearch) {
    $proc = Get-Process -Id $servicePids.NoteSearch -ErrorAction SilentlyContinue
    if ($proc) { Stop-Process -Id $servicePids.NoteSearch -Force; Write-Host "[OK] Stopped" }
    else { Write-Host "[INFO] Not running" }
}
Write-Host ""

Write-Host "[3/5] Stopping PaperEnhance MCP..."
if ($servicePids -and $servicePids.PaperEnhance) {
    $proc = Get-Process -Id $servicePids.PaperEnhance -ErrorAction SilentlyContinue
    if ($proc) { Stop-Process -Id $servicePids.PaperEnhance -Force; Write-Host "[OK] Stopped" }
    else { Write-Host "[INFO] Not running" }
}
Write-Host ""

Write-Host "[4/5] Stopping BlogUpload MCP..."
if ($servicePids -and $servicePids.BlogUpload) {
    $proc = Get-Process -Id $servicePids.BlogUpload -ErrorAction SilentlyContinue
    if ($proc) { Stop-Process -Id $servicePids.BlogUpload -Force; Write-Host "[OK] Stopped" }
    else { Write-Host "[INFO] Not running" }
}
Write-Host ""

# Stop any remaining Python processes
Write-Host "[INFO] Checking for remaining Python processes..."
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*note_search_server*" -or
    $_.CommandLine -like "*paper_enhance_server*" -or
    $_.CommandLine -like "*blog_upload_server*" -or
    $_.CommandLine -like "*uvicorn*app.main*"
}
if ($pythonProcs) {
    $pythonProcs | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Host "  Stopped Python PID: $($_.Id)"
    }
}
Write-Host ""

# Stop Docker
Write-Host "[5/5] Stopping Milvus containers..."
$dockerPs = docker ps --format "{{.Names}}" 2>$null
if ($dockerPs -match "milvus") {
    docker compose -f vector-database.yml down
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Milvus stopped"
    } else {
        Write-Host "[ERROR] Failed to stop Docker"
    }
} else {
    Write-Host "[INFO] Milvus not running"
}
Write-Host ""

# Cleanup
if (Test-Path $pidsFile) {
    Remove-Item $pidsFile -Force
    Write-Host "[INFO] Cleaned up PID file"
}

Write-Host "===================================="
Write-Host "All services stopped!"
Write-Host "===================================="
Write-Host ""
Write-Host "To clean Docker volumes:"
Write-Host "  docker compose -f vector-database.yml down -v"
Write-Host ""
Write-Host "To restart:"
Write-Host "  .\start-en.ps1"
Write-Host "===================================="

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
