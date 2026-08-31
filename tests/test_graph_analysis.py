"""test_graph_analysis.py: Comprehensive Unit Test Suite for Intelligent Circuit Graph Analyzer."""

import unittest
from src.common.schemas import CircuitGraph, Component, BoundingBox, Terminal
from src.graph_analysis.schema import ConfidenceBucket, get_confidence_bucket
from src.graph_analysis.confidence import ConfidenceGraphBuilder
from src.graph_analysis.error_detector import CircuitErrorDetector
from src.graph_analysis.subcircuits import SubcircuitAnalyzer
from src.graph_analysis.simplifier import CircuitSimplifier
from src.graph_analysis.analyzer import IntelligentGraphAnalyzer


class TestConfidenceGraph(unittest.TestCase):
    """Test suite verifying Feature 1: Confidence-Aware Graph Schema & Bucketing."""

    def test_confidence_bucketing_ranges(self):
        """Verifies score classification into HIGH, MEDIUM, and LOW buckets."""
        self.assertEqual(get_confidence_bucket(0.95), ConfidenceBucket.HIGH)
        self.assertEqual(get_confidence_bucket(0.90), ConfidenceBucket.HIGH)
        self.assertEqual(get_confidence_bucket(0.85), ConfidenceBucket.MEDIUM)
        self.assertEqual(get_confidence_bucket(0.70), ConfidenceBucket.MEDIUM)
        self.assertEqual(get_confidence_bucket(0.65), ConfidenceBucket.LOW)
        self.assertEqual(get_confidence_bucket(0.10), ConfidenceBucket.LOW)

    def test_build_networkx_confidence_graph(self):
        """Verifies conversion of CircuitGraph to confidence-annotated NetworkX graph."""
        c1 = Component(
            id="R1",
            type="resistor",
            class_id=0,
            bbox=BoundingBox(xmin=100, ymin=100, xmax=200, ymax=150),
            center=(150, 125),
            confidence=0.95,
            terminals=[
                Terminal(id="T1", semantic_name="T1", position=(100, 125), confidence=0.96, connected_net="NET1"),
                Terminal(id="T2", semantic_name="T2", position=(200, 125), confidence=0.94, connected_net="NET2"),
            ],
        )

        c2 = Component(
            id="C1",
            type="capacitor.unpolarized",
            class_id=1,
            bbox=BoundingBox(xmin=300, ymin=100, xmax=400, ymax=150),
            center=(350, 125),
            confidence=0.82,
            terminals=[
                Terminal(id="T1", semantic_name="T1", position=(300, 125), confidence=0.85, connected_net="NET2"),
                Terminal(id="T2", semantic_name="T2", position=(400, 125), confidence=0.80, connected_net="0"),
            ],
        )

        circuit_graph = CircuitGraph(
            components=[c1, c2],
            nets={
                "NET1": ["R1.T1"],
                "NET2": ["R1.T2", "C1.T1"],
                "0": ["C1.T2"],
            },
            metadata={"source_image": "test_circuit.jpg"},
        )

        builder = ConfidenceGraphBuilder()
        G = builder.build_networkx_graph(circuit_graph)

        self.assertEqual(len(G.nodes()), 2)
        self.assertEqual(G.nodes["R1"]["confidence_bucket"], ConfidenceBucket.HIGH)
        self.assertEqual(G.nodes["C1"]["confidence_bucket"], ConfidenceBucket.MEDIUM)


class TestCircuitErrorDetection(unittest.TestCase):
    """Test suite verifying Feature 2: Automatic Circuit Error Detection."""

    def test_floating_terminal_detection(self):
        """Verifies detection of floating unconnected terminals with (x, y) pixel coordinates."""
        c1 = Component(
            id="R1",
            type="resistor",
            class_id=0,
            bbox=BoundingBox(xmin=100, ymin=100, xmax=200, ymax=150),
            center=(150, 125),
            confidence=0.95,
            terminals=[
                Terminal(id="T1", semantic_name="T1", position=(100, 125), confidence=0.95, connected_net="NET1"),
                Terminal(id="T2", semantic_name="T2", position=(200, 125), confidence=0.95, connected_net=None), # Floating!
            ],
        )

        circuit_graph = CircuitGraph(
            components=[c1],
            nets={"NET1": ["R1.T1"]},
        )

        detector = CircuitErrorDetector()
        errors = detector.detect_errors(circuit_graph)

        self.assertGreaterEqual(len(errors), 1)
        floating_err = next((e for e in errors if e.error_type == "floating_terminal"), None)
        self.assertIsNotNone(floating_err)
        self.assertEqual(floating_err.component_id, "R1")
        self.assertEqual(floating_err.terminal_id, "T2")
        self.assertEqual(floating_err.location, (200, 125))  # Exact pixel coordinates!

    def test_low_confidence_error_tagging(self):
        """Verifies that errors on low-confidence components tag 'is_possible_detection_error' as True."""
        c1 = Component(
            id="R2",
            type="resistor",
            class_id=0,
            bbox=BoundingBox(xmin=100, ymin=100, xmax=200, ymax=150),
            center=(150, 125),
            confidence=0.55,  # Low confidence (<0.70)
            terminals=[
                Terminal(id="T1", semantic_name="T1", position=(100, 125), confidence=0.55, connected_net=None),
                Terminal(id="T2", semantic_name="T2", position=(200, 125), confidence=0.55, connected_net="NET1"),
            ],
        )

        circuit_graph = CircuitGraph(
            components=[c1],
            nets={"NET1": ["R2.T2"]},
        )

        detector = CircuitErrorDetector()
        errors = detector.detect_errors(circuit_graph)

        floating_err = next((e for e in errors if e.error_type == "floating_terminal"), None)
        self.assertIsNotNone(floating_err)
        self.assertTrue(floating_err.is_possible_detection_error)
        self.assertEqual(floating_err.severity, "warning")


class TestSubcircuitAndSimplification(unittest.TestCase):
    """Test suite verifying Feature 3 (Subcircuits) and Feature 5 (Simplification)."""

    def test_disconnected_subcircuits(self):
        """Verifies identification of isolated subcircuits using NetworkX connected components."""
        c1 = Component(
            id="V1",
            type="voltage.dc",
            class_id=4,
            bbox=BoundingBox(xmin=100, ymin=100, xmax=150, ymax=200),
            center=(125, 150),
            confidence=0.95,
            terminals=[
                Terminal(id="POS", semantic_name="POS", position=(125, 100), connected_net="NET1"),
                Terminal(id="NEG", semantic_name="NEG", position=(125, 200), connected_net="0"),
            ],
        )

        c2 = Component(
            id="R1",
            type="resistor",
            class_id=0,
            bbox=BoundingBox(xmin=200, ymin=100, xmax=300, ymax=150),
            center=(250, 125),
            confidence=0.90,
            terminals=[
                Terminal(id="T1", semantic_name="T1", position=(200, 125), connected_net="NET1"),
                Terminal(id="T2", semantic_name="T2", position=(300, 125), connected_net="0"),
            ],
        )

        c3 = Component(
            id="R3_ISOLATED",
            type="resistor",
            class_id=0,
            bbox=BoundingBox(xmin=600, ymin=100, xmax=700, ymax=150),
            center=(650, 125),
            confidence=0.88,
            terminals=[
                Terminal(id="T1", semantic_name="T1", position=(600, 125), connected_net="NET5"),
                Terminal(id="T2", semantic_name="T2", position=(700, 125), connected_net="NET5"),
            ],
        )

        circuit_graph = CircuitGraph(
            components=[c1, c2, c3],
            nets={
                "NET1": ["V1.POS", "R1.T1"],
                "0": ["V1.NEG", "R1.T2"],
                "NET5": ["R3_ISOLATED.T1", "R3_ISOLATED.T2"],
            },
        )

        analyzer = IntelligentGraphAnalyzer()
        report = analyzer.analyze(circuit_graph, image_id="test_subcircuits")

        self.assertEqual(len(report.subcircuits), 2)
        isolated_sub = next((s for s in report.subcircuits if not s.is_connected), None)
        self.assertIsNotNone(isolated_sub)
        self.assertIn("R3_ISOLATED", isolated_sub.components)


if __name__ == "__main__":
    unittest.main()
