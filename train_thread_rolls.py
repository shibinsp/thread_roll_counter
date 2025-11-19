#!/usr/bin/env python3
"""
Train YOLOv11 model on thread roll dataset
"""

from ultralytics import YOLO
import os

def train_model():
    """Train YOLOv11 on thread roll dataset."""

    print("=" * 60)
    print("YOLOv11 Thread Roll Training")
    print("=" * 60)

    # Configuration
    data_yaml = "thread_roll_dataset/data.yaml"
    model_name = "yolo11n.pt"  # Using nano model for speed

    # Check if dataset exists
    if not os.path.exists(data_yaml):
        print("❌ Dataset not found! Run auto_annotate.py first")
        return

    print(f"\n📊 Dataset: {data_yaml}")
    print(f"🤖 Base model: {model_name}")

    # Load pre-trained YOLOv11 model
    print(f"\n📦 Loading base model...")
    model = YOLO(model_name)

    print(f"\n🚀 Starting training...")
    print("   This may take 5-15 minutes depending on your hardware")
    print("=" * 60)

    # Train the model with heavy augmentation for small dataset
    results = model.train(
        # Data
        data=data_yaml,

        # Training parameters
        epochs=100,              # Number of epochs (will use early stopping)
        patience=20,             # Early stopping patience
        batch=8,                 # Small batch for small dataset
        imgsz=640,               # Image size

        # Model saving
        save=True,               # Save checkpoints
        save_period=10,          # Save every 10 epochs

        # Device
        device='cpu',            # Use CPU (change to 0 for GPU)
        workers=4,               # Data loading workers

        # Optimization
        optimizer='auto',        # Auto-select optimizer
        lr0=0.001,              # Initial learning rate
        lrf=0.01,               # Final learning rate
        momentum=0.937,         # SGD momentum
        weight_decay=0.0005,    # Weight decay
        warmup_epochs=3,        # Warmup epochs

        # Augmentation (HEAVY for small dataset)
        hsv_h=0.02,             # HSV-Hue augmentation
        hsv_s=0.7,              # HSV-Saturation augmentation
        hsv_v=0.4,              # HSV-Value augmentation
        degrees=15.0,           # Rotation augmentation (+/- deg)
        translate=0.2,          # Translation augmentation (+/- fraction)
        scale=0.9,              # Scaling augmentation (+/- gain)
        shear=0.0,              # Shear augmentation (+/- deg)
        perspective=0.0001,     # Perspective augmentation
        flipud=0.5,             # Vertical flip probability
        fliplr=0.5,             # Horizontal flip probability
        mosaic=1.0,             # Mosaic augmentation probability
        mixup=0.2,              # MixUp augmentation probability
        copy_paste=0.3,         # Copy-paste augmentation probability

        # Other
        pretrained=True,        # Use pre-trained weights
        verbose=True,           # Verbose output
        seed=42,                # Random seed
        deterministic=True,     # Deterministic training
        single_cls=True,        # Single class dataset
        rect=False,             # Rectangular training
        cos_lr=True,            # Cosine learning rate scheduler
        close_mosaic=10,        # Disable mosaic for last N epochs
        amp=False,              # Automatic Mixed Precision (disable for CPU)

        # Project naming
        project='runs/train',
        name='thread_roll_v1',
        exist_ok=True,
    )

    print("\n" + "=" * 60)
    print("✓ Training Complete!")
    print("=" * 60)

    # Get best model path
    best_model_path = os.path.join('runs/train/thread_roll_v1/weights/best.pt')

    print(f"\n📍 Best model saved at:")
    print(f"   {best_model_path}")

    print(f"\n📊 Training Results:")
    print(f"   - Check metrics at: runs/train/thread_roll_v1/results.png")
    print(f"   - Check predictions at: runs/train/thread_roll_v1/val_batch*_pred.jpg")

    # Validation
    print(f"\n🔍 Validating model...")
    metrics = model.val()

    print(f"\n📈 Validation Metrics:")
    print(f"   - Precision: {metrics.box.p[0]:.3f}" if hasattr(metrics.box, 'p') else "   - Precision: N/A")
    print(f"   - Recall: {metrics.box.r[0]:.3f}" if hasattr(metrics.box, 'r') else "   - Recall: N/A")
    print(f"   - mAP50: {metrics.box.map50:.3f}" if hasattr(metrics.box, 'map50') else "   - mAP50: N/A")
    print(f"   - mAP50-95: {metrics.box.map:.3f}" if hasattr(metrics.box, 'map') else "   - mAP50-95: N/A")

    print(f"\n📦 To deploy the model:")
    print(f"   cp {best_model_path} backend/app/models_weights/best.pt")
    print(f"   (The backend will auto-reload)")

    return best_model_path


if __name__ == "__main__":
    train_model()
