"""schemas.py: Core Strongly-Typed Data Schemas for Project NETLIST.

Defines all central data structures for Detections, Terminals, Components, Wires,
Junctions, Nets, CircuitGraphs, and Evaluation Reports.
"""

from typing import List, Dict, Tuple, Optional, Any
from pydantic import BaseModel, Field
import numpy as np


class BoundingBox(BaseModel):
    """Bounding box in absolute image pixel coordinates [xmin, ymin, xmax, ymax]."""
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    @property
    def width(self) -> float:
        return max(0.0, self.xmax - self.xmin)

    @property
    def height(self) -> float:
        return max(0.0, self.ymax - self.ymin)

    @property
    def center(self) -> Tuple[float, float]:
        return ((self.xmin + self.xmax) / 2.0, (self.ymin + self.ymax) / 2.0)

    @property
    def area(self) -> float:
        return self.width * self.height

    def to_yolo(self, img_width: int, img_height: int) -> Tuple[float, float, float, float]:
        """Converts to normalized YOLO format (center_x, center_y, width, height) in [0, 1]."""
        cx = ((self.xmin + self.xmax) / 2.0) / img_width
        cy = ((self.ymin + self.ymax) / 2.0) / img_height
        w = self.width / img_width
        h = self.height / img_height
        return (
            float(np.clip(cx, 0.0, 1.0)),
            float(np.clip(cy, 0.0, 1.0)),
            float(np.clip(w, 0.0, 1.0)),
            float(np.clip(h, 0.0, 1.0))
        )

    @classmethod
    def from_yolo(cls, cx: float, cy: float, w: float, h: float, img_width: int, img_height: int) -> "BoundingBox":
        """Reconstructs absolute pixel BoundingBox from normalized YOLO coordinates."""
        abs_cx = cx * img_width
        abs_cy = cy * img_height
        abs_w = w * img_width
        abs_h = h * img_height
        return cls(
            xmin=abs_cx - abs_w / 2.0,
            ymin=abs_cy - abs_h / 2.0,
            xmax=abs_cx + abs_w / 2.0,
            ymax=abs_cy + abs_h / 2.0
        )


class Detection(BaseModel):
    """Output from symbol detector."""
    class_id: int
    class_name: str
    confidence: float = 1.0
    bbox: BoundingBox
    rotation: Optional[float] = None  # Degrees if annotated or predicted


class Terminal(BaseModel):
    """Terminal / port of an electronic component."""
    id: str                                     # e.g., "T1", "A", "K", "B", "C", "E"
    semantic_name: str                          # e.g., "anode", "cathode", "base", "connector"
    position: Tuple[float, float]               # Absolute image coordinates (x, y)
    normalized_position: Tuple[float, float] = (0.5, 0.5) # [0, 1] relative to component bbox
    direction: Optional[Tuple[float, float]] = None       # Outward normal vector (dx, dy)
    confidence: float = 1.0
    connected_net: Optional[str] = None         # Net identifier, e.g., "NET1"


class Component(BaseModel):
    """Electronic component with geometric location and terminals."""
    id: str                                     # Deterministic canonical ID (e.g. "R1", "C1", "D1")
    type: str                                   # Class name (e.g. "resistor", "diode.light_emitting")
    class_id: int
    bbox: BoundingBox
    center: Tuple[float, float]
    orientation: float = 0.0                    # Angle in degrees (0, 90, 180, 270 or continuous)
    orientation_confidence: float = 1.0
    confidence: float = 1.0
    value: Optional[str] = None                 # Optional SPICE value (e.g. "10k", "100uF")
    terminals: List[Terminal] = Field(default_factory=list)

    def get_terminal(self, terminal_id: str) -> Optional[Terminal]:
        for term in self.terminals:
            if term.id == terminal_id or term.semantic_name == terminal_id:
                return term
        return None


class WireSegment(BaseModel):
    """Tracing segment of an electrical wire line."""
    id: str
    points: List[Tuple[float, float]]           # Ordered sequence of pixel coordinates [(x, y)]
    start_point: Tuple[float, float]
    end_point: Tuple[float, float]
    length_pixels: float
    confidence: float = 1.0


class Junction(BaseModel):
    """Electrical junction point or visual crossing."""
    id: str
    position: Tuple[float, float]               # Image coordinate (x, y)
    degree: int                                 # Degree in skeleton graph (e.g. 3 for T-junction, 4 for X-junction)
    is_crossover: bool = False                  # True if determined to be non-connected crossing
    connected_wire_ids: List[str] = Field(default_factory=list)


class SkeletonGraphData(BaseModel):
    """Graph of morphological skeleton pixels, segments, endpoints, and junctions."""
    endpoints: List[Tuple[float, float]] = Field(default_factory=list)
    junctions: List[Junction] = Field(default_factory=list)
    wire_segments: List[WireSegment] = Field(default_factory=list)


class Net(BaseModel):
    """Electrical net grouping connected component terminals."""
    id: str                                     # e.g., "NET1", "NET2", "GND"
    terminals: List[str] = Field(default_factory=list) # e.g. ["R1.T1", "C1.POS", "V1.POS"]
    confidence: float = 1.0


class ComponentEdge(BaseModel):
    """Derived component-to-component connection edge preserving terminal metadata."""
    source_component: str                       # e.g., "R1"
    source_terminal: str                        # e.g., "T1"
    target_component: str                       # e.g., "C1"
    target_terminal: str                        # e.g., "POS"
    net_id: str                                 # e.g., "NET1"
    confidence: float = 1.0


class CircuitGraph(BaseModel):
    """Canonical circuit graph representation."""
    components: List[Component] = Field(default_factory=list)
    nets: Dict[str, List[str]] = Field(default_factory=dict) # net_id -> list of "CompID.TermID"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_canonical_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable canonical dictionary representation."""
        return {
            "components": [
                {
                    "id": c.id,
                    "type": c.type,
                    "class_id": c.class_id,
                    "bbox": [c.bbox.xmin, c.bbox.ymin, c.bbox.xmax, c.bbox.ymax],
                    "center": list(c.center),
                    "orientation": c.orientation,
                    "terminals": [
                        {
                            "id": t.id,
                            "semantic_name": t.semantic_name,
                            "position": list(t.position),
                            "net": t.connected_net
                        }
                        for t in c.terminals
                    ]
                }
                for c in sorted(self.components, key=lambda x: x.id)
            ],
            "nets": {
                k: sorted(v) for k, v in sorted(self.nets.items())
            },
            "metadata": self.metadata
        }

    def to_spice_netlist(self, title: str = "Extracted Circuit") -> str:
        """Exports standard SPICE-compatible text netlist."""
        lines = [f"* {title}", f"* Generated by Project NETLIST"]
        
        # Build mapping from "CompID.TermID" to net name
        term_to_net = {}
        for net_name, term_list in self.nets.items():
            for term_ref in term_list:
                term_to_net[term_ref] = net_name

        for comp in sorted(self.components, key=lambda x: x.id):
            cid = comp.id
            ctype = comp.type.lower()
            val = comp.value or "1"
            
            # Map terminals
            net_pins = []
            for t in comp.terminals:
                ref = f"{cid}.{t.id}"
                net_name = term_to_net.get(ref, "0" if "gnd" in ctype else f"UNCONNECTED_{ref}")
                net_pins.append(net_name)
            
            if len(net_pins) == 0:
                continue
            
            pin_str = " ".join(net_pins)
            lines.append(f"{cid} {pin_str} {val}")
            
        lines.append(".end")
        return "\n".join(lines)


class EvaluationMetrics(BaseModel):
    """Metrics comparing predicted CircuitGraph against ground truth."""
    ged_score: float = 0.0
    component_precision: float = 1.0
    component_recall: float = 1.0
    component_f1: float = 1.0
    net_precision: float = 1.0
    net_recall: float = 1.0
    net_f1: float = 1.0
    node_insertions: int = 0
    node_deletions: int = 0
    node_mismatches: int = 0
    edge_insertions: int = 0
    edge_deletions: int = 0
    details: Dict[str, Any] = Field(default_factory=dict)
