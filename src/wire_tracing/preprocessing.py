"""preprocessing.py: Image Preprocessing, Thresholding, and Component Masking for Wire Tracing."""

from typing import List, Tuple, Optional
import numpy as np
import cv2

from src.common.schemas import Component, BoundingBox


class WirePreprocessor:
    """Extracts clean binary wire mask from circuit photograph."""

    def __init__(
        self,
        blur_kernel: int = 3,
        adaptive_block_size: int = 25,
        adaptive_c: int = 10,
        mask_expansion: int = 4
    ):
        self.blur_kernel = blur_kernel
        self.adaptive_block_size = adaptive_block_size
        self.adaptive_c = adaptive_c
        self.mask_expansion = mask_expansion

    def preprocess(
        self,
        image: np.ndarray,
        components: Optional[List[Component]] = None
    ) -> np.ndarray:
        """Converts raw RGB circuit image to a binary wire foreground mask (255 = wire, 0 = bg)."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # 1. Denoise with bilateral or Gaussian filter
        blurred = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)

        # 2. Adaptive thresholding for uneven illumination in photographs
        binary = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            self.adaptive_block_size,
            self.adaptive_c
        )

        # 3. Mask out detected components to isolate wire network
        if components:
            binary = self.mask_components(binary, components)

        # 4. Remove tiny isolated noise specs
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        return binary

    def mask_components(
        self,
        binary_mask: np.ndarray,
        components: List[Component]
    ) -> np.ndarray:
        """Masks component bounding boxes while preserving wire pixels entering terminals."""
        wire_mask = binary_mask.copy()
        h, w = wire_mask.shape[:2]

        for comp in components:
            bbox = comp.bbox
            
            # Expanded bounding box
            x1 = int(max(0, bbox.xmin - self.mask_expansion))
            y1 = int(max(0, bbox.ymin - self.mask_expansion))
            x2 = int(min(w, bbox.xmax + self.mask_expansion))
            y2 = int(min(h, bbox.ymax + self.mask_expansion))

            # Erase component interior
            wire_mask[y1:y2, x1:x2] = 0

            # Restore wire pixels in small radius around each terminal
            for term in comp.terminals:
                tx, ty = int(round(term.position[0])), int(round(term.position[1]))
                t_radius = 8
                tx1 = max(0, tx - t_radius)
                ty1 = max(0, ty - t_radius)
                tx2 = min(w, tx + t_radius + 1)
                ty2 = min(h, ty + t_radius + 1)
                
                # Copy original binary pixels in terminal zone
                wire_mask[ty1:ty2, tx1:tx2] = binary_mask[ty1:ty2, tx1:tx2]

        return wire_mask
