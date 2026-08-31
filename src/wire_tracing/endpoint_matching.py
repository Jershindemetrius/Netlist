"""endpoint_matching.py: Confidence-Scored Wire Endpoint to Component Terminal Matching."""

import math
from typing import List, Tuple, Dict, Any, Optional
from src.common.schemas import Component, Terminal, WireSegment
from src.common.utils import euclidean_dist, unit_vector, dot_product


class EndpointMatcher:
    """Matches extracted wire endpoints to component terminals based on geometry and direction."""

    def __init__(
        self,
        max_snap_radius: float = 35.0,
        direction_weight: float = 0.35,
        distance_weight: float = 0.45,
        orientation_weight: float = 0.20,
        min_confidence: float = 0.30
    ):
        self.max_snap_radius = max_snap_radius
        self.direction_weight = direction_weight
        self.distance_weight = distance_weight
        self.orientation_weight = orientation_weight
        self.min_confidence = min_confidence

    def match_endpoint_to_terminals(
        self,
        endpoint: Tuple[float, float],
        wire_path: List[Tuple[float, float]],
        components: List[Component]
    ) -> Optional[Tuple[str, str, float]]:
        """Matches a single wire endpoint to the most likely (component_id, terminal_id, confidence).
        
        Returns:
            (comp_id, term_id, confidence) or None if no candidate exceeds min_confidence.
        """
        # Determine local wire direction approaching the endpoint
        if len(wire_path) >= 3:
            # Vector pointing away from wire towards terminal
            wire_dir = unit_vector((endpoint[0] - wire_path[-3][0], endpoint[1] - wire_path[-3][1]))
        elif len(wire_path) >= 2:
            wire_dir = unit_vector((endpoint[0] - wire_path[0][0], endpoint[1] - wire_path[0][1]))
        else:
            wire_dir = (0.0, 0.0)

        best_match: Optional[Tuple[str, str, float]] = None
        best_score = -1.0

        for comp in components:
            for term in comp.terminals:
                dist = euclidean_dist(endpoint, term.position)
                if dist > self.max_snap_radius:
                    continue

                # 1. Distance score (1.0 at distance 0, decaying to 0.0 at max_radius)
                dist_score = max(0.0, 1.0 - (dist / self.max_snap_radius))

                # 2. Direction alignment score
                dir_score = 0.5  # Neutral default
                if term.direction is not None and (wire_dir[0] != 0 or wire_dir[1] != 0):
                    # Wire approaching terminal should align with the terminal's outward normal
                    dot = dot_product(wire_dir, term.direction)
                    # dot == -1 means perfectly aligned head-on approach
                    dir_score = max(0.0, min(1.0, (-dot + 1.0) / 2.0))

                # 3. Component confidence weighting
                comp_score = comp.confidence * term.confidence

                # Composite match confidence
                total_score = (
                    self.distance_weight * dist_score +
                    self.direction_weight * dir_score +
                    self.orientation_weight * comp_score
                )

                if total_score > best_score:
                    best_score = total_score
                    best_match = (comp.id, term.id, float(total_score))

        if best_match and best_match[2] >= self.min_confidence:
            return best_match

        return None
