"""asc_parser.py: Robust LTspice .asc Ground-Truth Schematic Parser into Canonical CircuitGraph."""

import re
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

from src.common.schemas import CircuitGraph, Component, Terminal, BoundingBox
from src.common.logging import logger
from src.common.io import ensure_dir
from src.geometry.terminal_templates import TerminalTemplateManager
from src.graph_assembly.net_builder import DisjointSetUnion
from src.graph_assembly.graph_normalizer import GraphNormalizer


class AscParser:
    """Parses LTspice .asc schematic files into canonical CircuitGraph representation."""

    SYMBOL_CLASS_MAP = {
        "res": "resistor",
        "res2": "resistor",
        "cap": "capacitor.unpolarized",
        "polcap": "capacitor.polarized",
        "ind": "inductor",
        "ind2": "inductor",
        "diode": "diode",
        "led": "diode.light_emitting",
        "zener": "diode.zener",
        "npn": "transistor.bjt",
        "pnp": "transistor.bjt",
        "nmos": "transistor.fet",
        "pmos": "transistor.fet",
        "voltage": "voltage.dc",
        "current": "probe.current",
        "misc/ne555": "integrated_circuit.ne555",
        "misc\\ne555": "integrated_circuit.ne555",
        "ne555": "integrated_circuit.ne555",
        "opamp2": "operational_amplifier",
        "gnd": "gnd"
    }

    def __init__(self):
        self.template_manager = TerminalTemplateManager()

    def parse_file(self, asc_path: str) -> CircuitGraph:
        """Parses a .asc file from disk into a CircuitGraph."""
        with open(asc_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return self.parse_content(content, source_file=Path(asc_path).name)

    def parse_content(self, text: str, source_file: str = "") -> CircuitGraph:
        """Parses the text content of an LTspice .asc schematic."""
        lines = text.splitlines()

        wires: List[Tuple[int, int, int, int]] = []
        flags: List[Tuple[int, int, str]] = []
        raw_symbols: List[Dict[str, Any]] = []
        current_symbol: Optional[Dict[str, Any]] = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if line_str.startswith("WIRE "):
                parts = line_str.split()
                if len(parts) >= 5:
                    wires.append((int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))

            elif line_str.startswith("FLAG "):
                parts = line_str.split()
                if len(parts) >= 4:
                    flags.append((int(parts[1]), int(parts[2]), parts[3]))

            elif line_str.startswith("SYMBOL "):
                parts = line_str.split()
                if len(parts) >= 5:
                    sym_type = parts[1]
                    sym_x = int(parts[2])
                    sym_y = int(parts[3])
                    sym_rot = parts[4]

                    current_symbol = {
                        "type": sym_type,
                        "x": sym_x,
                        "y": sym_y,
                        "rot": sym_rot,
                        "inst_name": None,
                        "value": None
                    }
                    raw_symbols.append(current_symbol)

            elif line_str.startswith("SYMATTR ") and current_symbol is not None:
                parts = line_str.split(maxsplit=2)
                if len(parts) >= 3:
                    attr_name = parts[1]
                    attr_val = parts[2]
                    if attr_name == "InstName":
                        current_symbol["inst_name"] = attr_val
                    elif attr_name == "Value":
                        current_symbol["value"] = attr_val

        # Collect unique wire coordinates
        dsu = DisjointSetUnion()
        all_wire_coords: List[Tuple[int, int]] = []

        for x1, y1, x2, y2 in wires:
            p1_key = f"coord_{x1}_{y1}"
            p2_key = f"coord_{x2}_{y2}"
            dsu.union(p1_key, p2_key)
            all_wire_coords.extend([(x1, y1), (x2, y2)])

        all_wire_coords = list(set(all_wire_coords))

        # Connect flags in DSU
        for fx, fy, f_name in flags:
            f_key = f"coord_{fx}_{fy}"
            dsu.union(f_key, f"flag_{f_name}")

        # Instantiate components and snap pins to nearest wire coordinates
        components: List[Component] = []

        for idx, sym in enumerate(raw_symbols):
            sym_key = sym["type"].lower().replace("\\", "/")
            base_key = sym_key.split("/")[-1]
            
            class_name = self.SYMBOL_CLASS_MAP.get(sym_key, self.SYMBOL_CLASS_MAP.get(base_key, "resistor"))
            inst_id = sym["inst_name"] or f"COMP_{idx+1}"
            
            sx, sy = sym["x"], sym["y"]

            # Template definition for pin count and ids
            template = self.template_manager.get_template(class_name)
            raw_terms = template.get("terminals", [
                {"id": "T1", "name": "connector"},
                {"id": "T2", "name": "connector"}
            ])

            # Find nearby wire coordinates within radius 64px
            nearby_coords = [
                pt for pt in all_wire_coords
                if math.hypot(pt[0] - sx, pt[1] - sy) <= 80.0
            ]
            # Sort by distance from symbol center
            nearby_coords.sort(key=lambda pt: math.hypot(pt[0] - sx, pt[1] - sy))

            comp_terminals: List[Terminal] = []
            used_coords = set()

            for t_idx, t_spec in enumerate(raw_terms):
                t_id = t_spec["id"]
                t_name = t_spec["name"]

                # Assign nearest unused wire coordinate
                assigned_coord = (sx, sy)
                for pt in nearby_coords:
                    if pt not in used_coords:
                        assigned_coord = pt
                        used_coords.add(pt)
                        break

                pin_x, pin_y = assigned_coord
                pin_coord_key = f"coord_{pin_x}_{pin_y}"
                term_ref = f"{inst_id}.{t_id}"
                
                # Union terminal pin in DSU
                dsu.union(term_ref, pin_coord_key)

                comp_terminals.append(
                    Terminal(
                        id=t_id,
                        semantic_name=t_name,
                        position=(float(pin_x), float(pin_y)),
                        confidence=1.0
                    )
                )

            comp = Component(
                id=inst_id,
                type=class_name,
                class_id=0,
                bbox=BoundingBox(xmin=float(sx - 30), ymin=float(sy - 30), xmax=float(sx + 30), ymax=float(sy + 30)),
                center=(float(sx), float(sy)),
                value=sym["value"],
                terminals=comp_terminals
            )
            components.append(comp)

        # Assemble Nets from DSU
        groups = defaultdict(list)
        for comp in components:
            for term in comp.terminals:
                t_ref = f"{comp.id}.{term.id}"
                root = dsu.find(t_ref)
                groups[root].append(t_ref)

        nets: Dict[str, List[str]] = {}
        net_counter = 1
        for root, term_list in sorted(groups.items(), key=lambda x: x[0]):
            is_ground = any(dsu.find(f"flag_{f[2]}") == root for f in flags if f[2] == "0")
            if is_ground:
                nid = "0"
            else:
                nid = f"NET{net_counter}"
                net_counter += 1
            nets[nid] = sorted(term_list)

        raw_graph = CircuitGraph(
            components=components,
            nets=nets,
            metadata={"source_file": source_file, "is_ground_truth": True}
        )

        normalizer = GraphNormalizer()
        return normalizer.normalize(raw_graph)
