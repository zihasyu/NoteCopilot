@echo off
echo ==========================================
echo NoteCopilot Reset
echo ==========================================
echo.

set /p confirm="This will DELETE all data. Continue? (y/N): "
if /i not "%confirm%"=="y" (
    echo [INFO] Cancelled.
    pause
    exit /b 0
)

echo [INFO] Stopping services...
docker-compose down 2>nul

echo [INFO] Removing Docker volumes...
docker volume rm notecopilot_etcd_data notecopilot_milvus_data notecopilot_minio_data 2>nul

echo [INFO] Cleaning checkpoints...
if exist checkpoints rmdir /s /q checkpoints
mkdir checkpoints

echo [INFO] Cleaning vector DB...
python -c "
import os
import shutil
for root, dirs, files in os.walk('.'):
    for d in dirs:
        if d == '__pycache__':
            shutil.rmtree(os.path.join(root, d))
"

echo.
echo [OK] Reset complete. Run start.bat to restart.
echo.
pause
