"""confidence.py: Feature 1 - Confidence-Aware Graph Builder Implementation."""

import networkx as nx
from typing import Dict, List, Tuple, Any, Optional
from src.common.schemas import CircuitGraph, Component, Terminal
from src.graph_analysis.schema import (
    ConfidenceBucket,
    ConfidenceNode,
    ConfidenceEdge,
    get_confidence_bucket,
)


class ConfidenceGraphBuilder:
    """Transforms a baseline CircuitGraph into a confidence-annotated NetworkX graph."""

    def build_networkx_graph(self, circuit_graph: CircuitGraph) -> nx.Graph:
        """Constructs a NetworkX Graph where components are nodes and wire connections are edges.
        
        Every node stores:
            - component_id: str
            - type: str
            - detection_confidence: float (YOLO score)
            - confidence_bucket: ConfidenceBucket (HIGH, MEDIUM, LOW)
            - bbox: List[float]
            - center: Tuple[float, float]
            - terminals: List[Dict]

        Every edge stores:
            - source_terminal: str
            - target_terminal: str
            - net_id: str
            - connection_confidence: float
            - confidence_bucket: ConfidenceBucket (HIGH, MEDIUM, LOW)
        """
        G = nx.Graph()

        # Map terminal references (e.g. "R1.T1") to Net IDs
        term_to_net: Dict[str, str] = {}
        for net_id, term_refs in (circuit_graph.nets or {}).items():
            for ref in term_refs:
                term_to_net[ref] = net_id

        # 1. Add Component Nodes
        for comp in circuit_graph.components:
            conf = float(comp.confidence)
            bucket = get_confidence_bucket(conf)

            term_list = [
                {
                    "id": t.id,
                    "semantic_name": t.semantic_name,
                    "position": list(t.position),
                    "confidence": float(t.confidence),
                    "net": term_to_net.get(f"{comp.id}.{t.id}", t.connected_net)
                }
                for t in comp.terminals
            ]

            node_data = ConfidenceNode(
                component_id=comp.id,
                type=comp.type,
                class_id=comp.class_id,
                detection_confidence=conf,
                confidence_bucket=bucket,
                bbox=[comp.bbox.xmin, comp.bbox.ymin, comp.bbox.xmax, comp.bbox.ymax],
                center=comp.center,
                orientation=comp.orientation,
                value=comp.value,
                terminals=term_list,
            )

            G.add_node(
                comp.id,
                component_id=comp.id,
                type=comp.type,
                class_id=comp.class_id,
                detection_confidence=conf,
                confidence_bucket=bucket,
                bbox=[comp.bbox.xmin, comp.bbox.ymin, comp.bbox.xmax, comp.bbox.ymax],
                center=comp.center,
                terminals=term_list,
                node_object=node_data,
            )

        # 2. Add Wire Connection Edges between Component Terminals on shared Nets
        edge_counter = 0
        for net_id, term_refs in (circuit_graph.nets or {}).items():
            # Group terminal references by component ID
            refs_list = list(term_refs)
            for i in range(len(refs_list)):
                for j in range(i + 1, len(refs_list)):
                    ref_a = refs_list[i]
                    ref_b = refs_list[j]

                    parts_a = ref_a.split(".")
                    parts_b = ref_b.split(".")

                    comp_a = parts_a[0]
                    term_a = parts_a[1] if len(parts_a) > 1 else parts_a[0]
                    comp_b = parts_b[0]
                    term_b = parts_b[1] if len(parts_b) > 1 else parts_b[0]

                    if comp_a == comp_b:
                        continue  # Skip internal self-loops

                    # Calculate edge connection confidence derived from component & terminal confidences
                    comp_obj_a = circuit_graph.components[0] if len(circuit_graph.components) > 0 else None
                    conf_a = 1.0
                    conf_b = 1.0
                    for c in circuit_graph.components:
                        if c.id == comp_a:
                            conf_a = c.confidence
                        elif c.id == comp_b:
                            conf_b = c.confidence

                    edge_conf = round(min(conf_a, conf_b), 2)
                    edge_bucket = get_confidence_bucket(edge_conf)

                    edge_id = f"edge_{ref_a}_to_{ref_b}"
                    edge_counter += 1

                    edge_obj = ConfidenceEdge(
                        id=edge_id,
                        source_component=comp_a,
                        source_terminal=term_a,
                        target_component=comp_b,
                        target_terminal=term_b,
                        net_id=net_id,
                        connection_confidence=edge_conf,
                        confidence_bucket=edge_bucket,
                    )

                    G.add_edge(
                        comp_a,
                        comp_b,
                        key=edge_id,
                        id=edge_id,
                        source_terminal=term_a,
                        target_terminal=term_b,
                        net_id=net_id,
                        connection_confidence=edge_conf,
                        confidence_bucket=edge_bucket,
                        edge_object=edge_obj,
                    )

        return G

    def extract_confidence_nodes_and_edges(
        self, G: nx.Graph
    ) -> Tuple[List[ConfidenceNode], List[ConfidenceEdge]]:
        """Extracts structured list of ConfidenceNode and ConfidenceEdge objects from NetworkX graph."""
        nodes: List[ConfidenceNode] = []
        edges: List[ConfidenceEdge] = []

        for node_id, data in G.nodes(data=True):
            if "node_object" in data:
                nodes.append(data["node_object"])

        for u, v, data in G.edges(data=True):
            if "edge_object" in data:
                edges.append(data["edge_object"])

        return nodes, edges
