"""utils.py: Geometric Math and Coordinate Transformation Utilities."""

import math
from typing import Tuple, List
import numpy as np


def euclidean_dist(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculates Euclidean distance between two 2D points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def rotate_point(
    point: Tuple[float, float],
    angle_degrees: float,
    center: Tuple[float, float] = (0.0, 0.0)
) -> Tuple[float, float]:
    """Rotates a point counter-clockwise by angle_degrees around a center point."""
    rad = math.radians(angle_degrees)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    
    px = point[0] - center[0]
    py = point[1] - center[1]
    
    rx = px * cos_a - py * sin_a
    ry = px * sin_a + py * cos_a
    
    return (rx + center[0], ry + center[1])


def unit_vector(vec: Tuple[float, float]) -> Tuple[float, float]:
    """Returns normalized unit vector."""
    mag = math.hypot(vec[0], vec[1])
    if mag < 1e-8:
        return (0.0, 0.0)
    return (vec[0] / mag, vec[1] / mag)


def dot_product(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    """Returns scalar dot product of two 2D vectors."""
    return v1[0] * v2[0] + v1[1] * v2[1]


def compute_iou(box1: List[float], box2: List[float]) -> float:
    """Computes Intersection over Union (IoU) between [xmin, ymin, xmax, ymax] boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection_w = max(0.0, x2 - x1)
    intersection_h = max(0.0, y2 - y1)
    intersection_area = intersection_w * intersection_h

    area1 = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
    area2 = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])
    union_area = area1 + area2 - intersection_area

    if union_area <= 0.0:
        return 0.0
    return float(intersection_area / union_area)


def bbox_distance(box1: List[float], box2: List[float]) -> float:
    """Calculates Euclidean distance between centers of two bounding boxes."""
    cx1 = (box1[0] + box1[2]) / 2.0
    cy1 = (box1[1] + box1[3]) / 2.0
    cx2 = (box2[0] + box2[2]) / 2.0
    cy2 = (box2[1] + box2[3]) / 2.0
    return math.hypot(cx1 - cx2, cy1 - cy2)
