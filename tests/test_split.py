"""test_split.py: Unit Tests for Drafter-Isolated Partitioning."""

import unittest
from src.data.split_drafters import DrafterSplitter


class TestDrafterSplitter(unittest.TestCase):

    def test_zero_drafter_overlap(self):
        splitter = DrafterSplitter(seed=42)
        mock_drafters = [f"drafter_{i}" for i in range(1, 31)]
        manifest = splitter.generate_split(drafters=mock_drafters)

        train_set = set(manifest["splits"]["train"])
        val_set = set(manifest["splits"]["val"])
        test_set = set(manifest["splits"]["test"])

        self.assertEqual(len(train_set.intersection(val_set)), 0)
        self.assertEqual(len(train_set.intersection(test_set)), 0)
        self.assertEqual(len(val_set.intersection(test_set)), 0)
        self.assertEqual(len(train_set) + len(val_set) + len(test_set), 30)

    def test_split_reproducibility(self):
        s1 = DrafterSplitter(seed=123).generate_split()
        s2 = DrafterSplitter(seed=123).generate_split()
        self.assertEqual(s1["splits"], s2["splits"])


if __name__ == "__main__":
    unittest.main()
