"""prepare_dataset.py: End-to-End Dataset Preparation Script (Audit, Split, Convert VOC -> YOLO)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
from src.common.logging import logger
from src.data.dataset_inspector import DatasetInspector
from src.data.split_drafters import DrafterSplitter
from src.data.voc_to_yolo import VocToYoloConverter
from src.common.io import save_json


def prepare_dataset(
    data_dir: str = "data/raw/cghd",
    classes_file: str = "classes.json",
    split_manifest_path: str = "data/splits/split_manifest.json",
    output_dir: str = "data/processed/yolo",
    seed: int = 42
) -> None:
    """Audits CGHD dataset, generates drafter-isolated split, and converts VOC to YOLO format."""
    print("=" * 65)
    print("             STAGE 0: DATASET PREPARATION")
    print("=" * 65)

    # 1. Audit Dataset
    logger.info("Auditing raw dataset...")
    inspector = DatasetInspector(data_dir=data_dir, classes_file=classes_file)
    stats = inspector.inspect()
    inspector.print_summary(stats)

    # 2. Drafter Split
    logger.info("Generating drafter-isolated splits...")
    splitter = DrafterSplitter(data_dir=data_dir, seed=seed)
    manifest = splitter.generate_split()

    manifest_path = Path(split_manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(manifest, manifest_path)
    logger.info(f"Saved split manifest to: {manifest_path}")

    # 3. Convert VOC -> YOLO
    logger.info("Converting VOC XML to YOLO format...")
    converter = VocToYoloConverter(
        data_dir=data_dir,
        classes_file=classes_file,
        split_manifest_path=split_manifest_path,
        output_dir=output_dir
    )
    conv_report = converter.convert(copy_images=True)
    logger.info(f"Dataset preparation complete! YOLO dataset ready at: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare dataset for YOLO training.")
    parser.add_argument("--data-dir", default="data/raw/cghd", help="Path to raw CGHD dataset")
    parser.add_argument("--classes", default="classes.json", help="Path to classes.json")
    parser.add_argument("--split", default="data/splits/split_manifest.json", help="Path to split manifest")
    parser.add_argument("--output", default="data/processed/yolo", help="Path to output YOLO dataset")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for split reproducibility")
    args = parser.parse_args()

    prepare_dataset(
        data_dir=args.data_dir,
        classes_file=args.classes,
        split_manifest_path=args.split,
        output_dir=args.output,
        seed=args.seed
    )
