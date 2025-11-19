# Thread Roll Counter

AI-powered thread roll detection and counting application using YOLOv11, FastAPI, and React.

## Features

- **Image Upload**: Upload or capture images using mobile camera
- **AI Detection**: YOLO-based object detection for thread rolls
- **Color Classification**: Automatic color detection (pink, yellow, orange, white, other)
- **Results Visualization**: Bounding boxes and color-coded detection results
- **Record Management**: View, update, and manage past detection records
- **Mobile-First Design**: Responsive UI optimized for mobile devices
- **RESTful API**: Complete backend API for all operations

## Tech Stack

### Frontend
- React 18
- Axios for API communication
- Custom CSS with mobile-first responsive design
- Color Theme: Blues (#2E5E99, #7BA4D0, #E7F0FA)

### Backend
- FastAPI
- SQLAlchemy ORM
- SQLite database
- Ultralytics YOLOv11/v8
- OpenCV & scikit-learn for color detection

## Project Structure

```
object counting/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # SQLAlchemy models
│   │   ├── detection.py         # YOLO & color detection logic
│   │   ├── uploads/             # Uploaded images storage
│   │   └── models_weights/      # YOLO model weights
│   │       └── best.pt          # ⚠️ Place your trained model here
│   ├── requirements.txt
│   └── thread_rolls.db          # SQLite database (auto-created)
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUpload.js
│   │   │   ├── Results.js
│   │   │   └── RecordsList.js
│   │   ├── App.js
│   │   ├── index.js
│   │   ├── index.css
│   │   └── api.js
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn
- YOLO model weights file (`best.pt`)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Place YOLO model weights**:
   - Copy your trained YOLO model weights file
   - Place it at: `backend/app/models_weights/best.pt`
   - **⚠️ IMPORTANT**: The application will not work without this file!

5. **Run the backend server**:
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at: `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure API URL** (optional):
   - Create `.env` file in frontend directory
   - Add: `REACT_APP_API_URL=http://localhost:8000`
   - Default is already set to localhost:8000

4. **Run the development server**:
   ```bash
   npm start
   ```

   The app will open at: `http://localhost:3000`

## Usage

### 1. Upload Image
- Click the upload area or drag and drop an image
- On mobile, you can use the camera to capture directly
- Supports JPG, PNG, WEBP formats

### 2. Add Details (Optional)
- Enter your name
- Add description/notes about the detection

### 3. Detect Thread Rolls
- Click "Detect Thread Rolls" button
- Wait for AI processing (typically 1-3 seconds)
- View results with:
  - Total count
  - Color breakdown
  - Bounding boxes on image
  - Confidence scores

### 4. View Past Records
- Scroll down to see all previous detections
- Click any record to view full details
- Records are sorted by most recent first

## API Endpoints

### POST /predict
Upload image for detection
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@image.jpg" \
  -F "user=John Doe" \
  -F "description=Batch A"
```

**Response**:
```json
{
  "id": 1,
  "total_count": 15,
  "color_counts": {
    "pink": 5,
    "yellow": 4,
    "white": 3,
    "orange": 2,
    "other": 1
  },
  "detections": [...],
  "image_filename": "20250118_120000_image.jpg",
  "user": "John Doe",
  "description": "Batch A",
  "created_at": "2025-01-18T12:00:00"
}
```

### GET /records
Get all detection records
```bash
curl http://localhost:8000/records
```

### GET /records/{id}
Get single record
```bash
curl http://localhost:8000/records/1
```

### PATCH /records/{id}
Update record description
```bash
curl -X PATCH http://localhost:8000/records/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}'
```

### DELETE /records/{id}
Delete a record
```bash
curl -X DELETE http://localhost:8000/records/1
```

## Color Detection

The application uses KMeans clustering and HSV color mapping to classify thread rolls into the following colors:

- **Pink**: HSV range [140-170, 50-255, 50-255]
- **Yellow**: HSV range [20-30, 100-255, 100-255]
- **Orange**: HSV range [10-20, 100-255, 100-255]
- **White**: HSV range [0-180, 0-30, 200-255]
- **Other**: Any color not matching above ranges

### Calibrating Color Ranges

If the color detection is not accurate for your specific thread rolls, you can adjust the HSV ranges in `backend/app/detection.py`:

```python
COLOR_RANGES = {
    "pink": [(140, 50, 50), (170, 255, 255)],
    "yellow": [(20, 100, 100), (30, 255, 255)],
    "orange": [(10, 100, 100), (20, 255, 255)],
    "white": [(0, 0, 200), (180, 30, 255)],
}
```

Use sample images to calibrate these ranges for best results.

## Model Training

To train your own YOLO model:

1. Collect images of thread rolls in the square rack
2. Annotate using tools like CVAT, Roboflow, or LabelImg
3. Train using Ultralytics YOLO:
   ```python
   from ultralytics import YOLO

   model = YOLO('yolov11n.pt')  # or yolov8n.pt
   model.train(data='dataset.yaml', epochs=100, imgsz=640)
   ```
4. Copy the best weights to `backend/app/models_weights/best.pt`

## Troubleshooting

### Backend Issues

**Error: "Model file not found"**
- Ensure `best.pt` exists at `backend/app/models_weights/best.pt`
- Check file permissions

**Error: "Module not found"**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

**Slow inference**
- Use a smaller YOLO model (yolov11n instead of yolov11x)
- Reduce image size before processing
- Use GPU if available (install CUDA-enabled PyTorch)

### Frontend Issues

**Cannot connect to backend**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Verify `REACT_APP_API_URL` in frontend

**Images not displaying**
- Check that `/uploads` directory has proper permissions
- Verify backend static file mounting is working

## Production Deployment

### Backend
- Use gunicorn or uvicorn with multiple workers
- Set up proper CORS origins (not `"*"`)
- Use PostgreSQL instead of SQLite for production
- Add authentication/authorization
- Set up file storage (S3, Azure Blob, etc.)

### Frontend
- Build for production: `npm run build`
- Serve using nginx or similar
- Configure proper API URL in environment variables
- Enable HTTPS

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions, please check:
1. This README file
2. FastAPI documentation: `http://localhost:8000/docs`
3. Ultralytics YOLO docs: https://docs.ultralytics.com

## Version

**v1.0.0** - Initial release with YOLO detection, color classification, and full CRUD API
