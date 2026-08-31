"""schema.py: Data Schemas and Confidence Bucketing Enums for Graph Analysis Module."""

from enum import Enum
from typing import List, Dict, Tuple, Optional, Any
from pydantic import BaseModel, Field


class ConfidenceBucket(str, Enum):
    """Confidence categorization buckets."""
    HIGH = "HIGH"         # 0.90 - 1.00
    MEDIUM = "MEDIUM"     # 0.70 - 0.89
    LOW = "LOW"           # < 0.70


def get_confidence_bucket(score: float) -> ConfidenceBucket:
    """Classifies confidence score into HIGH, MEDIUM, or LOW bucket."""
    if score >= 0.90:
        return ConfidenceBucket.HIGH
    elif score >= 0.70:
        return ConfidenceBucket.MEDIUM
    else:
        return ConfidenceBucket.LOW


class ConfidenceNode(BaseModel):
    """Confidence-annotated component node schema."""
    component_id: str
    type: str
    class_id: int = 0
    detection_confidence: float
    confidence_bucket: ConfidenceBucket
    bbox: List[float] = Field(default_factory=list) # [xmin, ymin, xmax, ymax]
    center: Tuple[float, float] = (0.0, 0.0)
    orientation: float = 0.0
    value: Optional[str] = None
    terminals: List[Dict[str, Any]] = Field(default_factory=list)


class ConfidenceEdge(BaseModel):
    """Confidence-annotated connection edge schema between component terminals."""
    id: str
    source_component: str
    source_terminal: str
    target_component: str
    target_terminal: str
    net_id: str
    connection_confidence: float
    confidence_bucket: ConfidenceBucket


class CircuitError(BaseModel):
    """Deterministic structural circuit error item with pixel coordinates."""
    error_id: str
    component_id: str
    terminal_id: Optional[str] = None
    error_type: str
    severity: str = "warning"  # "confirmed" or "warning"
    message: str
    location: Tuple[float, float] = (0.0, 0.0) # (x, y) pixel coordinates in original image
    is_possible_detection_error: bool = False


class SubcircuitGroup(BaseModel):
    """Subcircuit connected component group."""
    subcircuit_id: str
    components: List[str] = Field(default_factory=list)
    nets: List[str] = Field(default_factory=list)
    is_connected: bool = True


class SimplificationResult(BaseModel):
    """Circuit simplification equivalent representation."""
    pattern_type: str
    original_components: List[str] = Field(default_factory=list)
    equivalent_label: str
    formula_text: str


class AnalysisReport(BaseModel):
    """Structured Analysis Payload consumed by Debugger UI."""
    image_id: str
    overall_confidence: float
    overall_bucket: ConfidenceBucket
    nodes: List[ConfidenceNode] = Field(default_factory=list)
    edges: List[ConfidenceEdge] = Field(default_factory=list)
    errors: List[CircuitError] = Field(default_factory=list)
    subcircuits: List[SubcircuitGroup] = Field(default_factory=list)
    simplifications: List[SimplificationResult] = Field(default_factory=list)
