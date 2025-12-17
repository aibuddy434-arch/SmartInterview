#!/bin/bash

# AI Interview Avatar System - Quick Start Script
# This script helps you get the system up and running quickly

echo "🚀 AI Interview Avatar System - Quick Start"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if MySQL is running
if ! mysqladmin ping -h localhost --silent 2>/dev/null; then
    echo "⚠️  MySQL is not running. Please start MySQL first."
    echo "   Windows: net start mysql"
    echo "   macOS: brew services start mysql"
    echo "   Linux: sudo systemctl start mysql"
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Backend setup
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials before continuing."
    echo "   Press Enter when ready to continue..."
    read
fi

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p uploads/resumes uploads/audio uploads/video

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "✅ Backend setup complete!"

# Frontend setup
echo ""
echo "🔧 Setting up Frontend..."
cd ../frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete!"

# Start services
echo ""
echo "🚀 Starting Services..."
echo ""

# Start backend in background
cd ../backend
source venv/bin/activate
echo "Starting backend server on http://localhost:8000..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
cd ../frontend
echo "Starting frontend server on http://localhost:3000..."
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 System is starting up!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Services stopped'; exit 0" INT

wait

