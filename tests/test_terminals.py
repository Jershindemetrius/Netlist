"""test_terminals.py: Unit Tests for Terminal Estimation and Rotations."""

import unittest
from src.common.schemas import BoundingBox, Detection
from src.geometry.terminal_estimator import TerminalEstimator


class TestTerminalEstimator(unittest.TestCase):

    def setUp(self):
        self.estimator = TerminalEstimator()

    def test_resistor_terminal_positions(self):
        det = Detection(
            class_id=10,
            class_name="resistor",
            confidence=0.9,
            bbox=BoundingBox(xmin=100, ymin=100, xmax=200, ymax=100)
        )
        comp = self.estimator.estimate_terminals("R1", det)
        self.assertEqual(len(comp.terminals), 2)
        self.assertEqual(comp.terminals[0].id, "T1")
        self.assertEqual(comp.terminals[1].id, "T2")


if __name__ == "__main__":
    unittest.main()
