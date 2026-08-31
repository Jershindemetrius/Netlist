"""test_evaluation.py: Unit Tests for ASC Parser and Graph Evaluator."""

import unittest
from pathlib import Path

from src.eval.asc_parser import AscParser
from src.eval.graph_distance import GraphEvaluator


class TestEvaluation(unittest.TestCase):

    def setUp(self):
        self.asc_file = Path("data/raw/cghd/drafter_1/spice/C1.asc")

    def test_asc_parsing(self):
        if not self.asc_file.exists():
            self.skipTest(f"ASC test file missing at {self.asc_file}")

        parser = AscParser()
        graph = parser.parse_file(str(self.asc_file))

        self.assertGreater(len(graph.components), 0)
        self.assertGreater(len(graph.nets), 0)

        # Check presence of expected components from C1.asc (U1, Q1, R1, R2, C1, D1, V1)
        comp_types = [c.type for c in graph.components]
        self.assertIn("integrated_circuit.ne555", comp_types)
        self.assertIn("transistor.bjt", comp_types)
        self.assertIn("resistor", comp_types)

    def test_graph_self_evaluation(self):
        if not self.asc_file.exists():
            self.skipTest(f"ASC test file missing at {self.asc_file}")

        parser = AscParser()
        graph = parser.parse_file(str(self.asc_file))

        evaluator = GraphEvaluator()
        metrics = evaluator.evaluate(graph, graph, run_exact_ged=True)

        self.assertEqual(metrics.ged_score, 0.0)
        self.assertEqual(metrics.component_f1, 1.0)
        self.assertEqual(metrics.net_f1, 1.0)


if __name__ == "__main__":
    unittest.main()
