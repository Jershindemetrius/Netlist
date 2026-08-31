"""test_skeleton.py: Unit Tests for Skeletonization and Junction Detection."""

import unittest
import numpy as np

from src.wire_tracing.skeleton import WireSkeletonizer
from src.wire_tracing.junctions import JunctionDetector


class TestSkeletonAndJunctions(unittest.TestCase):

    def test_line_skeletonization(self):
        # Create a thick horizontal bar
        img = np.zeros((50, 50), dtype=np.uint8)
        img[20:30, 5:45] = 255

        skeletonizer = WireSkeletonizer()
        skel = skeletonizer.skeletonize(img)

        # Skeleton should be 1-pixel wide line
        self.assertTrue((skel > 0).sum() < (img > 0).sum())

    def test_t_junction_detection(self):
        # Create a T-shaped 1-pixel skeleton
        img = np.zeros((50, 50), dtype=np.uint8)
        img[25, 10:40] = 255  # Horizontal
        img[25:40, 25] = 255  # Vertical branch downwards

        detector = JunctionDetector(cluster_radius=3.0)
        endpoints, junctions = detector.detect(img)

        self.assertEqual(len(endpoints), 3)  # 3 line ends
        self.assertEqual(len(junctions), 1)  # 1 T-junction at center (25, 25)
        self.assertAlmostEqual(junctions[0].position[0], 25.0, delta=2.0)
        self.assertAlmostEqual(junctions[0].position[1], 25.0, delta=2.0)


if __name__ == "__main__":
    unittest.main()
