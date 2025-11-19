import cv2
import numpy as np
from ultralytics import YOLO
from sklearn.cluster import KMeans
from PIL import Image
import os
from typing import List, Dict, Tuple

# Color label mapping using HSV ranges
COLOR_RANGES = {
    "pink": [(140, 50, 50), (170, 255, 255)],
    "yellow": [(20, 100, 100), (30, 255, 255)],
    "orange": [(10, 100, 100), (20, 255, 255)],
    "white": [(0, 0, 200), (180, 30, 255)],
}


class ThreadRollDetector:
    def __init__(self, model_path: str, confidence_threshold: float = 0.15):
        """
        Initialize the YOLO model for thread roll detection.

        Args:
            model_path: Path to the YOLO model weights file
            confidence_threshold: Minimum confidence for detections
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        print(f"✓ Model loaded with confidence threshold: {confidence_threshold}")

    def detect_rolls(self, image_path: str) -> List[Dict]:
        """
        Detect thread rolls in an image using YOLO.

        Args:
            image_path: Path to the input image

        Returns:
            List of detection dictionaries with bbox, confidence, and color
        """
        # Run YOLO inference
        results = self.model.predict(
            source=image_path,
            conf=self.confidence_threshold,
            verbose=False
        )

        # Load the original image for color extraction
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        detections = []

        # Process each detection
        for result in results:
            boxes = result.boxes
            print(f"🔍 YOLO detected {len(boxes)} objects in image")

            for box in boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())

                # Get class name
                class_id = int(box.cls[0].cpu().numpy())
                class_name = result.names[class_id] if hasattr(result, 'names') else "unknown"

                print(f"  → Detected: {class_name} (confidence: {confidence:.2f})")

                # Crop the detected region
                crop = image_rgb[int(y1):int(y2), int(x1):int(x2)]

                # Extract dominant color
                color_label = self._get_dominant_color(crop)

                detection = {
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": confidence,
                    "color": color_label,
                    "class": class_name  # Add detected class name
                }
                detections.append(detection)

        if len(detections) == 0:
            print("⚠️  No objects detected. Try:")
            print("   - Lowering confidence threshold")
            print("   - Using better lighting")
            print("   - Training a custom model for thread rolls")

        return detections

    def _get_dominant_color(self, crop: np.ndarray) -> str:
        """
        Extract dominant color from a cropped image region.

        Args:
            crop: Cropped image region (RGB)

        Returns:
            Color label string
        """
        if crop.size == 0:
            return "other"

        # Resize crop for faster processing
        crop_resized = cv2.resize(crop, (50, 50))

        # Reshape for KMeans
        pixels = crop_resized.reshape(-1, 3)

        # Apply KMeans to find dominant color
        kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
        kmeans.fit(pixels)
        dominant_color_rgb = kmeans.cluster_centers_[0]

        # Convert RGB to HSV for better color classification
        dominant_color_bgr = np.uint8([[dominant_color_rgb[::-1]]])
        dominant_color_hsv = cv2.cvtColor(dominant_color_bgr, cv2.COLOR_BGR2HSV)[0][0]

        # Map to color label
        color_label = self._map_hsv_to_label(dominant_color_hsv)

        return color_label

    def _map_hsv_to_label(self, hsv: np.ndarray) -> str:
        """
        Map HSV values to predefined color labels.

        Args:
            hsv: HSV color values [H, S, V]

        Returns:
            Color label string
        """
        h, s, v = hsv

        # Check each color range
        for color_name, (lower, upper) in COLOR_RANGES.items():
            lower = np.array(lower)
            upper = np.array(upper)

            if (lower[0] <= h <= upper[0] and
                lower[1] <= s <= upper[1] and
                lower[2] <= v <= upper[2]):
                return color_name

        return "other"

    def process_image(self, image_path: str) -> Dict:
        """
        Process an image and return detection results with color counts.

        Args:
            image_path: Path to the input image

        Returns:
            Dictionary with total_count, color_counts, and detections
        """
        detections = self.detect_rolls(image_path)

        # Count colors
        color_counts = {}
        for detection in detections:
            color = detection["color"]
            color_counts[color] = color_counts.get(color, 0) + 1

        return {
            "total_count": len(detections),
            "color_counts": color_counts,
            "detections": detections
        }
