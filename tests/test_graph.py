"""test_graph.py: Unit Tests for Circuit Graph Normalization, Nets, and SPICE Export."""

import unittest
from src.common.schemas import CircuitGraph, Component, Terminal, BoundingBox
from src.graph_assembly.graph_normalizer import GraphNormalizer


class TestCircuitGraph(unittest.TestCase):

    def test_canonical_relabeling(self):
        c1 = Component(
            id="RAW_10",
            type="resistor",
            class_id=10,
            bbox=BoundingBox(xmin=100, ymin=100, xmax=150, ymax=150),
            center=(125, 125),
            terminals=[
                Terminal(id="T1", semantic_name="connector", position=(100, 125)),
                Terminal(id="T2", semantic_name="connector", position=(150, 125))
            ]
        )
        c2 = Component(
            id="RAW_20",
            type="voltage.dc",
            class_id=7,
            bbox=BoundingBox(xmin=50, ymin=100, xmax=80, ymax=150),
            center=(65, 125),
            terminals=[
                Terminal(id="POS", semantic_name="positive", position=(65, 100)),
                Terminal(id="NEG", semantic_name="negative", position=(65, 150))
            ]
        )

        graph = CircuitGraph(
            components=[c1, c2],
            nets={
                "NET_A": ["RAW_20.POS", "RAW_10.T1"],
                "NET_B": ["RAW_10.T2", "RAW_20.NEG"]
            }
        )

        normalizer = GraphNormalizer()
        norm_graph = normalizer.normalize(graph)

        comp_ids = [c.id for c in norm_graph.components]
        self.assertIn("V1", comp_ids)
        self.assertIn("R1", comp_ids)

        spice_text = norm_graph.to_spice_netlist()
        self.assertIn("V1", spice_text)
        self.assertIn("R1", spice_text)
        self.assertIn(".end", spice_text)


if __name__ == "__main__":
    unittest.main()
