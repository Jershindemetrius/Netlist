"""skeleton_graph.py: NetworkX Pixel and Segment Graph Construction from Skeleton."""

import math
from typing import List, Tuple, Dict, Any, Set
import numpy as np
import networkx as nx

from src.common.schemas import WireSegment, SkeletonGraphData
from src.wire_tracing.junctions import JunctionDetector


class SkeletonGraphBuilder:
    """Constructs a topological network graph from a skeleton binary image."""

    def __init__(self, cluster_radius: float = 6.0):
        self.junction_detector = JunctionDetector(cluster_radius=cluster_radius)

    def build_graph(self, skeleton: np.ndarray) -> Tuple[nx.Graph, SkeletonGraphData]:
        """Converts skeleton image to NetworkX pixel graph and extracts continuous wire segments."""
        endpoints, junctions = self.junction_detector.detect(skeleton)
        
        # Build pixel-level graph
        G_pixel = nx.Graph()
        fg_pixels = np.column_stack(np.where(skeleton > 0))
        
        for r, c in fg_pixels:
            G_pixel.add_node((c, r))

        # Add 8-connectivity edges
        h, w = skeleton.shape[:2]
        for r, c in fg_pixels:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        if skeleton[nr, nc] > 0:
                            G_pixel.add_edge((c, r), (nc, nr), weight=math.hypot(dc, dr))

        # Extract continuous wire segments from connected components
        wire_segments: List[WireSegment] = []
        seg_counter = 1

        for component_nodes in nx.connected_components(G_pixel):
            subgraph = G_pixel.subgraph(component_nodes)
            
            # Find nodes with degree 1 or >= 3 in subgraph
            terminal_nodes = [node for node in subgraph.nodes() if subgraph.degree(node) != 2]
            
            if not terminal_nodes and len(component_nodes) > 3:
                # Closed loop without endpoints: pick arbitrary starting node
                start_node = next(iter(component_nodes))
                cycle_path = list(component_nodes)
                wire_segments.append(
                    WireSegment(
                        id=f"W{seg_counter}",
                        points=[(float(p[0]), float(p[1])) for p in cycle_path],
                        start_point=(float(start_node[0]), float(start_node[1])),
                        end_point=(float(start_node[0]), float(start_node[1])),
                        length_pixels=float(len(cycle_path)),
                        confidence=0.9
                    )
                )
                seg_counter += 1
            else:
                # Trace paths between terminal nodes (endpoints or junctions)
                visited_edges: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = set()
                
                for t_node in terminal_nodes:
                    for neighbor in subgraph.neighbors(t_node):
                        edge_key = (min(t_node, neighbor), max(t_node, neighbor))
                        if edge_key in visited_edges:
                            continue

                        # Trace simple path until another terminal node
                        path = [t_node, neighbor]
                        visited_edges.add(edge_key)
                        curr = neighbor
                        prev = t_node

                        while curr not in terminal_nodes and subgraph.degree(curr) == 2:
                            next_candidates = [n for n in subgraph.neighbors(curr) if n != prev]
                            if not next_candidates:
                                break
                            next_node = next_candidates[0]
                            e = (min(curr, next_node), max(curr, next_node))
                            visited_edges.add(e)
                            path.append(next_node)
                            prev = curr
                            curr = next_node

                        if len(path) >= 2:
                            wire_segments.append(
                                WireSegment(
                                    id=f"W{seg_counter}",
                                    points=[(float(p[0]), float(p[1])) for p in path],
                                    start_point=(float(path[0][0]), float(path[0][1])),
                                    end_point=(float(path[-1][0]), float(path[-1][1])),
                                    length_pixels=float(len(path)),
                                    confidence=0.95
                                )
                            )
                            seg_counter += 1

        graph_data = SkeletonGraphData(
            endpoints=endpoints,
            junctions=junctions,
            wire_segments=wire_segments
        )

        return G_pixel, graph_data
