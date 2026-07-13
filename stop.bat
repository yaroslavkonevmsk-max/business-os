@echo off
cd /d "%~dp0"
echo [Business OS] Stopping all services...
docker compose down
echo.
echo ============================================
echo  Business OS stopped.
echo ============================================
pause
