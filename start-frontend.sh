#!/bin/bash

# Thread Roll Counter - Frontend Startup Script

echo "========================================="
echo "Thread Roll Counter - Frontend Setup"
echo "========================================="
echo ""

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing npm dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start the frontend server
echo ""
echo "Starting React development server..."
echo "Frontend will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd frontend
npm start
