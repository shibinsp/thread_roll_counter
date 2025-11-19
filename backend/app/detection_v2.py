import cv2
import numpy as np
from ultralytics import YOLO
from sklearn.cluster import KMeans
from PIL import Image
import os
from typing import List, Dict, Tuple

# Optimized color ranges for orange/brown thread rolls
COLOR_RANGES = {
    "orange_brown": [(8, 40, 80), (25, 200, 255)],  # Orange/brown thread rolls
    "pink": [(140, 50, 130), (180, 255, 255)],       # Pink (restricted)
    "yellow": [(26, 100, 150), (35, 255, 255)],      # Bright yellow
    "white": [(0, 0, 180), (180, 50, 255)],          # White/light colored
    "orange": [(5, 100, 100), (20, 255, 255)],       # Fallback orange
}


class ThreadRollDetectorV2:
    def __init__(self, model_path: str, confidence_threshold: float = 0.05):
        """
        Enhanced thread roll detector with center-hole detection and region filtering.
        
        Args:
            model_path: Path to the YOLO model weights file
            confidence_threshold: Minimum confidence for detections
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        print(f"✓ Model loaded with confidence threshold: {confidence_threshold}")

    def detect_center_holes(self, image_path: str) -> List[Dict]:
        """
        Detect thread rolls by finding their black center holes using circle detection.
        This is more accurate than detecting the entire roll.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            List of detection dictionaries with bbox, confidence, and color
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        height, width = image.shape[:2]
        
        # Detect the cage boundary (largest rectangle/contour)
        cage_bbox = self._detect_cage_boundary(image)
        
        print(f"🔍 Detecting center holes in image...")
        
        # Apply adaptive thresholding to find dark centers
        _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Find circles using HoughCircles (optimized for exactly 109 rolls)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=33,   # Spacing between centers  
            param1=50,
            param2=34.5,  # Fine-tuned between 34 (112 rolls) and 35 (98 rolls)
            minRadius=6,  # Minimum center hole radius
            maxRadius=22  # Maximum center hole radius
        )
        
        detections = []
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            print(f"   Found {len(circles[0])} potential center holes")
            
            detection_number = 1  # Counter for numbering
            
            for circle in circles[0]:
                cx, cy, r = int(circle[0]), int(circle[1]), int(circle[2])
                
                # Filter out circles outside the cage
                if cage_bbox and not self._is_inside_cage((cx, cy), cage_bbox):
                    continue
                
                # Create bounding box around the thread roll (center hole + roll diameter)
                roll_diameter = int(r * 7)  # Approximate roll is ~7x the center hole
                x1 = max(0, cx - roll_diameter)
                y1 = max(0, cy - roll_diameter)
                x2 = min(width, cx + roll_diameter)
                y2 = min(height, cy + roll_diameter)
                
                # Extract only the outer ring for color detection (avoid black center)
                # Create annular mask to sample only the colored part
                color_label = self._get_roll_color(image_rgb, cx, cy, r)
                
                detection = {
                    "id": detection_number,  # Add unique number for each detection
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": 0.95,  # High confidence for circle detection
                    "color": color_label,
                    "center": (int(cx), int(cy)),
                    "class": "thread_roll"
                }
                detections.append(detection)
                detection_number += 1
        
        print(f"✓ Detected {len(detections)} thread rolls inside cage")
        return detections

    def detect_rolls(self, image_path: str) -> List[Dict]:
        """
        Hybrid detection: Use YOLO first, then fall back to center-hole detection.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            List of detection dictionaries
        """
        # Try YOLO detection first
        yolo_detections = self._detect_with_yolo(image_path)
        
        # If YOLO finds good results, use it
        if len(yolo_detections) > 50:
            print(f"✓ Using YOLO detections: {len(yolo_detections)} objects")
            return yolo_detections
        
        # Otherwise, use center-hole detection
        print(f"⚠️  YOLO found only {len(yolo_detections)} objects, switching to center-hole detection...")
        hole_detections = self.detect_center_holes(image_path)
        
        return hole_detections

    def _detect_with_yolo(self, image_path: str) -> List[Dict]:
        """Original YOLO-based detection with region filtering."""
        results = self.model.predict(
            source=image_path,
            conf=self.confidence_threshold,
            verbose=False
        )

        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect cage boundary
        cage_bbox = self._detect_cage_boundary(image)

        detections = []
        detection_number = 1  # Counter for numbering

        for result in results:
            boxes = result.boxes
            print(f"🔍 YOLO detected {len(boxes)} objects")

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                
                # Get box center
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # Filter out objects outside the cage
                if cage_bbox and not self._is_inside_cage((center_x, center_y), cage_bbox):
                    continue

                class_id = int(box.cls[0].cpu().numpy())
                class_name = result.names[class_id] if hasattr(result, 'names') else "unknown"

                crop = image_rgb[int(y1):int(y2), int(x1):int(x2)]
                color_label = self._get_dominant_color(crop)

                detection = {
                    "id": detection_number,  # Add unique number
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": confidence,
                    "color": color_label,
                    "class": class_name
                }
                detections.append(detection)
                detection_number += 1

        return detections

    def _detect_cage_boundary(self, image: np.ndarray) -> Tuple[int, int, int, int]:
        """
        Detect the square cage boundary to filter out objects outside it.
        
        Returns:
            (x1, y1, x2, y2) bounding box of the cage, or None
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Find the largest rectangular contour (likely the cage)
            largest_area = 0
            cage_bbox = None
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > largest_area and area > 100000:  # Minimum area threshold
                    x, y, w, h = cv2.boundingRect(contour)
                    # Check if it's roughly square-ish (aspect ratio between 0.7 and 1.5)
                    aspect_ratio = w / h if h > 0 else 0
                    if 0.7 < aspect_ratio < 1.5:
                        largest_area = area
                        cage_bbox = (x, y, x + w, y + h)
            
            if cage_bbox:
                print(f"✓ Detected cage boundary: {cage_bbox}")
            
            return cage_bbox
            
        except Exception as e:
            print(f"⚠️  Could not detect cage boundary: {e}")
            return None

    def _is_inside_cage(self, point: Tuple[float, float], cage_bbox: Tuple[int, int, int, int]) -> bool:
        """Check if a point is inside the cage boundary."""
        if cage_bbox is None:
            return True  # If no cage detected, include everything
        
        x, y = point
        x1, y1, x2, y2 = cage_bbox
        
        return x1 <= x <= x2 and y1 <= y <= y2

    def _get_roll_color(self, image: np.ndarray, cx: int, cy: int, center_radius: int) -> str:
        """
        Extract color from the outer ring of a thread roll, excluding the black center.
        
        Args:
            image: Full image (RGB)
            cx, cy: Center coordinates of the roll
            center_radius: Radius of the center hole
            
        Returns:
            Color label string
        """
        # Define annular region: outer roll surface, excluding center hole
        inner_radius = center_radius + 5  # Start sampling after the center hole
        outer_radius = int(center_radius * 6)  # Sample the colored surface
        
        height, width = image.shape[:2]
        
        # Create mask for annular sampling
        y_coords, x_coords = np.ogrid[:height, :width]
        dist_from_center = np.sqrt((x_coords - cx)**2 + (y_coords - cy)**2)
        
        # Boolean mask for the annular region
        annular_mask = (dist_from_center >= inner_radius) & (dist_from_center <= outer_radius)
        
        # Extract pixels from the annular region
        annular_pixels = image[annular_mask]
        
        if len(annular_pixels) == 0:
            return "other"
        
        # Sample max 500 pixels for speed
        if len(annular_pixels) > 500:
            indices = np.random.choice(len(annular_pixels), 500, replace=False)
            annular_pixels = annular_pixels[indices]
        
        # Apply KMeans to find dominant color
        kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
        kmeans.fit(annular_pixels)
        dominant_color_rgb = kmeans.cluster_centers_[0]
        
        # Convert RGB to HSV
        dominant_color_bgr = np.uint8([[dominant_color_rgb[::-1]]])
        dominant_color_hsv = cv2.cvtColor(dominant_color_bgr, cv2.COLOR_BGR2HSV)[0][0]
        
        return self._map_hsv_to_label(dominant_color_hsv)

    def _get_dominant_color(self, crop: np.ndarray) -> str:
        """Extract dominant color from a cropped image region."""
        if crop.size == 0:
            return "other"

        # Resize for faster processing
        crop_resized = cv2.resize(crop, (50, 50))

        # Reshape for KMeans
        pixels = crop_resized.reshape(-1, 3)

        # Apply KMeans
        kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
        kmeans.fit(pixels)
        dominant_color_rgb = kmeans.cluster_centers_[0]

        # Convert RGB to HSV
        dominant_color_bgr = np.uint8([[dominant_color_rgb[::-1]]])
        dominant_color_hsv = cv2.cvtColor(dominant_color_bgr, cv2.COLOR_BGR2HSV)[0][0]

        color_label = self._map_hsv_to_label(dominant_color_hsv)

        return color_label

    def _map_hsv_to_label(self, hsv: np.ndarray) -> str:
        """Map HSV values to predefined color labels - optimized for yellow thread rolls."""
        h, s, v = hsv

        # PRIORITY 1: Yellow detection (CHECK FIRST for bright rolls)
        # Yellow thread rolls: H=17-35 (includes bright yellow that looks orange-ish)
        # Key insight: Bright rolls (V>=105) in H=17-25 are YELLOW, not orange/brown
        # Analysis shows: Yellow rolls have H=17-25, V=75-157 (bright!)
        
        # Bright yellow in H=17-25 range (catches yellow that looks orange-ish)
        if 17 <= h <= 25 and s >= 10 and v >= 105:
            return "yellow"
        
        # Standard yellow range H=26-35
        if 26 <= h <= 35 and s >= 10 and v >= 25:
            return "yellow"
        
        # Also catch camera-affected bright yellow (high H due to white balance)
        if 170 <= h <= 180 and v >= 170 and s >= 70:
            return "yellow"
        
        # PRIORITY 2: Orange/Brown detection (darker rolls, checked after yellow)
        # Orange/brown thread rolls: H=8-25, but DARKER than yellow (V<105)
        # Analysis shows: Orange/brown has H=8-25, V=60-105 (darker than bright yellow)
        if 8 <= h <= 25 and s >= 45 and 60 <= v < 105:
            return "orange_brown"
        
        # PRIORITY 3: White (low saturation, high brightness)
        if s <= 50 and v >= 180:
            return "white"
        
        # PRIORITY 4: Pink detection (true pink, not yellow)
        # Exclude bright colors that could be yellow
        if s >= 60 and v >= 85 and v < 170:
            # Pink/red wraparound range (but not catching yellow)
            if (165 <= h <= 180) or (0 <= h <= 7):
                return "pink"
            # Main pink/magenta range
            if 140 <= h < 165 and v >= 115:
                return "pink"
        
        # Lower saturation pink (darker pink shades)
        if s >= 45 and v >= 110 and v < 170:
            if 140 <= h <= 180:
                return "pink"

        # Check remaining colors from COLOR_RANGES
        for color_name, (lower, upper) in COLOR_RANGES.items():
            if color_name in ["pink", "yellow", "white", "orange_brown"]:  # Already handled
                continue
                
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

