#!/usr/bin/env python3
"""
Interactive Image Annotation Tool for Thread Rolls
Click and drag to draw bounding boxes around thread rolls
"""

import cv2
import os
import glob
from pathlib import Path

class ImageAnnotator:
    def __init__(self, image_dir, output_dir):
        self.image_dir = image_dir
        self.output_dir = output_dir
        self.current_image = None
        self.current_image_path = None
        self.clone = None
        self.boxes = []
        self.drawing = False
        self.start_point = None
        self.current_box = None

        # Get all images
        self.image_files = sorted(glob.glob(os.path.join(image_dir, "*.jp*g")))
        self.current_index = 0

    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for drawing bounding boxes."""

        if event == cv2.EVENT_LBUTTONDOWN:
            # Start drawing
            self.drawing = True
            self.start_point = (x, y)
            self.current_box = [x, y, x, y]

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                # Update current box
                self.current_box[2] = x
                self.current_box[3] = y

        elif event == cv2.EVENT_LBUTTONUP:
            # Finish drawing
            self.drawing = False
            self.current_box[2] = x
            self.current_box[3] = y

            # Add box if it's valid (not too small)
            if abs(self.current_box[2] - self.current_box[0]) > 10 and \
               abs(self.current_box[3] - self.current_box[1]) > 10:
                self.boxes.append(self.current_box[:])
                print(f"✓ Added box #{len(self.boxes)}: {self.current_box}")

            self.current_box = None

    def draw_boxes(self, image):
        """Draw all saved boxes and current box on image."""
        img = image.copy()

        # Draw saved boxes (green)
        for box in self.boxes:
            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            cv2.putText(img, f"Thread Roll", (box[0], box[1]-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Draw current box being drawn (yellow)
        if self.current_box:
            cv2.rectangle(img, (self.current_box[0], self.current_box[1]),
                         (self.current_box[2], self.current_box[3]), (0, 255, 255), 2)

        return img

    def save_annotations(self):
        """Save annotations in YOLO format."""
        if not self.boxes or not self.current_image_path:
            return

        # Get image dimensions
        h, w = self.current_image.shape[:2]

        # Convert boxes to YOLO format
        yolo_boxes = []
        for box in self.boxes:
            # Convert to x_center, y_center, width, height (normalized 0-1)
            x_center = ((box[0] + box[2]) / 2) / w
            y_center = ((box[1] + box[3]) / 2) / h
            width = abs(box[2] - box[0]) / w
            height = abs(box[3] - box[1]) / h

            # Class 0 for thread_roll
            yolo_boxes.append(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        # Save annotation file
        filename = Path(self.current_image_path).stem
        label_path = os.path.join(self.output_dir, 'labels', f"{filename}.txt")

        with open(label_path, 'w') as f:
            f.write('\n'.join(yolo_boxes))

        print(f"✓ Saved {len(yolo_boxes)} annotations to {label_path}")

    def load_image(self, index):
        """Load image at given index."""
        if index < 0 or index >= len(self.image_files):
            return False

        # Save previous annotations
        if self.boxes:
            self.save_annotations()

        # Load new image
        self.current_index = index
        self.current_image_path = self.image_files[index]
        self.current_image = cv2.imread(self.current_image_path)
        self.clone = self.current_image.copy()
        self.boxes = []

        # Copy image to output images folder
        filename = Path(self.current_image_path).name
        output_image_path = os.path.join(self.output_dir, 'images', filename)
        cv2.imwrite(output_image_path, self.current_image)

        print(f"\n{'='*60}")
        print(f"Image {index + 1}/{len(self.image_files)}: {filename}")
        print(f"{'='*60}")

        return True

    def run(self):
        """Run the annotation tool."""
        if not self.image_files:
            print("❌ No images found in directory!")
            return

        print("\n" + "="*60)
        print("Thread Roll Annotation Tool")
        print("="*60)
        print("\nControls:")
        print("  - Click and drag to draw bounding box")
        print("  - 'n' = Next image")
        print("  - 'p' = Previous image")
        print("  - 'u' = Undo last box")
        print("  - 'c' = Clear all boxes")
        print("  - 's' = Save and next")
        print("  - 'q' = Quit")
        print("="*60)

        # Create window
        cv2.namedWindow("Annotate Thread Rolls")
        cv2.setMouseCallback("Annotate Thread Rolls", self.mouse_callback)

        # Load first image
        self.load_image(0)

        while True:
            # Draw boxes on image
            display = self.draw_boxes(self.current_image)

            # Add info text
            info_text = f"Image {self.current_index + 1}/{len(self.image_files)} | Boxes: {len(self.boxes)}"
            cv2.putText(display, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, "Press 'h' for help", (10, display.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Annotate Thread Rolls", display)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                # Quit
                self.save_annotations()
                break

            elif key == ord('n'):
                # Next image
                self.load_image(self.current_index + 1)

            elif key == ord('p'):
                # Previous image
                self.load_image(self.current_index - 1)

            elif key == ord('u'):
                # Undo last box
                if self.boxes:
                    removed = self.boxes.pop()
                    print(f"✗ Removed box: {removed}")

            elif key == ord('c'):
                # Clear all boxes
                self.boxes = []
                print("✗ Cleared all boxes")

            elif key == ord('s'):
                # Save and next
                self.save_annotations()
                self.load_image(self.current_index + 1)

            elif key == ord('h'):
                # Show help
                print("\nControls:")
                print("  - Click and drag to draw bounding box")
                print("  - 'n' = Next image")
                print("  - 'p' = Previous image")
                print("  - 'u' = Undo last box")
                print("  - 'c' = Clear all boxes")
                print("  - 's' = Save and next")
                print("  - 'q' = Quit\n")

        cv2.destroyAllWindows()

        print("\n" + "="*60)
        print("Annotation Complete!")
        print("="*60)
        print(f"Annotated {len(glob.glob(os.path.join(self.output_dir, 'labels', '*.txt')))} images")
        print(f"Saved to: {self.output_dir}")


if __name__ == "__main__":
    import sys

    image_dir = "/home/shibin/Desktop/object counting/sample_images_for_training"
    output_dir = "/home/shibin/Desktop/object counting/thread_roll_dataset/train"

    # Create output directories
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'labels'), exist_ok=True)

    annotator = ImageAnnotator(image_dir, output_dir)
    annotator.run()
