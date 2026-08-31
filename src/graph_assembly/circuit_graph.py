"""circuit_graph.py: Bipartite and MultiGraph Circuit Graph Data Structures."""

from typing import List, Dict, Tuple, Any, Optional
import networkx as nx

from src.common.schemas import CircuitGraph, Component, Terminal, Net, ComponentEdge


class CircuitGraphManager:
    """Manages bipartite net-based circuit graphs and derived component MultiGraphs."""

    @staticmethod
    def to_bipartite_networkx(graph: CircuitGraph) -> nx.Graph:
        """Converts CircuitGraph to a bipartite NetworkX Graph with Component, Terminal, and Net nodes."""
        B = nx.Graph()

        for comp in graph.components:
            B.add_node(comp.id, type="component", class_name=comp.type, bbox=comp.bbox.model_dump())
            for term in comp.terminals:
                t_key = f"{comp.id}.{term.id}"
                B.add_node(t_key, type="terminal", semantic_name=term.semantic_name, position=term.position)
                B.add_edge(comp.id, t_key, relation="HAS_TERMINAL")

        for net_id, term_refs in graph.nets.items():
            B.add_node(net_id, type="net")
            for t_ref in term_refs:
                if t_ref in B:
                    B.add_edge(t_ref, net_id, relation="BELONGS_TO")

        return B

    @staticmethod
    def to_component_multigraph(graph: CircuitGraph) -> nx.MultiGraph:
        """Derives a component-level MultiGraph preserving terminal metadata on parallel edges."""
        MG = nx.MultiGraph()

        for comp in graph.components:
            MG.add_node(comp.id, type=comp.type, class_id=comp.class_id, center=comp.center)

        # For every net connecting 2 or more terminals, connect all pairs of components
        for net_id, term_refs in graph.nets.items():
            parsed_terms = []
            for ref in term_refs:
                if "." in ref:
                    parts = ref.split(".", 1)
                    parsed_terms.append((parts[0], parts[1]))

            for i in range(len(parsed_terms)):
                for j in range(i + 1, len(parsed_terms)):
                    c1, t1 = parsed_terms[i]
                    c2, t2 = parsed_terms[j]
                    if c1 != c2:
                        MG.add_edge(
                            c1, c2,
                            key=f"{net_id}_{t1}_{t2}",
                            net=net_id,
                            c1_terminal=t1,
                            c2_terminal=t2
                        )

        return MG
