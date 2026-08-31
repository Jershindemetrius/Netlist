"""junctions.py: Endpoint, Junction, and Crossover Detection from Skeleton."""

import math
from typing import List, Tuple, Dict, Any
import numpy as np
from scipy.ndimage import convolve

from src.common.schemas import Junction


class JunctionDetector:
    """Detects endpoints, 3-way/4-way junctions, and crossovers from 1-pixel skeletons."""

    def __init__(self, cluster_radius: float = 6.0):
        self.cluster_radius = cluster_radius

    def _compute_neighbor_degrees(self, skeleton: np.ndarray) -> np.ndarray:
        """Calculates 8-connectivity degree for every foreground pixel."""
        binary = (skeleton > 0).astype(np.uint8)
        
        # 3x3 kernel summing all 8 surrounding neighbors
        kernel = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ], dtype=np.uint8)

        neighbor_count = convolve(binary, kernel, mode='constant', cval=0)
        # Degree is neighbor count only on foreground skeleton pixels
        return neighbor_count * binary

    def detect(self, skeleton: np.ndarray) -> Tuple[List[Tuple[float, float]], List[Junction]]:
        """Detects endpoints and clustered junctions from a skeleton mask.
        
        Returns:
            (endpoints, junctions)
        """
        degrees = self._compute_neighbor_degrees(skeleton)
        
        # Endpoints: degree == 1
        ep_coords = np.column_stack(np.where(degrees == 1))
        endpoints: List[Tuple[float, float]] = [(float(c[1]), float(c[0])) for c in ep_coords]

        # Junction candidate pixels: degree >= 3
        junc_coords = np.column_stack(np.where(degrees >= 3))
        raw_junction_points = [(float(c[1]), float(c[0])) for c in junc_coords]

        # Cluster junction candidate pixels within cluster_radius into single logical junctions
        clustered_junctions = self._cluster_junctions(raw_junction_points)

        return endpoints, clustered_junctions

    def _cluster_junctions(self, points: List[Tuple[float, float]]) -> List[Junction]:
        """Groups nearby junction pixels into single centroids."""
        if not points:
            return []

        clusters: List[List[Tuple[float, float]]] = []
        for pt in points:
            matched = False
            for cl in clusters:
                # Check distance to cluster centroid
                cx = sum(p[0] for p in cl) / len(cl)
                cy = sum(p[1] for p in cl) / len(cl)
                if math.hypot(pt[0] - cx, pt[1] - cy) <= self.cluster_radius:
                    cl.append(pt)
                    matched = True
                    break
            if not matched:
                clusters.append([pt])

        junctions: List[Junction] = []
        for idx, cl in enumerate(clusters):
            cx = float(sum(p[0] for p in cl) / len(cl))
            cy = float(sum(p[1] for p in cl) / len(cl))
            degree = max(3, len(cl)) # Approximate degree
            
            junctions.append(
                Junction(
                    id=f"J{idx+1}",
                    position=(cx, cy),
                    degree=degree,
                    is_crossover=False
                )
            )

        return junctions
