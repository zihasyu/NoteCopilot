@echo off
echo ==========================================
echo NoteCopilot Stopper
echo ==========================================
echo.

echo [INFO] Stopping Docker services...
docker-compose down
@REM docker-compose down --remove-orphans --volumes 
echo.
echo [OK] All services stopped.
echo.
pause
