#!/usr/bin/env python3
"""
Auto-annotate thread roll images using current YOLO model
This creates initial annotations that can be used for training
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from ultralytics import YOLO
import glob
from pathlib import Path
import shutil

def auto_annotate_images():
    """Auto-annotate images using pre-trained YOLO model."""

    # Paths
    image_dir = "/home/shibin/Desktop/object counting/sample_images_for_training"
    output_dir = "/home/shibin/Desktop/object counting/thread_roll_dataset"
    model_path = "backend/app/models_weights/best.pt"

    print("=" * 60)
    print("Auto-Annotation Tool for Thread Rolls")
    print("=" * 60)

    # Load YOLO model
    print(f"\n📦 Loading YOLO model...")
    model = YOLO(model_path)

    # Get all images
    image_files = glob.glob(os.path.join(image_dir, "*.jp*g")) + \
                  glob.glob(os.path.join(image_dir, "*.png"))

    if not image_files:
        print("❌ No images found!")
        return

    print(f"✓ Found {len(image_files)} images")

    # Split into train/val (80/20)
    split_idx = int(len(image_files) * 0.8)
    train_images = image_files[:split_idx]
    val_images = image_files[split_idx:]

    print(f"  - Train: {len(train_images)} images")
    print(f"  - Val: {len(val_images)} images")

    # Process train images
    print(f"\n🔍 Auto-annotating training images...")
    annotate_split(model, train_images, os.path.join(output_dir, 'train'))

    # Process val images
    print(f"\n🔍 Auto-annotating validation images...")
    annotate_split(model, val_images, os.path.join(output_dir, 'val'))

    # Create data.yaml
    print(f"\n📝 Creating data.yaml...")
    create_data_yaml(output_dir)

    print("\n" + "=" * 60)
    print("✓ Auto-annotation Complete!")
    print("=" * 60)
    print(f"\nDataset saved to: {output_dir}")
    print(f"Train images: {len(train_images)}")
    print(f"Val images: {len(val_images)}")
    print(f"\n⚠️  Note: Auto-annotations may not be perfect.")
    print("Review and manually correct if needed before training.")


def annotate_split(model, image_files, output_dir):
    """Annotate a split of images."""

    # Create directories
    images_dir = os.path.join(output_dir, 'images')
    labels_dir = os.path.join(output_dir, 'labels')
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    for i, image_path in enumerate(image_files, 1):
        filename = Path(image_path).stem
        print(f"  [{i}/{len(image_files)}] {Path(image_path).name}...", end=' ')

        # Copy image
        dest_image = os.path.join(images_dir, Path(image_path).name)
        shutil.copy(image_path, dest_image)

        # Run prediction with low confidence to catch all objects
        results = model.predict(image_path, conf=0.1, verbose=False)

        # Convert to YOLO format
        yolo_annotations = []

        for result in results:
            boxes = result.boxes
            if len(boxes) == 0:
                print("⚠️  No detections")
                continue

            # Get image dimensions
            h, w = result.orig_shape

            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                # Convert to YOLO format (class x_center y_center width height)
                x_center = ((x1 + x2) / 2) / w
                y_center = ((y1 + y2) / 2) / h
                width = abs(x2 - x1) / w
                height = abs(y2 - y1) / h

                # Class 0 for thread_roll
                yolo_annotations.append(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        # Save annotations
        label_path = os.path.join(labels_dir, f"{filename}.txt")

        if yolo_annotations:
            with open(label_path, 'w') as f:
                f.write('\n'.join(yolo_annotations))
            print(f"✓ {len(yolo_annotations)} boxes")
        else:
            # Create empty label file
            open(label_path, 'w').close()
            print("⚠️  No annotations (empty file created)")


def create_data_yaml(dataset_dir):
    """Create data.yaml configuration file."""

    yaml_content = f"""# Thread Roll Dataset
path: {dataset_dir}
train: train/images
val: val/images

# Classes
nc: 1  # number of classes
names: ['thread_roll']  # class names
"""

    yaml_path = os.path.join(dataset_dir, 'data.yaml')

    with open(yaml_path, 'w') as f:
        f.write(yaml_content)

    print(f"✓ Created {yaml_path}")


if __name__ == "__main__":
    auto_annotate_images()
