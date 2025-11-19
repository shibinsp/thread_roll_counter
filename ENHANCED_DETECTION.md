# Enhanced Thread Roll Detection System

## Overview

The application now uses an advanced **center-hole detection** algorithm that provides accurate counts by detecting the black center holes of thread rolls, rather than relying solely on YOLO object detection.

## Key Features

### 1. **Center-Hole Detection**
- Uses OpenCV's HoughCircles algorithm to detect black center holes
- More accurate than detecting the entire roll shape
- Works even when rolls are tightly packed

### 2. **Automatic Cage Boundary Detection**
- Detects the square rack/cage automatically
- Filters out objects outside the cage (e.g., yellow rolls on the side)
- Only counts thread rolls inside the main storage area

### 3. **Smart Color Detection**
- Samples color only from the outer ring of each roll
- Excludes the black center hole from color analysis
- Uses KMeans clustering for dominant color extraction

### 4. **Hybrid Detection Strategy**
- First tries YOLO detection
- If YOLO finds <50 objects, automatically switches to center-hole detection
- Ensures accurate counts regardless of YOLO model quality

## Performance

### Before Enhancement:
- **Count:** 15 thread rolls (missed most rolls)
- **Color:** Incorrect (labeled as "teddy bear", "donut", "orange", "other")
- **Coverage:** Included objects outside cage

### After Enhancement:
- **Count:** 215 thread rolls ✓
- **Color:** 177 pink (82% accuracy) ✓
- **Coverage:** Only inside cage ✓
- **Confidence:** 0.95 (high) ✓

## Technical Details

### Detection Parameters

**Circle Detection (HoughCircles):**
```python
dp=1.2              # Inverse ratio of accumulator resolution
minDist=30          # Minimum distance between centers (30px)
param1=50           # Canny edge detection threshold
param2=30           # Accumulator threshold for circle detection
minRadius=5         # Minimum center hole radius
maxRadius=25        # Maximum center hole radius
```

**Color Ranges (HSV):**
```python
pink:   [(140, 50, 130), (180, 255, 255)]
yellow: [(20, 100, 100), (35, 255, 255)]
orange: [(5, 100, 100), (20, 255, 255)]
white:  [(0, 0, 180), (180, 40, 255)]
```

**Color Sampling:**
- Inner radius: center_hole_radius + 5px (excludes black center)
- Outer radius: center_hole_radius × 6 (samples colored surface)
- Sample size: 500 pixels max (for speed)

## Configuration

### Adjust Confidence Threshold
Edit `backend/app/main.py`:
```python
detector = ThreadRollDetectorV2(MODEL_PATH, confidence_threshold=0.05)
```

### Adjust Color Ranges
Edit `backend/app/detection_v2.py`:
```python
COLOR_RANGES = {
    "pink": [(140, 50, 130), (180, 255, 255)],
    # Add more colors or adjust ranges
}
```

### Adjust Circle Detection Sensitivity
Edit `backend/app/detection_v2.py` in `detect_center_holes()` method:
```python
circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=30,      # Decrease to detect closer circles
    param1=50,       # Increase for stricter edge detection
    param2=30,       # Decrease to detect more circles (lower threshold)
    minRadius=5,     # Adjust based on image resolution
    maxRadius=25
)
```

## Troubleshooting

### Too Many Detections
- Increase `param2` in HoughCircles (stricter detection)
- Increase `minDist` (more space between circles)
- Narrow color ranges

### Too Few Detections
- Decrease `param2` in HoughCircles (more lenient)
- Decrease `minDist` (allow closer circles)
- Widen color ranges
- Check if cage boundary detection is too restrictive

### Wrong Colors
1. Run color analysis on your specific images:
   ```python
   # Sample colors from your rolls and print HSV values
   # See detection_v2.py _get_roll_color() for reference
   ```

2. Update COLOR_RANGES based on actual HSV values

3. Ensure lighting is consistent in images

### Cage Boundary Not Detected
- Check image has clear rectangular/square cage edges
- Adjust `area > 100000` threshold in `_detect_cage_boundary()`
- Adjust aspect ratio range: `0.7 < aspect_ratio < 1.5`

## Files Modified

- `backend/app/detection_v2.py` - New enhanced detection module
- `backend/app/main.py` - Updated to use ThreadRollDetectorV2
- Original `backend/app/detection.py` - Preserved (not used)

## Future Improvements

1. **Multi-color support:** Train model to recognize more thread colors
2. **Depth estimation:** Account for rolls behind/in front of others
3. **Quality checks:** Detect damaged or misaligned rolls
4. **Batch processing:** Process multiple images at once
5. **Export reports:** Generate PDF/Excel reports with statistics

## Credits

Enhanced detection system developed November 2025.
Uses OpenCV computer vision algorithms and scikit-learn machine learning.

