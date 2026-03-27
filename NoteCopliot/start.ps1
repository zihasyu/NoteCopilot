# Disable progress bar for cleaner output
$ProgressPreference = 'SilentlyContinue'

Write-Host "===================================="
Write-Host "Starting SuperBizAgent Service"
Write-Host "===================================="
Write-Host ""

# [1/6] Check Package Manager
Write-Host "[1/6] Checking package manager..."
$uvPath = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uvPath) {
    Write-Host "[INFO] uv not found. Using traditional pip method." -ForegroundColor Yellow
    Write-Host "[TIP] Install uv for faster performance: pip install uv" -ForegroundColor Cyan
    $USE_UV = $false
} else {
    Write-Host "[SUCCESS] uv package manager detected." -ForegroundColor Green
    $USE_UV = $true
}
Write-Host ""

# [2/6] Configure Python Version
Write-Host "[2/6] Configuring Python version..."
$pyVersionFile = ".python-version"
if (Test-Path $pyVersionFile) {
    $PYTHON_VERSION = Get-Content $pyVersionFile | Select-Object -First 1
    Write-Host "[INFO] Current configured version: $PYTHON_VERSION"
    
    if ($PYTHON_VERSION -like "*3.10*") {
        Write-Host "[WARNING] Python 3.10 is incompatible. Auto-updating to 3.13..." -ForegroundColor Yellow
        Set-Content -Path $pyVersionFile -Value "3.13"
        Write-Host "[SUCCESS] Updated to Python 3.13" -ForegroundColor Green
    }
} else {
    Write-Host "[INFO] Creating .python-version file..."
    Set-Content -Path $pyVersionFile -Value "3.13"
}
Write-Host ""

# [3/6] Create/Sync Virtual Environment
Write-Host "[3/6] Creating/Syncing virtual environment..."
$venvPython = ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "[INFO] Virtual environment exists. Checking for updates..."
    
    if ($USE_UV) {
        Write-Host "[INFO] Attempting uv sync..."
        $syncResult = uv sync 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARNING] uv sync failed. Falling back to pip update..." -ForegroundColor Yellow
            & $venvPython -m pip install -e . -q
        } else {
            Write-Host "[SUCCESS] Sync completed using uv." -ForegroundColor Green
        }
    } else {
        Write-Host "[INFO] Updating dependencies using pip..."
        & $venvPython -m pip install -e . -q
    }
} else {
    Write-Host "[INFO] Creating new virtual environment..."
    
    if ($USE_UV) {
        Write-Host "[INFO] Attempting creation with uv sync..."
        uv sync 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Environment created using uv." -ForegroundColor Green
            # Skip to next section
        } else {
            Write-Host "[WARNING] uv sync failed. Falling back to traditional method..." -ForegroundColor Yellow
            python -m venv .venv
        }
    } else {
        python -m venv .venv
    }

    # Verify creation if we fell back or didn't use uv successfully
    if (-not (Test-Path $venvPython)) {
        # Try one last time explicitly if uv failed and we didn't retry above logic correctly
        if (-not (Test-Path $venvPython)) {
             python -m venv .venv
        }
    }

    if (-not (Test-Path $venvPython)) {
        Write-Host "[ERROR] Failed to create virtual environment." -ForegroundColor Red
        Write-Host "[TIP] Please ensure Python 3.11+ is installed and in PATH." -ForegroundColor Cyan
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "[INFO] Installing project dependencies (this may take a few minutes)..."
    & $venvPython -m pip install --upgrade pip -q
    & $venvPython -m pip install -e . -q
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Dependency installation failed." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[SUCCESS] Virtual environment created." -ForegroundColor Green
}

Write-Host "[SUCCESS] Virtual environment ready." -ForegroundColor Green
Write-Host ""

$PYTHON_CMD = $venvPython

# [4/6] Start Docker Compose (Milvus)
Write-Host "[4/6] Starting Milvus Vector Database..."

# PowerShell handles {{ }} naturally, no escaping needed!
$milvusRunning = docker ps --format "{{.Names}}" | Select-String "milvus-standalone"

if ($milvusRunning) {
    Write-Host "[INFO] Milvus container is already running."
} else {
    Write-Host "[INFO] Starting Milvus container..."
    docker compose -f vector-database.yml up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to start Docker. Please ensure Docker Desktop is running." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "[INFO] Waiting for Milvus to start (10s)..."
    Start-Sleep -Seconds 10
}
Write-Host "[SUCCESS] Milvus database ready." -ForegroundColor Green
Write-Host ""

# [5/6] Start CLS MCP Service
Write-Host "[5/6] Starting CLS MCP Service..."
Start-Process -FilePath $PYTHON_CMD -ArgumentList "mcp_servers/cls_server.py" -WindowStyle Minimized -PassThru | Out-Null
Start-Sleep -Seconds 2
Write-Host "[SUCCESS] CLS MCP Service started." -ForegroundColor Green
Write-Host ""

# [6/6] Start Monitor MCP Service
Write-Host "[6/6] Starting Monitor MCP Service..."
Start-Process -FilePath $PYTHON_CMD -ArgumentList "mcp_servers/monitor_server.py" -WindowStyle Minimized -PassThru | Out-Null
Start-Sleep -Seconds 2
Write-Host "[SUCCESS] Monitor MCP Service started." -ForegroundColor Green
Write-Host ""

# [7/8] Start FastAPI Service
Write-Host "[7/8] Starting FastAPI Service..."
Start-Process -FilePath $PYTHON_CMD -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9900" -PassThru | Out-Null

Write-Host "[INFO] Waiting for service startup (15s)..."
Start-Sleep -Seconds 15
Write-Host ""

# [8/8] Check Status and Upload Documents
Write-Host "[INFO] Checking service status..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9900/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "[SUCCESS] FastAPI service is running normally." -ForegroundColor Green
        Write-Host ""
        
        Write-Host "[8/8] Uploading documents to vector database..."
        $docsPath = "aiops-docs\*.md"
        $files = Get-Item $docsPath -ErrorAction SilentlyContinue
        
        if ($files) {
            foreach ($file in $files) {
                Write-Host "   Uploading: $($file.Name)"
                # Using curl.exe explicitly to match batch behavior, or Invoke-WebRequest
                # Here we use curl.exe if available, otherwise fallback logic could be added
                $curlArgs = "-s", "-X", "POST", "http://localhost:9900/api/upload", "-F", "file=@$($file.FullName)"
                & curl.exe $curlArgs 2>$null
            }
            Write-Host "[SUCCESS] Document upload complete." -ForegroundColor Green
        } else {
            Write-Host "[INFO] No .md files found in aiops-docs folder. Skipping upload." -ForegroundColor Yellow
        }
    } else {
        throw "Status code: $($response.StatusCode)"
    }
} catch {
    Write-Host "[WARNING] Service might not be fully ready yet or health check failed." -ForegroundColor Yellow
    Write-Host "   Error: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "===================================="
Write-Host "Service Startup Complete!" -ForegroundColor Green
Write-Host "===================================="
Write-Host "Web Interface: http://localhost:9900"
Write-Host "API Docs:      http://localhost:9900/docs"
Write-Host ""
Write-Host "View Logs:"
Write-Host "  - FastAPI: logs\app_*.log"
Write-Host "  - CLS MCP: Check terminal or log files"
Write-Host "  - Monitor: Check terminal or log files"
Write-Host "Stop Services: Close the terminal windows or run stop script"
Write-Host "===================================="

# Keep window open if run directly
Read-Host "Press Enter to close this window"