"""Common schemas, logging, I/O, and utilities."""
from src.common.schemas import (
    BoundingBox,
    Detection,
    Terminal,
    Component,
    WireSegment,
    Junction,
    SkeletonGraphData,
    Net,
    ComponentEdge,
    CircuitGraph,
    EvaluationMetrics
)
from src.common.logging import logger, setup_logger
from src.common.io import (
    load_json,
    save_json,
    load_yaml,
    save_yaml,
    load_image,
    save_image,
    ensure_dir,
    PipelineCache
)
from src.common.utils import (
    euclidean_dist,
    rotate_point,
    unit_vector,
    dot_product,
    compute_iou,
    bbox_distance
)
