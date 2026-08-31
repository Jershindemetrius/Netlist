"""test_voc_converter.py: Unit Tests for Pascal VOC to YOLO Conversion."""

import unittest
import tempfile
import json
from pathlib import Path

from src.data.voc_to_yolo import VocToYoloConverter
from src.common.schemas import BoundingBox


class TestVocConverter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        
        # Create mock classes.json
        self.classes_file = self.root / "classes.json"
        with open(self.classes_file, "w", encoding="utf-8") as f:
            json.dump({"__background__": 0, "resistor": 1, "capacitor.unpolarized": 2, "diode": 3}, f)

        # Create mock split manifest
        self.split_file = self.root / "split_manifest.json"
        with open(self.split_file, "w", encoding="utf-8") as f:
            json.dump({
                "splits": {
                    "train": ["drafter_1"],
                    "val": [],
                    "test": []
                }
            }, f)

        # Create mock drafter_1 XML
        d1_xml_dir = self.root / "cghd" / "drafter_1" / "annotations"
        d1_xml_dir.mkdir(parents=True)
        xml_content = """<annotation>
            <size><width>1000</width><height>1000</height></size>
            <object>
                <name>resistor</name>
                <bndbox><xmin>100</xmin><ymin>200</ymin><xmax>300</xmax><ymax>400</ymax></bndbox>
            </object>
            <object>
                <name>diode</name>
                <bndbox><xmin>500</xmin><ymin>600</ymin><xmax>700</xmax><ymax>800</ymax></bndbox>
            </object>
        </annotation>"""
        with open(d1_xml_dir / "C1_D1_P1.xml", "w", encoding="utf-8") as f:
            f.write(xml_content)

        self.converter = VocToYoloConverter(
            data_dir=str(self.root / "cghd"),
            classes_file=str(self.classes_file),
            split_manifest_path=str(self.split_file),
            output_dir=str(self.root / "yolo")
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_bbox_normalization(self):
        box = BoundingBox(xmin=100, ymin=200, xmax=300, ymax=400)
        cx, cy, w, h = box.to_yolo(1000, 1000)
        self.assertAlmostEqual(cx, 0.20)
        self.assertAlmostEqual(cy, 0.30)
        self.assertAlmostEqual(w, 0.20)
        self.assertAlmostEqual(h, 0.20)

    def test_conversion_flow(self):
        report = self.converter.convert(copy_images=False)
        self.assertEqual(report["total_converted_samples"], 1)
        self.assertEqual(report["total_converted_boxes"], 2)

        label_file = self.root / "yolo" / "labels" / "train" / "drafter_1_C1_D1_P1.txt"
        self.assertTrue(label_file.exists())
        with open(label_file, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        self.assertEqual(len(lines), 2)


if __name__ == "__main__":
    unittest.main()
