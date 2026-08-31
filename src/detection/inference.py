"""inference.py: Batch and Tiled Inference Helper for High-Resolution Images."""

from typing import List, Optional
import numpy as np

from src.common.schemas import Detection
from src.detection.detector import YOLO11Detector


class CircuitInferenceEngine:
    """Runs batch or tiled symbol detection on full circuit images."""

    def __init__(self, detector: Optional[YOLO11Detector] = None):
        self.detector = detector or YOLO11Detector()

    def predict_image(self, image: np.ndarray, image_id: Optional[str] = None) -> List[Detection]:
        """Runs symbol detection pipeline."""
        return self.detector.detect(image, image_id=image_id)
