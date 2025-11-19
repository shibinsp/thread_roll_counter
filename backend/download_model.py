#!/usr/bin/env python3
"""
Download YOLOv11 pre-trained model for Thread Roll Counter

This script downloads a pre-trained YOLOv11 model from Ultralytics.
For production use, you should train your own model on your specific thread roll images.
"""

from ultralytics import YOLO
import os

# Model options:
# yolo11n.pt - Nano (smallest, fastest)
# yolo11s.pt - Small
# yolo11m.pt - Medium
# yolo11l.pt - Large
# yolo11x.pt - Extra Large (best accuracy, slowest)

MODEL_NAME = "yolo11n.pt"  # Using nano for speed
SAVE_PATH = "app/models_weights/best.pt"

def download_model():
    """Download YOLOv11 model and save it to the models_weights directory."""

    print("=" * 60)
    print("YOLOv11 Model Download")
    print("=" * 60)
    print(f"\nDownloading {MODEL_NAME}...")
    print("This may take a few minutes depending on your connection.\n")

    try:
        # Load the model (this will download it if not present)
        model = YOLO(MODEL_NAME)

        print(f"✓ Model downloaded successfully")
        print(f"  Model: {MODEL_NAME}")
        print(f"  Type: YOLOv11 Nano")

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

        # Save to the expected location
        model.save(SAVE_PATH)

        print(f"\n✓ Model saved to: {SAVE_PATH}")
        print("\n" + "=" * 60)
        print("IMPORTANT NOTES:")
        print("=" * 60)
        print("""
This is a GENERAL-PURPOSE pre-trained YOLOv11 model.
It was trained on the COCO dataset and can detect 80 common objects.

⚠️  For THREAD ROLL detection specifically, you should:

1. Collect images of your thread rolls in the square rack
2. Annotate them using a tool like:
   - Roboflow (https://roboflow.com)
   - CVAT (https://cvat.ai)
   - LabelImg (https://github.com/heartexlabs/labelImg)

3. Train a custom YOLOv11 model:

   from ultralytics import YOLO

   model = YOLO('yolo11n.pt')
   results = model.train(
       data='your_dataset.yaml',
       epochs=100,
       imgsz=640,
       batch=16,
       name='thread_roll_detector'
   )

4. Replace this model with your trained model

For now, this pre-trained model will work as a placeholder
and can detect general objects, but it won't be optimized
for thread rolls specifically.
""")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Error downloading model: {e}")
        return False


if __name__ == "__main__":
    success = download_model()
    exit(0 if success else 1)
