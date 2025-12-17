@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 AI Interview Avatar System - Quick Start
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed!

REM Backend setup
echo.
echo 🔧 Setting up Backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your database credentials before continuing.
    echo    Press Enter when ready to continue...
    pause
)

REM Create uploads directory
echo Creating uploads directory...
if not exist "uploads" mkdir uploads
if not exist "uploads\resumes" mkdir uploads\resumes
if not exist "uploads\audio" mkdir uploads\audio
if not exist "uploads\video" mkdir uploads\video

REM Run database migrations
echo Running database migrations...
alembic upgrade head

echo ✅ Backend setup complete!

REM Frontend setup
echo.
echo 🔧 Setting up Frontend...
cd ..\frontend

REM Install dependencies
echo Installing Node.js dependencies...
npm install

echo ✅ Frontend setup complete!

REM Start services
echo.
echo 🚀 Starting Services...
echo.

REM Start backend in background
cd ..\backend
call venv\Scripts\activate.bat
echo Starting backend server on http://localhost:8000...
start "Backend Server" cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
cd ..\frontend
echo Starting frontend server on http://localhost:3000...
start "Frontend Server" cmd /k "npm start"

echo.
echo 🎉 System is starting up!
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause

