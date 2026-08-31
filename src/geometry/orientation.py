"""orientation.py: Component Orientation Estimation."""

import math
from typing import Tuple, Optional
import numpy as np
import cv2

from src.common.schemas import BoundingBox


class OrientationEstimator:
    """Estimates the rotation/orientation of an electronic symbol."""

    def __init__(self):
        pass

    def estimate_orientation(
        self,
        image: Optional[np.ndarray],
        bbox: BoundingBox,
        class_name: str,
        annotated_rotation: Optional[float] = None
    ) -> Tuple[float, float]:
        """Estimates orientation angle in degrees and confidence score.
        
        Returns:
            (angle_degrees, confidence)
        """
        # If ground truth / predicted rotation was explicitly supplied, use it
        if annotated_rotation is not None:
            norm_angle = float(annotated_rotation % 360)
            return (norm_angle, 1.0)

        # Fallback to image crop analysis or aspect ratio
        w = bbox.width
        h = bbox.height

        if image is None or image.size == 0 or w < 5 or h < 5:
            # Fallback based purely on aspect ratio
            if h > 1.3 * w:
                return (90.0, 0.6)  # Likely vertical
            return (0.0, 0.6)       # Likely horizontal

        # Crop symbol patch
        ymin = int(max(0, bbox.ymin))
        ymax = int(min(image.shape[0], bbox.ymax))
        xmin = int(max(0, bbox.xmin))
        xmax = int(min(image.shape[1], bbox.xmax))

        crop = image[ymin:ymax, xmin:xmax]
        if crop.size == 0:
            return (0.0, 0.5)

        if len(crop.shape) == 3:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        else:
            gray = crop

        # Otsu thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(binary > 0))

        if len(coords) < 10:
            if h > 1.3 * w:
                return (90.0, 0.5)
            return (0.0, 0.5)

        # PCA on foreground stroke pixels
        mean = np.mean(coords, axis=0)
        centered = coords - mean
        cov = np.cov(centered, rowvar=False)
        evals, evecs = np.linalg.eigh(cov)
        
        # Primary axis vector (row=y, col=x)
        primary_vec = evecs[:, np.argmax(evals)]
        angle_rad = math.atan2(primary_vec[0], primary_vec[1])  # (dy, dx)
        angle_deg = math.degrees(angle_rad) % 180

        # Snap to nearest cardinal direction (0, 90, 180, 270)
        cardinal_angles = [0.0, 90.0, 180.0, 270.0]
        closest_angle = min(cardinal_angles, key=lambda a: min(abs(a - angle_deg), abs(a - (angle_deg + 180))))

        return (closest_angle, 0.75)
