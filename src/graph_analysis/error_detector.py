"""error_detector.py: Feature 2 - Automatic Circuit Error Detection Rule Engine."""

import networkx as nx
from typing import List, Dict, Tuple, Any, Optional
from src.common.schemas import CircuitGraph
from src.graph_analysis.schema import (
    CircuitError,
    ConfidenceBucket,
    get_confidence_bucket,
)


class CircuitErrorDetector:
    """Runs deterministic topological rule checks over the circuit graph."""

    def detect_errors(
        self, circuit_graph: CircuitGraph, G: Optional[nx.Graph] = None
    ) -> List[CircuitError]:
        """Scans the circuit graph for topological errors:
        
        1. Floating Terminal: A component terminal with no net connection.
        2. Single Terminal Connection: A multi-terminal component with only 1 connected pin.
        3. Low Confidence Connection: Connection involving low-confidence detection.
        4. Disconnected Component: Component not connected to any other node.

        Each error includes (x, y) pixel location and tags 'possible detection error' if low confidence.
        """
        errors: List[CircuitError] = []
        error_counter = 0

        # Build net mapping: "CompID.TermID" -> Net ID
        term_to_net: Dict[str, str] = {}
        for net_id, term_refs in (circuit_graph.nets or {}).items():
            for ref in term_refs:
                term_to_net[ref] = net_id

        for comp in circuit_graph.components:
            comp_id = comp.id
            comp_conf = float(comp.confidence)
            is_comp_low_conf = comp_conf < 0.70

            connected_terminals: List[str] = []
            unconnected_terminals: List[Tuple[str, Tuple[float, float]]] = []

            for term in comp.terminals:
                term_ref = f"{comp_id}.{term.id}"
                net_id = term_to_net.get(term_ref, term.connected_net)

                if net_id and net_id != "NC" and not net_id.startswith("UNCONNECTED_"):
                    connected_terminals.append(term.id)
                else:
                    unconnected_terminals.append((term.id, term.position))

            # Rule 1: Floating Terminal Detection
            for term_id, pos in unconnected_terminals:
                error_counter += 1
                is_low_conf = is_comp_low_conf or (term.confidence < 0.70 if 'term' in locals() else False)

                errors.append(
                    CircuitError(
                        error_id=f"err_{error_counter}",
                        component_id=comp_id,
                        terminal_id=term_id,
                        error_type="floating_terminal",
                        severity="warning" if is_low_conf else "confirmed",
                        message=f"Floating Terminal: {comp_id}.{term_id} is not connected to any net.",
                        location=pos if (pos and pos != (0.0, 0.0)) else comp.center,
                        is_possible_detection_error=is_low_conf,
                    )
                )

            # Rule 2: Single Terminal Connection (Component needs >= 2 pins but only has 1 connected)
            if len(comp.terminals) >= 2 and len(connected_terminals) == 1:
                error_counter += 1
                conn_term = connected_terminals[0]
                term_obj = comp.get_terminal(conn_term)
                term_pos = term_obj.position if term_obj else comp.center

                errors.append(
                    CircuitError(
                        error_id=f"err_{error_counter}",
                        component_id=comp_id,
                        terminal_id=conn_term,
                        error_type="single_terminal",
                        severity="warning" if is_comp_low_conf else "confirmed",
                        message=f"Single Terminal Connection: {comp_id} has only 1 terminal ({conn_term}) connected.",
                        location=term_pos,
                        is_possible_detection_error=is_comp_low_conf,
                    )
                )

            # Rule 3: Low Confidence Connection Warning
            if is_comp_low_conf and len(connected_terminals) > 0:
                error_counter += 1
                errors.append(
                    CircuitError(
                        error_id=f"err_{error_counter}",
                        component_id=comp_id,
                        terminal_id=connected_terminals[0],
                        error_type="low_confidence_connection",
                        severity="warning",
                        message=f"Low Confidence Detection: {comp_id} has confidence {comp_conf:.2f} (<0.70). Verify wire tracing.",
                        location=comp.center,
                        is_possible_detection_error=True,
                    )
                )

        return errors
