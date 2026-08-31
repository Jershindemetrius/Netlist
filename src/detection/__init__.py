"""Detection, inference, NMS postprocessing, and training modules."""
from src.detection.detector import BaseDetector, YOLO11Detector
from src.detection.inference import CircuitInferenceEngine
from src.detection.postprocess import apply_nms
