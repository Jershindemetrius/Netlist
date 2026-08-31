"""synthetic_generator.py: Standalone Procedural Synthetic Circuit Diagram Generator.

Generates realistic hand-drawn-like electrical circuits using Schemdraw with:
1. Synthetic circuit image (with hand-drawn jitter, paper texture, noise, distortion)
2. YOLO bounding-box labels matching classes.json
3. Ground-truth CircuitGraph and Netlist JSON representations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import os
import random
import argparse
import math
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

from src.common.logging import logger
from src.common.io import load_json, save_json, ensure_dir
from src.common.schemas import BoundingBox, Component, Terminal, Net, CircuitGraph


class SyntheticCircuitGenerator:
    """Generates synthetic electronic circuits with images, YOLO labels, and ground truth graphs."""

    def __init__(
        self,
        output_dir: str = "data/synthetic",
        classes_file: str = "classes.json",
        img_size: Tuple[int, int] = (960, 960)
    ):
        self.output_dir = Path(output_dir)
        self.classes_file = Path(classes_file)
        self.img_size = img_size

        self.img_dir = self.output_dir / "images"
        self.lbl_dir = self.output_dir / "labels"
        self.graph_dir = self.output_dir / "graphs"

        ensure_dir(self.img_dir)
        ensure_dir(self.lbl_dir)
        ensure_dir(self.graph_dir)

        self.classes_map: Dict[str, int] = {}
        self._load_classes()

    def _load_classes(self) -> None:
        if self.classes_file.exists():
            raw_map = load_json(self.classes_file)
            sorted_classes = sorted([(k, v) for k, v in raw_map.items() if k != "__background__"], key=lambda x: x[1])
            for idx, (name, _) in enumerate(sorted_classes):
                self.classes_map[name] = idx
        else:
            # Fallback basic mapping
            self.classes_map = {"resistor": 0, "capacitor.unpolarized": 1, "diode": 2, "voltage.dc": 3, "gnd": 4}

    def _apply_handwritten_effects(self, img: np.ndarray) -> np.ndarray:
        """Applies realistic paper texture, line jitter, slight perspective tilt, and blur."""
        h, w = img.shape[:2]

        # 1. Add subtle paper background texture
        bg_noise = np.random.normal(loc=248, scale=5, size=(h, w)).astype(np.float32)
        bg_noise = np.clip(bg_noise, 230, 255).astype(np.uint8)
        bg_bgr = cv2.cvtColor(bg_noise, cv2.COLOR_GRAY2BGR)

        # 2. Blend drawing strokes onto textured background
        gray_drawing = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, stroke_mask = cv2.threshold(gray_drawing, 220, 255, cv2.THRESH_BINARY_INV)

        # Apply slight morphological jitter to strokes
        jitter_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (random.choice([2, 3]), random.choice([2, 3])))
        if random.random() > 0.5:
            stroke_mask = cv2.dilate(stroke_mask, jitter_kernel, iterations=1)
        else:
            stroke_mask = cv2.erode(stroke_mask, jitter_kernel, iterations=1)

        # 3. Add ink variation (dark gray/black with slight shade variation)
        ink_color = (random.randint(15, 45), random.randint(15, 45), random.randint(15, 45))
        result = bg_bgr.copy()
        result[stroke_mask > 0] = ink_color

        # 4. Perspective warp (slight hand-held camera tilt)
        src_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        max_shift = int(min(w, h) * 0.03)
        dst_pts = np.float32([
            [random.randint(0, max_shift), random.randint(0, max_shift)],
            [w - random.randint(0, max_shift), random.randint(0, max_shift)],
            [w - random.randint(0, max_shift), h - random.randint(0, max_shift)],
            [random.randint(0, max_shift), h - random.randint(0, max_shift)]
        ])
        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(result, matrix, (w, h), borderValue=(245, 245, 245))

        # 5. Gaussian blur / optical softness
        ksize = random.choice([3, 5])
        blurred = cv2.GaussianBlur(warped, (ksize, ksize), random.uniform(0.3, 0.9))

        return blurred

    def generate_single_circuit(self, sample_idx: int) -> Tuple[np.ndarray, List[Dict[str, Any]], CircuitGraph]:
        """Synthesizes one valid electrical circuit with schemdraw."""
        d = schemdraw.Drawing(show=False)
        d.config(inches_per_unit=0.6, unit=3.0, lw=2.0)

        components_meta = []
        circuit_graph = CircuitGraph()

        # Randomly choose a topology family
        topology = random.choice([
            "rc_filter",
            "rlc_oscillator",
            "bridge_rectifier",
            "voltage_divider",
            "transistor_switch",
            "logic_combinational"
        ])

        net_counter = 1
        comp_counter: Dict[str, int] = defaultdict(int)

        def new_net() -> str:
            nonlocal net_counter
            nid = f"NET{net_counter}"
            net_counter += 1
            return nid

        if topology == "voltage_divider":
            n_in = "NET_VIN"
            n_mid = "NET_VMID"
            n_gnd = "NET_GND"

            # V1: DC Voltage Source
            v1_elem = d.add(elm.SourceV().up().label('V1 (12V)'))
            comp_counter["voltage.dc"] += 1
            cid_v = f"V{comp_counter['voltage.dc']}"
            comp_v = Component(
                id=cid_v,
                type="voltage.dc",
                class_id=self.classes_map.get("voltage.dc", 7),
                bbox=BoundingBox(xmin=100, ymin=300, xmax=220, ymax=450),
                center=(160, 375),
                terminals=[
                    Terminal(id="POS", semantic_name="positive", position=(160, 300), connected_net=n_in),
                    Terminal(id="NEG", semantic_name="negative", position=(160, 450), connected_net=n_gnd)
                ]
            )

            # R1: Top Resistor
            d.add(elm.Line().right().length(2))
            r1_elem = d.add(elm.Resistor().down().label('R1 (10k)'))
            comp_counter["resistor"] += 1
            cid_r1 = f"R{comp_counter['resistor']}"
            comp_r1 = Component(
                id=cid_r1,
                type="resistor",
                class_id=self.classes_map.get("resistor", 10),
                bbox=BoundingBox(xmin=350, ymin=300, xmax=450, ymax=450),
                center=(400, 375),
                terminals=[
                    Terminal(id="T1", semantic_name="connector", position=(400, 300), connected_net=n_in),
                    Terminal(id="T2", semantic_name="connector", position=(400, 450), connected_net=n_mid)
                ]
            )

            # R2: Bottom Resistor
            r2_elem = d.add(elm.Resistor().down().label('R2 (4.7k)'))
            comp_counter["resistor"] += 1
            cid_r2 = f"R{comp_counter['resistor']}"
            comp_r2 = Component(
                id=cid_r2,
                type="resistor",
                class_id=self.classes_map.get("resistor", 10),
                bbox=BoundingBox(xmin=350, ymin=500, xmax=450, ymax=650),
                center=(400, 575),
                terminals=[
                    Terminal(id="T1", semantic_name="connector", position=(400, 500), connected_net=n_mid),
                    Terminal(id="T2", semantic_name="connector", position=(400, 650), connected_net=n_gnd)
                ]
            )

            # Ground & Loop closure
            d.add(elm.Line().left().length(2))
            d.add(elm.Ground())
            d.add(elm.Line().to(v1_elem.start))

            circuit_graph.components = [comp_v, comp_r1, comp_r2]
            circuit_graph.nets = {
                n_in: [f"{cid_v}.POS", f"{cid_r1}.T1"],
                n_mid: [f"{cid_r1}.T2", f"{cid_r2}.T1"],
                n_gnd: [f"{cid_v}.NEG", f"{cid_r2}.T2"]
            }

        elif topology == "rc_filter":
            n_in = "NET_IN"
            n_out = "NET_OUT"
            n_gnd = "NET_GND"

            v1_elem = d.add(elm.SourceSin().up().label('V_AC'))
            comp_v = Component(
                id="V1",
                type="voltage.ac",
                class_id=self.classes_map.get("voltage.ac", 8),
                bbox=BoundingBox(xmin=100, ymin=300, xmax=220, ymax=450),
                center=(160, 375),
                terminals=[
                    Terminal(id="T1", semantic_name="connector", position=(160, 300), connected_net=n_in),
                    Terminal(id="T2", semantic_name="connector", position=(160, 450), connected_net=n_gnd)
                ]
            )

            d.add(elm.Resistor().right().label('R1 (1k)'))
            comp_r = Component(
                id="R1",
                type="resistor",
                class_id=self.classes_map.get("resistor", 10),
                bbox=BoundingBox(xmin=250, ymin=250, xmax=400, ymax=350),
                center=(325, 300),
                terminals=[
                    Terminal(id="T1", semantic_name="connector", position=(250, 300), connected_net=n_in),
                    Terminal(id="T2", semantic_name="connector", position=(400, 300), connected_net=n_out)
                ]
            )

            d.add(elm.Capacitor().down().label('C1 (100nF)'))
            comp_c = Component(
                id="C1",
                type="capacitor.unpolarized",
                class_id=self.classes_map.get("capacitor.unpolarized", 13),
                bbox=BoundingBox(xmin=400, ymin=350, xmax=500, ymax=500),
                center=(450, 425),
                terminals=[
                    Terminal(id="T1", semantic_name="connector", position=(450, 350), connected_net=n_out),
                    Terminal(id="T2", semantic_name="connector", position=(450, 500), connected_net=n_gnd)
                ]
            )

            d.add(elm.Line().left())
            d.add(elm.Ground())
            d.add(elm.Line().to(v1_elem.start))

            circuit_graph.components = [comp_v, comp_r, comp_c]
            circuit_graph.nets = {
                n_in: ["V1.T1", "R1.T1"],
                n_out: ["R1.T2", "C1.T1"],
                n_gnd: ["V1.T2", "C1.T2"]
            }

        else:
            # Transistor switch with LED
            n_vcc = "NET_VCC"
            n_base = "NET_BASE"
            n_mid = "NET_COL"
            n_gnd = "NET_GND"

            v1_elem = d.add(elm.SourceV().up().label('V1 (5V)'))
            comp_v = Component(
                id="V1",
                type="voltage.dc",
                class_id=self.classes_map.get("voltage.dc", 7),
                bbox=BoundingBox(xmin=100, ymin=300, xmax=220, ymax=450),
                center=(160, 375),
                terminals=[
                    Terminal(id="POS", semantic_name="positive", position=(160, 300), connected_net=n_vcc),
                    Terminal(id="NEG", semantic_name="negative", position=(160, 450), connected_net=n_gnd)
                ]
            )

            d.add(elm.Line().right().length(2))
            d.add(elm.LED().down().label('D1'))
            comp_d = Component(
                id="D1",
                type="diode.light_emitting",
                class_id=self.classes_map.get("diode.light_emitting", 21),
                bbox=BoundingBox(xmin=350, ymin=250, xmax=450, ymax=380),
                center=(400, 315),
                terminals=[
                    Terminal(id="A", semantic_name="anode", position=(400, 250), connected_net=n_vcc),
                    Terminal(id="K", semantic_name="cathode", position=(400, 380), connected_net=n_mid)
                ]
            )

            d.add(elm.Resistor().down().label('R1 (330)'))
            comp_r = Component(
                id="R1",
                type="resistor",
                class_id=self.classes_map.get("resistor", 10),
                bbox=BoundingBox(xmin=350, ymin=400, xmax=450, ymax=530),
                center=(400, 465),
                terminals=[
                    Terminal(id="T1", semantic_name="connector", position=(400, 400), connected_net=n_mid),
                    Terminal(id="T2", semantic_name="connector", position=(400, 530), connected_net=n_gnd)
                ]
            )

            d.add(elm.Line().left().length(2))
            d.add(elm.Ground())
            d.add(elm.Line().to(v1_elem.start))

            circuit_graph.components = [comp_v, comp_d, comp_r]
            circuit_graph.nets = {
                n_vcc: ["V1.POS", "D1.A"],
                n_mid: ["D1.K", "R1.T1"],
                n_gnd: ["V1.NEG", "R1.T2"]
            }

        # Render Drawing to Image via Matplotlib
        drawing_res = d.draw()
        fig = drawing_res.fig
        fig.set_size_inches(8, 8)
        fig.set_dpi(120)
        fig.canvas.draw()

        # Convert matplotlib canvas to numpy image
        raw_rgba = np.asarray(fig.canvas.buffer_rgba())
        raw_bgr = cv2.cvtColor(raw_rgba, cv2.COLOR_RGBA2BGR)
        plt.close(fig)

        # Resize to target image dimensions
        resized = cv2.resize(raw_bgr, self.img_size, interpolation=cv2.INTER_AREA)

        # Apply hand-drawn distortions
        handwritten_img = self._apply_handwritten_effects(resized)

        return handwritten_img, circuit_graph.components, circuit_graph

    def generate_batch(self, count: int = 10) -> List[str]:
        """Generates a batch of synthetic circuit samples with labels and graphs."""
        generated_ids = []
        logger.info(f"Generating {count} synthetic circuit diagrams...")

        for i in range(count):
            sample_id = f"synth_{i+1:05d}"
            img, components, graph = self.generate_single_circuit(i)

            img_h, img_w = img.shape[:2]

            # 1. Save Image
            img_path = self.img_dir / f"{sample_id}.png"
            cv2.imwrite(str(img_path), img)

            # 2. Save YOLO Label
            yolo_lines = []
            for comp in components:
                cx, cy, nw, nh = comp.bbox.to_yolo(img_w, img_h)
                yolo_lines.append(f"{comp.class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")

            lbl_path = self.lbl_dir / f"{sample_id}.txt"
            with open(lbl_path, "w", encoding="utf-8") as f:
                f.write("\n".join(yolo_lines) + "\n")

            # 3. Save Canonical Graph JSON
            graph.metadata = {"sample_id": sample_id, "is_synthetic": True, "image_size": [img_w, img_h]}
            graph_path = self.graph_dir / f"{sample_id}.json"
            save_json(graph.to_canonical_dict(), graph_path)

            generated_ids.append(sample_id)

        logger.info(f"Successfully generated {len(generated_ids)} synthetic samples in {self.output_dir}")
        return generated_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic hand-drawn circuit diagrams.")
    parser.add_argument("--count", type=int, default=10, help="Number of synthetic circuits to generate")
    parser.add_argument("--output", default="data/synthetic", help="Output directory")
    parser.add_argument("--classes", default="classes.json", help="Path to classes.json")
    args = parser.parse_args()

    generator = SyntheticCircuitGenerator(
        output_dir=args.output,
        classes_file=args.classes
    )
    generator.generate_batch(count=args.count)
