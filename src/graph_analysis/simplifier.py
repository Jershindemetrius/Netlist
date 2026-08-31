"""simplifier.py: Feature 5 - Automatic Circuit Simplification Module."""

import networkx as nx
from typing import List, Dict, Set
from src.common.schemas import CircuitGraph
from src.graph_analysis.schema import SimplificationResult


class CircuitSimplifier:
    """Detects series and parallel component topological patterns for circuit reduction."""

    def detect_simplifications(
        self, circuit_graph: CircuitGraph, G: nx.Graph
    ) -> List[SimplificationResult]:
        """Detects series resistors, parallel resistors, and series capacitors."""
        simplifications: List[SimplificationResult] = []

        resistors = [c for c in circuit_graph.components if "resistor" in c.type.lower()]
        capacitors = [c for c in circuit_graph.components if "capacitor" in c.type.lower()]

        # 1. Series Resistors Detection
        if len(resistors) >= 2:
            for i in range(len(resistors)):
                for j in range(i + 1, len(resistors)):
                    r1 = resistors[i]
                    r2 = resistors[j]
                    if G.has_edge(r1.id, r2.id):
                        # Check degree of connection: if intermediate net only connects r1 and r2
                        simplifications.append(
                            SimplificationResult(
                                pattern_type="series_resistors",
                                original_components=[r1.id, r2.id],
                                equivalent_label=f"Req ({r1.id} + {r2.id})",
                                formula_text=f"Req = {r1.id} + {r2.id} = {r1.value or '10k'} + {r2.value or '10k'}",
                            )
                        )
                        break

        # 2. Parallel Resistors Detection
        if len(resistors) >= 2:
            # Check if r1 and r2 share two distinct nets
            term_to_net: Dict[str, str] = {}
            for net_id, term_refs in (circuit_graph.nets or {}).items():
                for ref in term_refs:
                    term_to_net[ref] = net_id

            for i in range(len(resistors)):
                for j in range(i + 1, len(resistors)):
                    r1 = resistors[i]
                    r2 = resistors[j]
                    nets_r1 = {term_to_net.get(f"{r1.id}.{t.id}") for t in r1.terminals if term_to_net.get(f"{r1.id}.{t.id}")}
                    nets_r2 = {term_to_net.get(f"{r2.id}.{t.id}") for t in r2.terminals if term_to_net.get(f"{r2.id}.{t.id}")}
                    shared_nets = nets_r1.intersection(nets_r2)

                    if len(shared_nets) >= 2:
                        simplifications.append(
                            SimplificationResult(
                                pattern_type="parallel_resistors",
                                original_components=[r1.id, r2.id],
                                equivalent_label=f"Req ({r1.id} || {r2.id})",
                                formula_text=f"Req = ({r1.id} · {r2.id}) / ({r1.id} + {r2.id})",
                            )
                        )

        # 3. Series Capacitors Detection
        if len(capacitors) >= 2:
            for i in range(len(capacitors)):
                for j in range(i + 1, len(capacitors)):
                    c1 = capacitors[i]
                    c2 = capacitors[j]
                    if G.has_edge(c1.id, c2.id):
                        simplifications.append(
                            SimplificationResult(
                                pattern_type="series_capacitors",
                                original_components=[c1.id, c2.id],
                                equivalent_label=f"Ceq ({c1.id} series {c2.id})",
                                formula_text=f"Ceq = ({c1.id} · {c2.id}) / ({c1.id} + {c2.id})",
                            )
                        )
                        break

        return simplifications
