"""analyzer.py: Intelligent Circuit Graph Analyzer High-Level Orchestrator."""

from typing import Dict, Any, Optional
from src.common.schemas import CircuitGraph
from src.graph_analysis.schema import (
    AnalysisReport,
    ConfidenceBucket,
    get_confidence_bucket,
)
from src.graph_analysis.confidence import ConfidenceGraphBuilder
from src.graph_analysis.error_detector import CircuitErrorDetector
from src.graph_analysis.subcircuits import SubcircuitAnalyzer
from src.graph_analysis.simplifier import CircuitSimplifier


class IntelligentGraphAnalyzer:
    """Consumes baseline CircuitGraph and runs confidence analysis, error detection,
    disconnected subcircuit analysis, and circuit simplification.
    """

    def __init__(self):
        self.confidence_builder = ConfidenceGraphBuilder()
        self.error_detector = CircuitErrorDetector()
        self.subcircuit_analyzer = SubcircuitAnalyzer()
        self.simplifier = CircuitSimplifier()

    def analyze(self, circuit_graph: CircuitGraph, image_id: str = "circuit_001") -> AnalysisReport:
        """Executes complete graph analysis pipeline over the input CircuitGraph."""
        # 1. Build Confidence-Aware NetworkX Graph (Feature 1)
        G = self.confidence_builder.build_networkx_graph(circuit_graph)
        nodes, edges = self.confidence_builder.extract_confidence_nodes_and_edges(G)

        # 2. Run Automatic Circuit Error Detection (Feature 2)
        errors = self.error_detector.detect_errors(circuit_graph, G)

        # 3. Detect Disconnected Subcircuits (Feature 3)
        subcircuits = self.subcircuit_analyzer.analyze_subcircuits(circuit_graph, G)

        # 4. Detect Circuit Simplifications (Feature 5)
        simplifications = self.simplifier.detect_simplifications(circuit_graph, G)

        # Calculate overall graph confidence
        if len(nodes) > 0:
            avg_conf = sum(n.detection_confidence for n in nodes) / float(len(nodes))
        else:
            avg_conf = 1.0

        overall_conf = round(avg_conf, 2)
        overall_bucket = get_confidence_bucket(overall_conf)

        return AnalysisReport(
            image_id=image_id,
            overall_confidence=overall_conf,
            overall_bucket=overall_bucket,
            nodes=nodes,
            edges=edges,
            errors=errors,
            subcircuits=subcircuits,
            simplifications=simplifications,
        )
