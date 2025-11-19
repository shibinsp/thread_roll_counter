# Quick Start Guide

Follow these steps to get the Thread Roll Counter running quickly.

## Step 1: Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Add Your YOLO Model

**⚠️ CRITICAL STEP** - The application won't work without this!

Place your trained YOLO model weights at:
```
backend/app/models_weights/best.pt
```

If you don't have a model yet:
- You can download a pre-trained YOLOv11 model from Ultralytics
- Or train your own using your thread roll images

## Step 3: Start the Backend

```bash
cd backend/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal running. The API will be at: http://localhost:8000

## Step 4: Install Frontend Dependencies

Open a **new terminal**:

```bash
cd frontend
npm install
```

## Step 5: Start the Frontend

```bash
npm start
```

The app will open automatically at: http://localhost:3000

## Step 6: Test the Application

1. Open http://localhost:3000 in your browser
2. Click "Upload Image" or drag & drop an image
3. Optionally add your name and description
4. Click "Detect Thread Rolls"
5. View the results with bounding boxes and color breakdown
6. Check past records at the bottom of the page

## Verify Everything Works

### Check Backend Health
Visit: http://localhost:8000
You should see: `{"message": "Thread Roll Counter API is running", "version": "1.0.0"}`

### Check API Documentation
Visit: http://localhost:8000/docs
You should see the interactive Swagger UI with all endpoints

### Test Image Upload
Use the frontend at http://localhost:3000 to upload an image

## Common Issues

### "Model file not found"
- Make sure `best.pt` exists at `backend/app/models_weights/best.pt`
- Check the file is not corrupted

### "Connection refused" or "Network Error"
- Make sure backend is running on port 8000
- Check firewall settings
- Verify no other service is using port 8000

### Frontend shows blank page
- Check browser console for errors (F12)
- Make sure Node.js version is 14 or higher
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and run `npm install` again

### Detection is slow
- Use a smaller YOLO model (yolov11n.pt)
- Reduce confidence threshold in `backend/app/main.py`
- Consider using GPU acceleration

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize color ranges for your specific thread rolls
- Train a custom YOLO model on your data for better accuracy
- Configure production deployment

## Development Tips

### Auto-reload
- Backend: Already enabled with `--reload` flag
- Frontend: React auto-reloads on file changes

### Debugging
- Backend logs appear in the terminal where uvicorn is running
- Frontend errors appear in browser console (F12)

### Testing API Directly
Use the Swagger UI at http://localhost:8000/docs to test endpoints without the frontend

Enjoy using Thread Roll Counter! 🧵
