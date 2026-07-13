@echo off
cd /d C:\KonCoOS\business-os
docker compose up --build -d
echo.
echo ============================================
echo  Business OS запущен!
echo  Backend API:  http://localhost:8000
echo  Mini App:     http://localhost:3000
echo  API Docs:     http://localhost:8000/docs
echo ============================================
pause
