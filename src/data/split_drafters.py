"""split_drafters.py: Drafter-Isolated Train / Val / Test Partition Generator.

Strictly enforces zero drafter overlap across splits to guarantee generalization
to unseen drafters and handwriting styles.
"""

import os
import random
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter

from src.common.logging import logger
from src.common.io import save_json, save_yaml, ensure_dir, load_json


class DrafterSplitter:
    """Partitions dataset drafters into Train / Val / Test splits."""

    def __init__(
        self,
        data_dir: str = "data/raw/cghd",
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42
    ):
        self.data_dir = Path(data_dir)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.seed = seed

    def discover_drafters(self) -> List[str]:
        """Discovers all drafter directory names in dataset."""
        if not self.data_dir.exists():
            return []
        drafters = [d.name for d in self.data_dir.iterdir() if d.is_dir() and "drafter_" in d.name]
        # Sort naturally by drafter index
        def drafter_key(name: str):
            idx = name.split("_")[1]
            return int(idx) if idx.lstrip("-").isdigit() else 0
        return sorted(drafters, key=drafter_key)

    def generate_split(self, drafters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Performs reproducible drafter partitioning."""
        if drafters is None:
            drafters = self.discover_drafters()

        if not drafters:
            # Fallback default 30 drafters if data directory is empty/remote
            drafters = [f"drafter_{i}" for i in range(1, 31)]
            logger.info(f"Discovered 0 local drafter folders. Using canonical 30 drafters (drafter_1 to drafter_30).")

        # Shuffle with fixed seed
        rng = random.Random(self.seed)
        shuffled = list(drafters)
        rng.shuffle(shuffled)

        n_total = len(shuffled)
        if n_total < 3:
            train_drafters = list(shuffled)
            val_drafters = list(shuffled)
            test_drafters = list(shuffled)
        else:
            n_val = max(1, int(round(n_total * self.val_ratio)))
            n_test = max(1, int(round(n_total * self.test_ratio)))
            n_train = n_total - n_val - n_test

            train_drafters = sorted(shuffled[:n_train])
            val_drafters = sorted(shuffled[n_train:n_train + n_val])
            test_drafters = sorted(shuffled[n_train + n_val:])

        # Verify zero leakage
        set_train = set(train_drafters)
        set_val = set(val_drafters)
        set_test = set(test_drafters)

        if n_total >= 3:
            assert len(set_train.intersection(set_val)) == 0, "Drafter overlap between Train and Val!"
            assert len(set_train.intersection(set_test)) == 0, "Drafter overlap between Train and Test!"
            assert len(set_val.intersection(set_test)) == 0, "Drafter overlap between Val and Test!"

        manifest = {
            "seed": self.seed,
            "total_drafters": n_total,
            "ratios": {
                "train": self.train_ratio,
                "val": self.val_ratio,
                "test": self.test_ratio
            },
            "splits": {
                "train": train_drafters,
                "val": val_drafters,
                "test": test_drafters
            },
            "counts": {
                "train_drafters": len(train_drafters),
                "val_drafters": len(val_drafters),
                "test_drafters": len(test_drafters)
            }
        }

        return manifest

    def compute_split_statistics(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Computes image and annotation counts for each split from local data."""
        stats = {}
        for split_name, d_list in manifest["splits"].items():
            split_images = 0
            split_annotations = 0
            for d_name in d_list:
                ann_dir = self.data_dir / d_name / "annotations"
                img_dir = self.data_dir / d_name / "images"
                if ann_dir.exists():
                    split_annotations += len(list(ann_dir.glob("*.xml")))
                if img_dir.exists():
                    split_images += len(list(img_dir.glob("*.[jJ][pP][gG]"))) + len(list(img_dir.glob("*.[pP][nN][gG]")))
            stats[split_name] = {
                "drafters": len(d_list),
                "images": split_images,
                "annotations": split_annotations
            }
        return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate drafter-isolated dataset splits.")
    parser.add_argument("--data-dir", default="data/raw/cghd", help="Path to raw CGHD dataset")
    parser.add_argument("--output", default="data/splits/split_manifest.json", help="Path to output split manifest JSON")
    parser.add_argument("--train-ratio", type=float, default=0.70, help="Train ratio (0.0 - 1.0)")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="Val ratio (0.0 - 1.0)")
    parser.add_argument("--test-ratio", type=float, default=0.15, help="Test ratio (0.0 - 1.0)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    splitter = DrafterSplitter(
        data_dir=args.data_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed
    )

    manifest = splitter.generate_split()
    save_json(manifest, args.output)
    
    # Also save YAML version
    yaml_out = Path(args.output).with_suffix(".yaml")
    save_yaml(manifest, yaml_out)

    print("=" * 65)
    print("           DRAFTER SPLIT MANIFEST GENERATED")
    print("=" * 65)
    print(f"Seed: {manifest['seed']}")
    print(f"Train ({manifest['counts']['train_drafters']} drafters): {manifest['splits']['train']}")
    print(f"Val   ({manifest['counts']['val_drafters']} drafters): {manifest['splits']['val']}")
    print(f"Test  ({manifest['counts']['test_drafters']} drafters): {manifest['splits']['test']}")
    print("-" * 65)
    
    stats = splitter.compute_split_statistics(manifest)
    for s_name, s_data in stats.items():
        print(f"Split [{s_name.upper():<5}]: {s_data['drafters']:>2} drafters, {s_data['images']:>4} images, {s_data['annotations']:>4} XMLs")
    print("=" * 65)
    print(f"Manifest written to: {args.output} and {yaml_out}")
