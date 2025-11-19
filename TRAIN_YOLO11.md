# Training Custom YOLOv11 for Thread Roll Detection

## Current Status

✅ **YOLOv11 Nano (pre-trained) is installed**
- Location: `backend/app/models_weights/best.pt`
- Type: General-purpose COCO model (80 object classes)
- Size: 5.4 MB

⚠️ **Important**: This pre-trained model will detect general objects but is NOT optimized for thread rolls. For production use, you should train your own model.

---

## Why Train a Custom Model?

The pre-trained YOLOv11 model:
- ✅ Works as a demo/placeholder
- ✅ Can detect some cylindrical objects
- ❌ Not trained specifically on thread rolls
- ❌ May miss thread rolls or misclassify them
- ❌ Won't be optimized for your specific setup

A custom-trained model will:
- ✅ Accurately detect YOUR thread rolls
- ✅ Work with YOUR lighting conditions
- ✅ Handle YOUR rack setup
- ✅ Provide better confidence scores
- ✅ Reduce false positives/negatives

---

## Step-by-Step Training Guide

### Step 1: Collect Images (Minimum 100-300 images)

**What to photograph:**
- Thread rolls in the square rack
- Various lighting conditions
- Different fill levels (full rack, partial)
- Different angles
- Different thread colors

**Tips:**
- Use the same camera you'll use in production
- Take photos at the same distance/angle
- Include some empty rack images
- Include some cluttered backgrounds
- More diverse images = better model

### Step 2: Annotate Your Images

Use one of these tools to draw bounding boxes around each thread roll:

#### Option A: Roboflow (Recommended - Easiest)
1. Go to https://roboflow.com (free account)
2. Create a new project: "Thread Roll Detection"
3. Upload your images
4. Use the annotation tool to draw boxes around each thread roll
5. Label each box as "thread_roll"
6. Export in "YOLOv11" format
7. Download the dataset

#### Option B: CVAT (Free, Self-hosted)
1. Install CVAT: https://cvat.ai
2. Create a new task
3. Upload images
4. Draw bounding boxes, label as "thread_roll"
5. Export in YOLO 1.1 format

#### Option C: LabelImg (Offline Tool)
```bash
pip install labelImg
labelImg
```
- Open your image folder
- Draw boxes, save in YOLO format

### Step 3: Prepare Dataset Structure

After annotation, organize your dataset:

```
thread_roll_dataset/
├── data.yaml
├── train/
│   ├── images/
│   │   ├── img1.jpg
│   │   ├── img2.jpg
│   │   └── ...
│   └── labels/
│       ├── img1.txt
│       ├── img2.txt
│       └── ...
└── val/
    ├── images/
    └── labels/
```

**data.yaml** should contain:
```yaml
path: /full/path/to/thread_roll_dataset
train: train/images
val: val/images

nc: 1  # number of classes
names: ['thread_roll']  # class names
```

### Step 4: Train YOLOv11

Create a training script `train_thread_rolls.py`:

```python
from ultralytics import YOLO

# Load YOLOv11 nano model
model = YOLO('yolo11n.pt')

# Train the model
results = model.train(
    data='thread_roll_dataset/data.yaml',  # path to your data.yaml
    epochs=100,                              # number of training epochs
    imgsz=640,                               # image size
    batch=16,                                # batch size (reduce if out of memory)
    name='thread_roll_v1',                   # name of the training run
    patience=20,                             # early stopping patience
    save=True,                               # save checkpoints
    device=0,                                # GPU device (use 'cpu' if no GPU)
    workers=8,                               # number of data loading workers
    pretrained=True,                         # use pre-trained weights
    optimizer='auto',                        # optimizer
    verbose=True,                            # verbose output
    seed=42,                                 # random seed for reproducibility
    # Data augmentation (helps with small datasets)
    hsv_h=0.015,                            # image HSV-Hue augmentation
    hsv_s=0.7,                              # image HSV-Saturation augmentation
    hsv_v=0.4,                              # image HSV-Value augmentation
    degrees=10.0,                           # rotation augmentation
    translate=0.1,                          # translation augmentation
    scale=0.5,                              # scaling augmentation
    fliplr=0.5,                             # horizontal flip probability
    mosaic=1.0,                             # mosaic augmentation probability
)

print("\n" + "="*60)
print("Training Complete!")
print("="*60)
print(f"Best model saved at: {results.save_dir}/weights/best.pt")
print("\nTo use this model, copy it to:")
print("  backend/app/models_weights/best.pt")
```

Run training:
```bash
cd "/home/shibin/Desktop/object counting/backend"
python3 train_thread_rolls.py
```

**Training time:**
- CPU: 1-3 hours (for 100 epochs)
- GPU: 10-30 minutes (for 100 epochs)

### Step 5: Evaluate the Model

After training, test your model:

```python
from ultralytics import YOLO

# Load your trained model
model = YOLO('runs/detect/thread_roll_v1/weights/best.pt')

# Validate on test images
metrics = model.val()

print(f"Precision: {metrics.box.p}")
print(f"Recall: {metrics.box.r}")
print(f"mAP50: {metrics.box.map50}")
print(f"mAP50-95: {metrics.box.map}")

# Test on a sample image
results = model.predict('test_image.jpg', save=True, conf=0.4)
```

### Step 6: Deploy Your Trained Model

```bash
# Copy your trained model
cp runs/detect/thread_roll_v1/weights/best.pt backend/app/models_weights/best.pt

# Backend will automatically reload and use the new model
```

---

## Quick Training with Roboflow

If you use Roboflow, they provide a training notebook:

1. Annotate images in Roboflow
2. Generate dataset → Export → YOLOv11 format
3. Use their provided training notebook (one-click training)
4. Download the trained `best.pt`
5. Copy to `backend/app/models_weights/best.pt`

---

## Tips for Better Accuracy

1. **More data is better**: 200-500 images > 50 images
2. **Balanced dataset**: Equal examples of all scenarios
3. **Augmentation**: Use HSV, rotation, flip augmentations
4. **Multiple training runs**: Try different hyperparameters
5. **Monitor training**: Watch for overfitting (train loss ≫ val loss)
6. **Test thoroughly**: Test on completely new images

---

## Model Size Options

Choose based on your needs:

| Model    | Size | Speed | Accuracy | Use Case |
|----------|------|-------|----------|----------|
| yolo11n  | 5MB  | Fast  | Good     | Mobile, Edge devices |
| yolo11s  | 18MB | Fast  | Better   | Balanced |
| yolo11m  | 40MB | Med   | Great    | Desktop app |
| yolo11l  | 50MB | Slow  | Better   | High accuracy needed |
| yolo11x  | 100MB| Slowest| Best    | Maximum accuracy |

For thread rolls, **yolo11n** or **yolo11s** is usually sufficient.

---

## Current Setup (For Testing)

The installed YOLOv11n pre-trained model will:
- Detect general objects in images
- May detect some thread rolls as "bottle", "cup", or "vase"
- Good for testing the application flow
- Should be replaced with a custom-trained model for production

You can start using the application now with the pre-trained model, then swap it out later when you have a custom-trained one!

---

## Need Help?

- Ultralytics Docs: https://docs.ultralytics.com
- Roboflow University: https://roboflow.com/learn
- YOLOv11 Training Tutorial: https://docs.ultralytics.com/modes/train/
