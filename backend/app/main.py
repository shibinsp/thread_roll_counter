from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import os
import shutil
from pydantic import BaseModel

from database import get_db, init_db, Record
from detection_v2 import ThreadRollDetectorV2

# Initialize FastAPI app
app = FastAPI(title="Thread Roll Counter API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "models_weights", "best.pt")

# Create uploads directory if it doesn't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Initialize detector (will be loaded on first request)
detector = None


def get_detector():
    """Lazy load the YOLO detector."""
    global detector
    if detector is None:
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(
                status_code=500,
                detail=f"Model file not found at {MODEL_PATH}. Please place your YOLO model weights there."
            )
        detector = ThreadRollDetectorV2(MODEL_PATH, confidence_threshold=0.5)
    return detector


# Pydantic models for request/response
class RecordResponse(BaseModel):
    id: int
    image_filename: str
    total_count: int
    color_counts: dict
    detections: list
    description: Optional[str] = None
    user: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_record(cls, record: Record):
        """Create response from database record."""
        return cls(
            id=record.id,
            image_filename=record.image_filename,
            total_count=record.total_count,
            color_counts=record.color_counts,
            detections=record.raw_detection,
            description=record.description,
            user=record.user,
            created_at=record.created_at
        )


class UpdateDescriptionRequest(BaseModel):
    description: str


# API Endpoints

@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Thread Roll Counter API is running", "version": "1.0.0"}


@app.post("/predict", response_model=RecordResponse)
async def predict(
    file: UploadFile = File(...),
    user: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Predict thread rolls in an uploaded image.

    Args:
        file: Image file (multipart/form-data)
        user: Optional user name
        description: Optional description

    Returns:
        Detection results with total count, color breakdown, and bounding boxes
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOADS_DIR, filename)

    # Save uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Run YOLO detection
    try:
        det = get_detector()
        result = det.process_image(file_path)
    except Exception as e:
        # Clean up uploaded file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

    # Save to database
    record = Record(
        image_filename=filename,
        total_count=result["total_count"],
        color_counts=result["color_counts"],
        raw_detection=result["detections"],
        description=description,
        user=user,
        created_at=datetime.utcnow()
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Prepare response
    response_data = {
        "id": record.id,
        "image_filename": record.image_filename,
        "total_count": record.total_count,
        "color_counts": record.color_counts,
        "detections": record.raw_detection,
        "description": record.description,
        "user": record.user,
        "created_at": record.created_at
    }

    return response_data


@app.get("/records", response_model=List[RecordResponse])
def get_records(db: Session = Depends(get_db)):
    """
    Get all detection records, ordered by most recent first.

    Returns:
        List of all records
    """
    records = db.query(Record).order_by(Record.created_at.desc()).all()
    return [RecordResponse.from_record(record) for record in records]


@app.get("/records/{record_id}", response_model=RecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    """
    Get a single detection record by ID.

    Args:
        record_id: Record ID

    Returns:
        Single record
    """
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return RecordResponse.from_record(record)


@app.patch("/records/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    update_data: UpdateDescriptionRequest,
    db: Session = Depends(get_db)
):
    """
    Update the description of a record.

    Args:
        record_id: Record ID
        update_data: New description

    Returns:
        Updated record
    """
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    record.description = update_data.description
    db.commit()
    db.refresh(record)

    return RecordResponse.from_record(record)


@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """
    Delete a record and its associated image file.

    Args:
        record_id: Record ID

    Returns:
        Success message
    """
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Delete image file
    image_path = os.path.join(UPLOADS_DIR, record.image_filename)
    if os.path.exists(image_path):
        os.remove(image_path)

    # Delete database record
    db.delete(record)
    db.commit()

    return {"message": "Record deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
