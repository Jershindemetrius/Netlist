"""skeleton.py: Morphological Skeletonization and Thinning for Wire Tracing."""

import numpy as np
from skimage.morphology import skeletonize


class WireSkeletonizer:
    """Computes 1-pixel wide morphological skeleton of binary circuit wire masks."""

    def __init__(self, method: str = "lee"):
        self.method = method

    def skeletonize(self, binary_mask: np.ndarray) -> np.ndarray:
        """Applies morphological skeletonization to a binary mask (0 or 255).
        
        Returns:
            np.ndarray: uint8 binary image where 255 represents skeleton paths, 0 is background.
        """
        # Convert to boolean mask
        bool_mask = binary_mask > 0
        
        # Apply scikit-image skeletonize
        try:
            skel = skeletonize(bool_mask, method=self.method)
        except Exception:
            skel = skeletonize(bool_mask)

        # Convert back to uint8 (0 / 255)
        return (skel.astype(np.uint8) * 255)
