"""voc_to_yolo.py: Converts CGHD Pascal VOC XML Annotations to YOLO Format.

Preserves drafter-isolated splits, validates coordinates, maps class names via classes.json,
and generates dataset.yaml for YOLO11 training.
"""

import os
import shutil
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

from src.common.logging import logger
from src.common.io import load_json, save_json, save_yaml, ensure_dir
from src.common.schemas import BoundingBox


class VocToYoloConverter:
    """Converts Pascal VOC XML annotations to YOLO format organized by drafter splits."""

    def __init__(
        self,
        data_dir: str = "data/raw/cghd",
        classes_file: str = "classes.json",
        split_manifest_path: str = "data/splits/split_manifest.json",
        output_dir: str = "data/processed/yolo"
    ):
        self.data_dir = Path(data_dir)
        self.classes_file = Path(classes_file)
        self.split_manifest_path = Path(split_manifest_path)
        self.output_dir = Path(output_dir)

        self.classes_map: Dict[str, int] = {}
        self.id_to_class: Dict[int, str] = {}
        self._load_classes()

    def _load_classes(self) -> None:
        if not self.classes_file.exists():
            raise FileNotFoundError(f"classes.json not found at {self.classes_file}")
        raw_map = load_json(self.classes_file)
        
        # Build 0-indexed contiguous YOLO class map excluding __background__ if present
        # In CGHD, classes are indexed 0..61 where 0 is __background__.
        # For YOLO detection, we map non-background classes to contiguous 0..N-1 IDs or preserve classes.json
        # Here we preserve standard 0..N-1 classes.
        self.classes_map = {}
        self.id_to_class = {}
        
        # Sort classes by their integer values
        sorted_classes = sorted([(k, v) for k, v in raw_map.items() if k != "__background__"], key=lambda x: x[1])
        for yolo_idx, (name, orig_id) in enumerate(sorted_classes):
            self.classes_map[name] = yolo_idx
            self.id_to_class[yolo_idx] = name

    def convert_box(
        self,
        xmin: float,
        ymin: float,
        xmax: float,
        ymax: float,
        img_width: int,
        img_height: int
    ) -> Optional[Tuple[float, float, float, float]]:
        """Converts pixel bounding box to normalized YOLO format with clipping & validation."""
        if img_width <= 0 or img_height <= 0:
            return None
        
        # Clip to image boundaries
        xmin = max(0.0, min(float(xmin), float(img_width)))
        ymin = max(0.0, min(float(ymin), float(img_height)))
        xmax = max(0.0, min(float(xmax), float(img_width)))
        ymax = max(0.0, min(float(ymax), float(img_height)))

        w = xmax - xmin
        h = ymax - ymin

        if w <= 1.0 or h <= 1.0:
            return None  # Ignore degenerate / invisible boxes

        cx = (xmin + xmax) / 2.0 / img_width
        cy = (ymin + ymax) / 2.0 / img_height
        norm_w = w / img_width
        norm_h = h / img_height

        return (
            max(0.0, min(1.0, cx)),
            max(0.0, min(1.0, cy)),
            max(0.0, min(1.0, norm_w)),
            max(0.0, min(1.0, norm_h))
        )

    def convert(self, copy_images: bool = True) -> Dict[str, Any]:
        """Runs the complete conversion process across all splits."""
        if not self.split_manifest_path.exists():
            raise FileNotFoundError(f"Split manifest not found at {self.split_manifest_path}")

        split_manifest = load_json(self.split_manifest_path)
        splits = split_manifest["splits"]

        report = {
            "splits": {},
            "total_converted_samples": 0,
            "total_converted_boxes": 0,
            "rejected_boxes": 0,
            "unknown_class_boxes": 0,
            "class_counts": Counter(),
            "output_directory": str(self.output_dir)
        }

        # Setup YOLO folder hierarchy
        for split_name in ["train", "val", "test"]:
            ensure_dir(self.output_dir / "images" / split_name)
            ensure_dir(self.output_dir / "labels" / split_name)
            report["splits"][split_name] = {"images": 0, "labels": 0, "boxes": 0}

        for split_name, drafter_list in splits.items():
            for drafter_name in drafter_list:
                d_dir = self.data_dir / drafter_name
                ann_dir = d_dir / "annotations"
                img_dir = d_dir / "images"

                if not ann_dir.exists():
                    continue

                for xml_file in ann_dir.glob("*.xml"):
                    try:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()

                        # Read dimensions
                        size_tag = root.find("size")
                        if size_tag is None:
                            continue
                        img_w = int(size_tag.find("width").text or 0)
                        img_h = int(size_tag.find("height").text or 0)

                        yolo_lines = []

                        for obj in root.findall("object"):
                            name_tag = obj.find("name")
                            if name_tag is None or not name_tag.text:
                                continue
                            class_name = name_tag.text.strip()

                            if class_name not in self.classes_map:
                                report["unknown_class_boxes"] += 1
                                continue

                            class_id = self.classes_map[class_name]

                            bnd = obj.find("bndbox")
                            if bnd is None:
                                continue

                            xmin = float(bnd.find("xmin").text or 0)
                            ymin = float(bnd.find("ymin").text or 0)
                            xmax = float(bnd.find("xmax").text or 0)
                            ymax = float(bnd.find("ymax").text or 0)

                            yolo_box = self.convert_box(xmin, ymin, xmax, ymax, img_w, img_h)
                            if yolo_box is None:
                                report["rejected_boxes"] += 1
                                continue

                            cx, cy, nw, nh = yolo_box
                            yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
                            report["class_counts"][class_name] += 1
                            report["total_converted_boxes"] += 1
                            report["splits"][split_name]["boxes"] += 1

                        # Save label file
                        sample_stem = f"{drafter_name}_{xml_file.stem}"
                        label_out_path = self.output_dir / "labels" / split_name / f"{sample_stem}.txt"
                        with open(label_out_path, "w", encoding="utf-8") as lf:
                            lf.write("\n".join(yolo_lines) + ("\n" if yolo_lines else ""))

                        report["splits"][split_name]["labels"] += 1
                        report["total_converted_samples"] += 1

                        # Handle image copy / symlink
                        if copy_images and img_dir.exists():
                            # Match possible extensions
                            matched_img = None
                            for ext in [".jpg", ".jpeg", ".png", ".JPG"]:
                                candidate = img_dir / f"{xml_file.stem}{ext}"
                                if candidate.exists():
                                    matched_img = candidate
                                    break

                            if matched_img:
                                dest_img = self.output_dir / "images" / split_name / f"{sample_stem}{matched_img.suffix}"
                                shutil.copy2(matched_img, dest_img)
                                report["splits"][split_name]["images"] += 1

                    except Exception as e:
                        logger.error(f"Error processing {xml_file}: {e}")

        # Emit dataset.yaml
        self.generate_dataset_yaml()

        return report

    def generate_dataset_yaml(self) -> Path:
        """Generates dataset.yaml for Ultralytics YOLO training."""
        yaml_data = {
            "path": str(self.output_dir.resolve()),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "nc": len(self.id_to_class),
            "names": {idx: name for idx, name in sorted(self.id_to_class.items())}
        }
        yaml_path = self.output_dir / "dataset.yaml"
        save_yaml(yaml_data, yaml_path)
        logger.info(f"Generated YOLO dataset.yaml at {yaml_path}")
        return yaml_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CGHD Pascal VOC to YOLO format.")
    parser.add_argument("--data-dir", default="data/raw/cghd", help="Path to raw CGHD dataset")
    parser.add_argument("--classes", default="classes.json", help="Path to classes.json")
    parser.add_argument("--split", default="data/splits/split_manifest.json", help="Path to split manifest")
    parser.add_argument("--output", default="data/processed/yolo", help="Output YOLO dataset directory")
    parser.add_argument("--no-copy", action="store_true", help="Do not copy images, only write labels")
    args = parser.parse_args()

    converter = VocToYoloConverter(
        data_dir=args.data_dir,
        classes_file=args.classes,
        split_manifest_path=args.split,
        output_dir=args.output
    )

    conv_report = converter.convert(copy_images=not args.no_copy)
    
    print("=" * 65)
    print("           VOC TO YOLO CONVERSION COMPLETED")
    print("=" * 65)
    print(f"Total Samples: {conv_report['total_converted_samples']}")
    print(f"Total Boxes:   {conv_report['total_converted_boxes']}")
    print(f"Rejected:      {conv_report['rejected_boxes']}")
    print(f"Unknown:       {conv_report['unknown_class_boxes']}")
    print("-" * 65)
    for s_name, s_info in conv_report["splits"].items():
        print(f"Split [{s_name.upper():<5}]: {s_info['images']} images, {s_info['labels']} label files, {s_info['boxes']} boxes")
    print("=" * 65)
