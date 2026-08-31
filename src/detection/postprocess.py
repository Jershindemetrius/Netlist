"""postprocess.py: Non-Maximum Suppression (NMS) and Filtering."""

from typing import List
from src.common.schemas import Detection
from src.common.utils import compute_iou


def apply_nms(detections: List[Detection], iou_threshold: float = 0.45) -> List[Detection]:
    """Filters overlapping duplicate detections using class-specific NMS."""
    if not detections:
        return []

    # Group by class
    by_class = {}
    for d in detections:
        by_class.setdefault(d.class_id, []).append(d)

    kept: List[Detection] = []

    for cls_id, det_list in by_class.items():
        # Sort by confidence descending
        sorted_dets = sorted(det_list, key=lambda x: x.confidence, reverse=True)
        
        while sorted_dets:
            best = sorted_dets.pop(0)
            kept.append(best)
            
            best_box = [best.bbox.xmin, best.bbox.ymin, best.bbox.xmax, best.bbox.ymax]
            remaining = []
            for d in sorted_dets:
                d_box = [d.bbox.xmin, d.bbox.ymin, d.bbox.xmax, d.bbox.ymax]
                if compute_iou(best_box, d_box) < iou_threshold:
                    remaining.append(d)
            sorted_dets = remaining

    return kept
