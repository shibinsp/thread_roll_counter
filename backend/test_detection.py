#!/usr/bin/env python3
"""
Test YOLO detection on uploaded images to see what it detects
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from detection import ThreadRollDetector
import glob

def test_uploaded_images():
    """Test detection on all uploaded images."""

    model_path = "app/models_weights/best.pt"
    uploads_dir = "app/uploads"

    if not os.path.exists(model_path):
        print("❌ Model file not found")
        return

    print("=" * 60)
    print("Testing YOLO Detection on Uploaded Images")
    print("=" * 60)

    # Get all uploaded images
    image_files = glob.glob(os.path.join(uploads_dir, "*.jp*g")) + \
                  glob.glob(os.path.join(uploads_dir, "*.png"))

    if not image_files:
        print("\n⚠️  No images found in uploads directory")
        print(f"Upload some images via the app first: http://localhost:3000")
        return

    print(f"\nFound {len(image_files)} uploaded images\n")

    # Test each confidence threshold
    thresholds = [0.15, 0.25, 0.35, 0.5]

    for threshold in thresholds:
        print(f"\n{'=' * 60}")
        print(f"Testing with confidence threshold: {threshold}")
        print('=' * 60)

        detector = ThreadRollDetector(model_path, confidence_threshold=threshold)

        for img_path in image_files[:3]:  # Test first 3 images
            filename = os.path.basename(img_path)
            print(f"\n📸 Image: {filename}")

            try:
                detections = detector.detect_rolls(img_path)

                if detections:
                    print(f"   ✓ Found {len(detections)} objects:")
                    for i, det in enumerate(detections, 1):
                        print(f"      {i}. {det.get('class', 'unknown')} - "
                              f"{det['color']} "
                              f"(conf: {det['confidence']:.2f})")
                else:
                    print("   ✗ No objects detected")

            except Exception as e:
                print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Recommendations:")
    print("=" * 60)
    print("""
If NO objects are detected at any threshold:
  → Your images don't contain objects from the COCO dataset
  → You MUST train a custom YOLOv11 model on thread rolls
  → See TRAIN_YOLO11.md for instructions

If SOME objects are detected (bottles, cups, etc.):
  → The model is working, but seeing wrong objects
  → Still need to train a custom model for thread rolls

If MANY objects are detected at low threshold:
  → Adjust threshold in backend/app/main.py
  → Use the threshold that works best for your images
    """)


if __name__ == "__main__":
    test_uploaded_images()
