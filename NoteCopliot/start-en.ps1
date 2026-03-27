# NoteCopilot Startup Script (PowerShell)
# Usage: .\start-en.ps1

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

Write-Host "===================================="
Write-Host "Starting NoteCopilot Services"
Write-Host "===================================="
Write-Host ""

# Check package manager
Write-Host "[1/7] Checking package manager..."
$useUv = $false
try {
    $uvVersion = uv --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] uv detected: $uvVersion"
        $useUv = $true
    }
} catch {
    Write-Host "[INFO] uv not found, using pip"
    Write-Host "[TIP] Install uv for faster setup: pip install uv"
}
Write-Host ""

# Check Python version
Write-Host "[2/7] Configuring Python version..."
if (Test-Path ".python-version") {
    $pythonVersion = Get-Content ".python-version" -Raw
    Write-Host "[INFO] Current version: $pythonVersion"
} else {
    Write-Host "[INFO] Creating .python-version file..."
    "3.11" | Out-File -FilePath ".python-version"
}
Write-Host ""

# Setup virtual environment
Write-Host "[3/7] Setting up virtual environment..."
$venvPython = ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "[INFO] Virtual environment exists"
    & $venvPython -m pip install -e . -q
} else {
    Write-Host "[INFO] Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment"
        exit 1
    }
    & $venvPython -m pip install --upgrade pip -q
    & $venvPython -m pip install -e . -q
}
Write-Host "[OK] Virtual environment ready"
Write-Host ""

$pythonCmd = $venvPython

# Start Docker/Milvus
Write-Host "[4/7] Starting Milvus database..."
$dockerPs = docker ps --format "{{.Names}}" 2>$null
if ($dockerPs -match "milvus-standalone") {
    Write-Host "[INFO] Milvus already running"
} else {
    docker compose -f vector-database.yml up -d
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker failed to start. Is Docker Desktop running?"
        exit 1
    }
    Write-Host "[INFO] Waiting 20s for Milvus to be fully ready..."
    Start-Sleep -Seconds 20

    # 检查 Milvus 是否真的就绪
    $maxRetries = 10
    $retryCount = 0
    $milvusReady = $false

    while ($retryCount -lt $maxRetries -and -not $milvusReady) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:9091/healthz" -Method GET -TimeoutSec 2 -ErrorAction Stop
            if ($response -eq "OK") {
                $milvusReady = $true
                Write-Host "[OK] Milvus health check passed"
            }
        } catch {
            $retryCount++
            Write-Host "[INFO] Waiting for Milvus to be ready... ($retryCount/$maxRetries)"
            Start-Sleep -Seconds 2
        }
    }

    if (-not $milvusReady) {
        Write-Host "[WARN] Milvus may not be fully ready, but continuing..."
    }
}
Write-Host "[OK] Milvus ready"
Write-Host ""

# Start MCP services
Write-Host "[5/7] Starting MCP services..."

$noteSearchJob = Start-Process -FilePath $pythonCmd -ArgumentList "mcp_servers/note_search_server.py" -WindowStyle Minimized -PassThru
Write-Host "[OK] NoteSearch MCP started (PID: $($noteSearchJob.Id))"
Start-Sleep -Seconds 2

$paperEnhanceJob = Start-Process -FilePath $pythonCmd -ArgumentList "mcp_servers/paper_enhance_server.py" -WindowStyle Minimized -PassThru
Write-Host "[OK] PaperEnhance MCP started (PID: $($paperEnhanceJob.Id))"
Start-Sleep -Seconds 2

$blogUploadJob = Start-Process -FilePath $pythonCmd -ArgumentList "mcp_servers/blog_upload_server.py" -WindowStyle Minimized -PassThru
Write-Host "[OK] BlogUpload MCP started (PID: $($blogUploadJob.Id))"
Write-Host ""

# Start FastAPI
Write-Host "[6/7] Starting FastAPI service..."
$fastapiJob = Start-Process -FilePath $pythonCmd -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9900" -WindowStyle Normal -PassThru
Write-Host "[INFO] Waiting 15s for startup..."
Start-Sleep -Seconds 15
Write-Host ""

# Check health and upload notes
Write-Host "[7/7] Checking service status..."
try {
    $health = Invoke-RestMethod -Uri "http://localhost:9900/health" -Method GET -TimeoutSec 5
    Write-Host "[OK] FastAPI service running"
    Write-Host ""

    Write-Host "[INFO] Uploading notes to vector database..."
    $expFiles = Get-ChildItem -Path "notes\experiments\*.md" -ErrorAction SilentlyContinue
    $paperFiles = Get-ChildItem -Path "notes\papers\*.md" -ErrorAction SilentlyContinue

    foreach ($file in $expFiles) {
        Write-Host "  Uploading: $($file.Name)"
        try {
            $form = @{ file = $file }
            Invoke-RestMethod -Uri "http://localhost:9900/api/upload" -Method POST -Form $form -TimeoutSec 10 | Out-Null
        } catch {
            Write-Host "  [WARN] Failed: $($file.Name)"
        }
    }

    foreach ($file in $paperFiles) {
        Write-Host "  Uploading: $($file.Name)"
        try {
            $form = @{ file = $file }
            Invoke-RestMethod -Uri "http://localhost:9900/api/upload" -Method POST -Form $form -TimeoutSec 10 | Out-Null
        } catch {
            Write-Host "  [WARN] Failed: $($file.Name)"
        }
    }

    Write-Host "[OK] Notes uploaded"
} catch {
    Write-Host "[WARN] Service may not be fully ready yet"
}

Write-Host ""
Write-Host "===================================="
Write-Host "NoteCopilot Started Successfully!"
Write-Host "===================================="
Write-Host "Web UI:    http://localhost:9900"
Write-Host "API Docs:  http://localhost:9900/docs"
Write-Host ""
Write-Host "Logs:"
Write-Host "  - FastAPI: logs\app_*.log"
Write-Host ""
Write-Host "To stop: .\stop-en.ps1"
Write-Host "===================================="

# Save PIDs
@{
    FastAPI = $fastapiJob.Id
    NoteSearch = $noteSearchJob.Id
    PaperEnhance = $paperEnhanceJob.Id
    BlogUpload = $blogUploadJob.Id
} | ConvertTo-Json | Out-File -FilePath ".service_pids.json"

Read-Host "Press Enter to close"
