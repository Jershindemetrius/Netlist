"""terminal_estimator.py: Hybrid Class-Aware Terminal Estimation."""

import math
from typing import List, Tuple, Optional
import numpy as np
import cv2

from src.common.schemas import BoundingBox, Terminal, Component, Detection
from src.common.utils import rotate_point
from src.geometry.terminal_templates import TerminalTemplateManager
from src.geometry.orientation import OrientationEstimator


class TerminalEstimator:
    """Estimates terminal positions and directions for detected components."""

    def __init__(self, template_manager: Optional[TerminalTemplateManager] = None):
        self.template_manager = template_manager or TerminalTemplateManager()
        self.orientation_estimator = OrientationEstimator()

    def estimate_terminals(
        self,
        component_id: str,
        detection: Detection,
        image: Optional[np.ndarray] = None,
        wire_mask: Optional[np.ndarray] = None
    ) -> Component:
        """Calculates precise image-coordinate terminals for a detected component."""
        bbox = detection.bbox
        class_name = detection.class_name
        
        # 1. Orientation estimation
        orientation, ori_conf = self.orientation_estimator.estimate_orientation(
            image=image,
            bbox=bbox,
            class_name=class_name,
            annotated_rotation=detection.rotation
        )

        # 2. Get class template
        template = self.template_manager.get_template(class_name)
        raw_terminals = template.get("terminals", [])

        # 3. Transform normalized terminal positions to rotated image coordinates
        terminals: List[Terminal] = []
        center_x, center_y = bbox.center

        for t_spec in raw_terminals:
            t_id = t_spec["id"]
            sem_name = t_spec["name"]
            norm_pos = t_spec["position"]  # [u, v] in [0, 1]
            raw_dir = t_spec.get("direction", [0.0, 0.0])

            # Unrotated absolute position relative to bounding box
            unrot_x = bbox.xmin + norm_pos[0] * bbox.width
            unrot_y = bbox.ymin + norm_pos[1] * bbox.height

            # Rotate around component center by orientation angle
            rot_x, rot_y = rotate_point((unrot_x, unrot_y), orientation, (center_x, center_y))

            # Rotate outward normal direction vector
            rad = math.radians(orientation)
            dir_x = raw_dir[0] * math.cos(rad) - raw_dir[1] * math.sin(rad)
            dir_y = raw_dir[0] * math.sin(rad) + raw_dir[1] * math.cos(rad)

            # Optional boundary pixel refinement using wire_mask if available
            refined_pos = (rot_x, rot_y)
            term_conf = ori_conf * detection.confidence

            if wire_mask is not None:
                refined_pos, score_bonus = self._refine_with_wire_pixels(
                    (rot_x, rot_y), wire_mask, search_radius=8
                )
                term_conf = min(1.0, term_conf + score_bonus)

            terminals.append(
                Terminal(
                    id=t_id,
                    semantic_name=sem_name,
                    position=refined_pos,
                    normalized_position=(norm_pos[0], norm_pos[1]),
                    direction=(dir_x, dir_y),
                    confidence=term_conf
                )
            )

        return Component(
            id=component_id,
            type=class_name,
            class_id=detection.class_id,
            bbox=bbox,
            center=(center_x, center_y),
            orientation=orientation,
            orientation_confidence=ori_conf,
            confidence=detection.confidence,
            terminals=terminals
        )

    def _refine_with_wire_pixels(
        self,
        predicted_pos: Tuple[float, float],
        wire_mask: np.ndarray,
        search_radius: int = 8
    ) -> Tuple[Tuple[float, float], float]:
        """Refines terminal position by searching for nearby foreground wire pixels."""
        px, py = int(round(predicted_pos[0])), int(round(predicted_pos[1]))
        h, w = wire_mask.shape[:2]

        y1 = max(0, py - search_radius)
        y2 = min(h, py + search_radius + 1)
        x1 = max(0, px - search_radius)
        x2 = min(w, px + search_radius + 1)

        patch = wire_mask[y1:y2, x1:x2]
        fg_coords = np.column_stack(np.where(patch > 0))

        if len(fg_coords) == 0:
            return (predicted_pos, 0.0)

        # Find closest foreground pixel
        patch_center = (py - y1, px - x1)
        dists = np.hypot(fg_coords[:, 0] - patch_center[0], fg_coords[:, 1] - patch_center[1])
        min_idx = np.argmin(dists)
        best_coord = fg_coords[min_idx]

        refined_x = float(x1 + best_coord[1])
        refined_y = float(y1 + best_coord[0])

        return ((refined_x, refined_y), 0.1)
