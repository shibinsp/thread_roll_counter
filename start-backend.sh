#!/bin/bash

# Thread Roll Counter - Backend Startup Script

echo "========================================="
echo "Thread Roll Counter - Backend Setup"
echo "========================================="
echo ""

# Check if venv exists
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv backend/venv
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to create virtual environment."
        echo "Please run: sudo apt install -y python3.12-venv"
        echo ""
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r backend/requirements.txt

# Check for YOLO model
if [ ! -f "backend/app/models_weights/best.pt" ]; then
    echo ""
    echo "⚠️  WARNING: YOLO model not found!"
    echo "Please place your trained YOLO model at:"
    echo "  backend/app/models_weights/best.pt"
    echo ""
    echo "The API will start but predictions will fail without the model."
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Start the backend server
echo ""
echo "Starting FastAPI backend server..."
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
