"""dataset_inspector.py: Automated Auditor and Statistics Generator for CGHD Dataset."""

import os
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

from src.common.logging import logger
from src.common.io import load_json, save_json, ensure_dir


class DatasetInspector:
    """Inspects and audits local or downloaded CGHD circuit dataset."""

    def __init__(self, data_dir: str = "data/raw/cghd", classes_file: str = "classes.json"):
        self.data_dir = Path(data_dir)
        self.classes_file = Path(classes_file)
        self.classes_map: Dict[str, int] = {}
        self.id_to_class: Dict[int, str] = {}
        self._load_classes()

    def _load_classes(self) -> None:
        if self.classes_file.exists():
            self.classes_map = load_json(self.classes_file)
            self.id_to_class = {v: k for k, v in self.classes_map.items()}
        else:
            logger.warning(f"classes.json not found at {self.classes_file}")

    def inspect(self) -> Dict[str, Any]:
        """Performs full dataset scan across all drafters and annotations."""
        stats = {
            "drafters": [],
            "drafter_count": 0,
            "total_images": 0,
            "total_annotations": 0,
            "total_boxes": 0,
            "total_asc_files": 0,
            "total_segmentation_maps": 0,
            "class_distribution": Counter(),
            "rotation_distribution": Counter(),
            "image_resolutions": Counter(),
            "drafter_stats": {},
            "malformed_annotations": [],
            "unknown_classes": Counter(),
            "classes_with_zero_samples": []
        }

        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist.")
            return stats

        # Discover drafter directories
        drafter_dirs = sorted([d for d in self.data_dir.iterdir() if d.is_dir() and "drafter_" in d.name],
                              key=lambda x: int(x.name.split("_")[1]) if x.name.split("_")[1].lstrip("-").isdigit() else 0)

        stats["drafter_count"] = len(drafter_dirs)
        stats["drafters"] = [d.name for d in drafter_dirs]

        for d_dir in drafter_dirs:
            d_name = d_dir.name
            ann_dir = d_dir / "annotations"
            img_dir = d_dir / "images"
            spice_dir = d_dir / "spice"
            seg_dir = d_dir / "segmentation"

            xml_files = list(ann_dir.glob("*.xml")) if ann_dir.exists() else []
            img_files = list(img_dir.glob("*.[jJ][pP][gG]")) + list(img_dir.glob("*.[jJ][pP][eE][gG]")) + list(img_dir.glob("*.[pP][nN][gG]")) if img_dir.exists() else []
            asc_files = list(spice_dir.glob("*.asc")) if spice_dir.exists() else []
            seg_files = list(seg_dir.glob("*.*")) if seg_dir.exists() else []

            stats["total_annotations"] += len(xml_files)
            stats["total_images"] += len(img_files)
            stats["total_asc_files"] += len(asc_files)
            stats["total_segmentation_maps"] += len(seg_files)

            d_box_count = 0
            d_class_counts = Counter()

            for xml_file in xml_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    # Image resolution
                    size_tag = root.find("size")
                    if size_tag is not None:
                        w = int(size_tag.find("width").text or 0)
                        h = int(size_tag.find("height").text or 0)
                        stats["image_resolutions"][f"{w}x{h}"] += 1

                    # Bounding boxes
                    for obj in root.findall("object"):
                        name_tag = obj.find("name")
                        if name_tag is None or not name_tag.text:
                            stats["malformed_annotations"].append(f"{xml_file}: empty object name")
                            continue

                        class_name = name_tag.text.strip()
                        stats["class_distribution"][class_name] += 1
                        d_class_counts[class_name] += 1
                        d_box_count += 1
                        stats["total_boxes"] += 1

                        if self.classes_map and class_name not in self.classes_map:
                            stats["unknown_classes"][class_name] += 1

                        # Rotation
                        bnd = obj.find("bndbox")
                        if bnd is not None:
                            rot_tag = bnd.find("rotation")
                            rot_val = rot_tag.text if rot_tag is not None and rot_tag.text else "None"
                            stats["rotation_distribution"][rot_val] += 1

                except Exception as e:
                    stats["malformed_annotations"].append(f"{xml_file}: parse error ({e})")

            stats["drafter_stats"][d_name] = {
                "images": len(img_files),
                "annotations": len(xml_files),
                "boxes": d_box_count,
                "asc_files": len(asc_files),
                "segmentations": len(seg_files),
                "unique_classes": len(d_class_counts)
            }

        # Check classes with zero samples
        for cls_name in self.classes_map:
            if cls_name != "__background__" and stats["class_distribution"][cls_name] == 0:
                stats["classes_with_zero_samples"].append(cls_name)

        return stats

    def print_summary(self, stats: Dict[str, Any]) -> None:
        """Prints a human-readable summary of the dataset inspection."""
        print("=" * 65)
        print("             CGHD DATASET INSPECTION REPORT")
        print("=" * 65)
        print(f"Total Drafters:          {stats['drafter_count']}")
        print(f"Total Annotated Images:  {stats['total_annotations']}")
        print(f"Total Image Files:       {stats['total_images']}")
        print(f"Total Bounding Boxes:    {stats['total_boxes']}")
        print(f"Total LTspice (.asc):    {stats['total_asc_files']}")
        print(f"Total Segmentation Maps: {stats['total_segmentation_maps']}")
        print("-" * 65)
        print("Image Resolutions:")
        for res, cnt in stats["image_resolutions"].most_common():
            print(f"  {res:<20} {cnt:>6} images")
        print("-" * 65)
        print(f"Class Frequencies (Top 15 out of {len(stats['class_distribution'])} present):")
        for cls_name, count in stats["class_distribution"].most_common(15):
            print(f"  {cls_name:<35} {count:>6} boxes")
        
        if stats["unknown_classes"]:
            print("-" * 65)
            print("Unknown Classes (Not in classes.json):")
            for cls_name, count in stats["unknown_classes"].items():
                print(f"  {cls_name:<35} {count:>6} boxes")

        if stats["malformed_annotations"]:
            print("-" * 65)
            print(f"Malformed Annotations Found: {len(stats['malformed_annotations'])}")
            for mal in stats["malformed_annotations"][:5]:
                print(f"  - {mal}")

        print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit and inspect CGHD dataset.")
    parser.add_argument("--data-dir", default="data/raw/cghd", help="Path to raw CGHD dataset root")
    parser.add_argument("--classes", default="classes.json", help="Path to classes.json")
    parser.add_argument("--output", default="data/dataset_inspection_report.json", help="Output JSON report path")
    args = parser.parse_args()

    inspector = DatasetInspector(data_dir=args.data_dir, classes_file=args.classes)
    inspection_stats = inspector.inspect()
    inspector.print_summary(inspection_stats)

    # Convert Counters to dicts for JSON serialization
    serializable = {
        k: dict(v) if isinstance(v, Counter) else v
        for k, v in inspection_stats.items()
    }
    save_json(serializable, args.output)
    print(f"Full inspection report written to: {args.output}")
