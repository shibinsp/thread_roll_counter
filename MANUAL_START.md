# Manual Start Guide

## Prerequisites

First, install python3-venv:
```bash
sudo apt install -y python3.12-venv
```

## Starting the Backend

Open Terminal 1:
```bash
cd "/home/shibin/Desktop/object counting"

# Create virtual environment (first time only)
python3 -m venv backend/venv

# Activate virtual environment
source backend/venv/bin/activate

# Install dependencies (first time only)
pip install -r backend/requirements.txt

# Start the server
cd backend/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Starting the Frontend

Open Terminal 2:
```bash
cd "/home/shibin/Desktop/object counting/frontend"

# Install dependencies (first time only)
npm install

# Start the server
npm start
```

Frontend will open automatically at: http://localhost:3000

## ⚠️ Important Notes

1. **YOLO Model Required**: Place your trained YOLO model at:
   ```
   backend/app/models_weights/best.pt
   ```
   The app will run without it, but predictions will fail.

2. **Keep both terminals running**: You need both the backend and frontend running simultaneously.

3. **First time setup**: The installation steps only need to be done once. After that, you just need to activate the venv and start the servers.

## Quick Restart (After First Setup)

Backend:
```bash
cd "/home/shibin/Desktop/object counting/backend"
source venv/bin/activate
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd "/home/shibin/Desktop/object counting/frontend"
npm start
```
