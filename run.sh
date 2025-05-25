#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Start backend server in the background
echo "Starting backend server..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install

# Start frontend server
echo "Starting frontend server..."
npm run dev

# When frontend server is stopped, kill the backend server
kill $BACKEND_PID
