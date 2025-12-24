@echo off
title AI Interview System - Starting...

echo ========================================
echo    AI Interview Avatar System
echo ========================================
echo.

:: Check if MySQL is running (optional)
echo [1/3] Checking prerequisites...

:: Start Backend Server
echo [2/3] Starting Backend Server...
start "AI Interview Backend" cmd /k "cd /d D:\ai_avatar\backend && venv\scripts\activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

:: Wait for backend to start
timeout /t 5 /nobreak > nul

:: Start Frontend Server
echo [3/3] Starting Frontend Server...
start "AI Interview Frontend" cmd /k "cd /d D:\ai_avatar\frontend && npm start"

echo.
echo ========================================
echo    Servers Starting...
echo ========================================
echo.
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:3000
echo.
echo    Opening browser in 10 seconds...
echo ========================================

:: Wait for frontend to start
timeout /t 10 /nobreak > nul

:: Open browser
start http://localhost:3000

echo.
echo Both servers are running!
echo Close this window to stop the startup script.
echo (The servers will continue running in their own windows)
pause
