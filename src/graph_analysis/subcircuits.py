"""subcircuits.py: Feature 3 - Disconnected Subcircuit Detection Engine."""

import networkx as nx
from typing import List, Dict, Set, Any
from src.common.schemas import CircuitGraph
from src.graph_analysis.schema import SubcircuitGroup


class SubcircuitAnalyzer:
    """Detects connected and isolated subcircuits using NetworkX connected components."""

    def analyze_subcircuits(
        self, circuit_graph: CircuitGraph, G: nx.Graph
    ) -> List[SubcircuitGroup]:
        """Identifies connected components in the graph and flags isolated subcircuits."""
        subcircuits: List[SubcircuitGroup] = []

        if len(G.nodes()) == 0:
            return subcircuits

        # Find connected components in the NetworkX graph
        connected_groups = list(nx.connected_components(G))

        # Map terminal refs to net IDs
        term_to_net: Dict[str, str] = {}
        for net_id, term_refs in (circuit_graph.nets or {}).items():
            for ref in term_refs:
                term_to_net[ref] = net_id

        # Determine the main / primary subcircuit (the largest connected component group)
        largest_group_size = max(len(group) for group in connected_groups) if connected_groups else 0

        for idx, group in enumerate(connected_groups, start=1):
            comp_list = sorted(list(group))
            is_main = len(group) == largest_group_size and idx == 1

            # Gather nets associated with components in this subcircuit
            sub_nets: Set[str] = set()
            for comp_id in comp_list:
                comp = next((c for c in circuit_graph.components if c.id == comp_id), None)
                if comp:
                    for t in comp.terminals:
                        net_id = term_to_net.get(f"{comp_id}.{t.id}", t.connected_net)
                        if net_id and net_id != "NC":
                            sub_nets.add(net_id)

            label = f"Subcircuit {idx} ({'Connected' if is_main else 'Isolated'})"

            subcircuits.append(
                SubcircuitGroup(
                    subcircuit_id=f"sub_{idx}",
                    components=comp_list,
                    nets=sorted(list(sub_nets)),
                    is_connected=is_main,
                )
            )

        return subcircuits
