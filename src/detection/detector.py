"""detector.py: Model-Agnostic Symbol Detector Interface and YOLO11 Implementation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import numpy as np
import cv2

from src.common.schemas import Detection, BoundingBox
from src.common.logging import logger
from src.common.io import load_json, PipelineCache


class BaseDetector(ABC):
    """Model-agnostic detector interface for circuit components."""

    @abstractmethod
    def detect(self, image: np.ndarray) -> List[Detection]:
        """Runs symbol detection on an input image.
        
        Returns:
            List[Detection]: List of detected symbols with bounding box, class, and confidence.
        """
        pass


class YOLO11Detector(BaseDetector):
    """Ultralytics YOLO11 symbol detector with batch and optional tiled inference."""

    def __init__(
        self,
        weights_path: Optional[str] = "models/checkpoints/best.pt",
        classes_file: str = "classes.json",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        img_size: int = 960,
        device: str = "auto",
        cache: Optional[PipelineCache] = None
    ):
        self.weights_path = Path(weights_path) if weights_path else None
        self.classes_file = Path(classes_file)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.img_size = img_size
        self.device = device
        self.cache = cache
        self.model = None

        self.id_to_class: Dict[int, str] = {}
        self._load_classes()
        self._load_model()

    def _load_classes(self) -> None:
        if self.classes_file.exists():
            raw = load_json(self.classes_file)
            sorted_classes = sorted([(k, v) for k, v in raw.items() if k != "__background__"], key=lambda x: x[1])
            for idx, (name, _) in enumerate(sorted_classes):
                self.id_to_class[idx] = name
        else:
            self.id_to_class = {0: "resistor", 1: "capacitor.unpolarized", 2: "diode", 3: "voltage.dc", 4: "gnd"}

    def _load_model(self) -> None:
        if self.weights_path and self.weights_path.exists():
            try:
                from ultralytics import YOLO
                self.model = YOLO(str(self.weights_path))
                logger.info(f"Loaded YOLO model from {self.weights_path}")
            except Exception as e:
                logger.warning(f"Could not load YOLO model: {e}. Falling back to heuristic/mock mode.")
                self.model = None
        else:
            logger.info("YOLO weights not found. Operating in heuristic/stub mode.")
            self.model = None

    def detect(self, image: np.ndarray, image_id: Optional[str] = None) -> List[Detection]:
        """Detects symbols using YOLO11 or cached intermediate outputs."""
        if image_id and self.cache:
            cached_data = self.cache.get_json(image_id, "detections")
            if cached_data is not None:
                logger.debug(f"Loaded detections for {image_id} from cache.")
                return [Detection.model_validate(d) for d in cached_data]

        detections: List[Detection] = []

        if self.model is not None:
            results = self.model.predict(
                source=image,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                imgsz=self.img_size,
                verbose=False
            )
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()
                    cls_name = self.id_to_class.get(cls_id, f"class_{cls_id}")

                    detections.append(
                        Detection(
                            class_id=cls_id,
                            class_name=cls_name,
                            confidence=conf,
                            bbox=BoundingBox(
                                xmin=float(xyxy[0]),
                                ymin=float(xyxy[1]),
                                xmax=float(xyxy[2]),
                                ymax=float(xyxy[3])
                            )
                        )
                    )
        else:
            # Heuristic contour detection as fallback when model weights are not yet present
            detections = self._heuristic_fallback_detect(image)

        if image_id and self.cache:
            self.cache.set_json(image_id, "detections", [d.model_dump() for d in detections])

        return detections

    def _heuristic_fallback_detect(self, image: np.ndarray) -> List[Detection]:
        """Extracts candidate component bounding boxes from contour connected components."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if 20 < w < 250 and 20 < h < 250:
                detections.append(
                    Detection(
                        class_id=0,
                        class_name="resistor",
                        confidence=0.5,
                        bbox=BoundingBox(xmin=float(x), ymin=float(y), xmax=float(x + w), ymax=float(y + h))
                    )
                )

        return detections[:30]
