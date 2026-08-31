"""graph_normalizer.py: Deterministic Canonical Graph Normalization."""

from typing import List, Dict, Tuple, Any
from collections import defaultdict
from src.common.schemas import CircuitGraph, Component, Terminal


class GraphNormalizer:
    """Normalizes CircuitGraphs to deterministic canonical forms for evaluation and comparison."""

    PREFIX_MAP = {
        "resistor": "R",
        "resistor.adjustable": "R",
        "resistor.photo": "R",
        "capacitor.unpolarized": "C",
        "capacitor.polarized": "C",
        "capacitor.adjustable": "C",
        "inductor": "L",
        "inductor.ferrite": "L",
        "inductor.coupled": "L",
        "transformer": "T",
        "diode": "D",
        "diode.light_emitting": "D",
        "diode.zener": "D",
        "diode.thyrector": "D",
        "transistor.bjt": "Q",
        "transistor.fet": "Q",
        "transistor.photo": "Q",
        "voltage.dc": "V",
        "voltage.ac": "V",
        "voltage.battery": "V",
        "integrated_circuit": "U",
        "integrated_circuit.ne555": "U",
        "operational_amplifier": "U",
        "operational_amplifier.schmitt_trigger": "U",
        "gnd": "GND",
        "vss": "VSS",
        "switch": "S",
        "relay": "K",
        "fuse": "F",
        "lamp": "LAMP",
        "crystal": "X"
    }

    @classmethod
    def get_component_prefix(cls, class_name: str) -> str:
        """Returns standard SPICE letter prefix for class name."""
        if class_name in cls.PREFIX_MAP:
            return cls.PREFIX_MAP[class_name]
        base = class_name.split(".")[0]
        return cls.PREFIX_MAP.get(base, "U")

    def normalize(self, graph: CircuitGraph) -> CircuitGraph:
        """Converts CircuitGraph to canonical normalized form."""
        # 1. Sort components by spatial reading order (top-to-bottom, left-to-right)
        # using center coordinates
        def spatial_sort_key(c: Component) -> Tuple[float, float, str]:
            # Quantize y-coordinate to tolerance rows
            y_row = round(c.center[1] / 30.0) * 30.0
            return (y_row, c.center[0], c.type)

        sorted_components = sorted(graph.components, key=spatial_sort_key)

        # 2. Assign canonical IDs (R1, R2, C1, etc.)
        id_mapping: Dict[str, str] = {} # old_id -> new_canonical_id
        prefix_counters: Dict[str, int] = defaultdict(int)

        canonical_components: List[Component] = []

        for comp in sorted_components:
            prefix = self.get_component_prefix(comp.type)
            if prefix in ["GND", "VSS"]:
                prefix_counters[prefix] += 1
                new_id = f"{prefix}{prefix_counters[prefix]}"
            else:
                prefix_counters[prefix] += 1
                new_id = f"{prefix}{prefix_counters[prefix]}"

            id_mapping[comp.id] = new_id

            # Create updated component copy
            new_terminals: List[Terminal] = []
            for term in sorted(comp.terminals, key=lambda t: t.id):
                new_terminals.append(
                    Terminal(
                        id=term.id,
                        semantic_name=term.semantic_name,
                        position=term.position,
                        normalized_position=term.normalized_position,
                        direction=term.direction,
                        confidence=term.confidence,
                        connected_net=None # updated in net reconstruction
                    )
                )

            canonical_components.append(
                Component(
                    id=new_id,
                    type=comp.type,
                    class_id=comp.class_id,
                    bbox=comp.bbox,
                    center=comp.center,
                    orientation=comp.orientation,
                    orientation_confidence=comp.orientation_confidence,
                    confidence=comp.confidence,
                    value=comp.value,
                    terminals=new_terminals
                )
            )

        # 3. Update nets with new component IDs
        remapped_nets: Dict[str, List[str]] = {}
        for net_id, term_refs in graph.nets.items():
            remapped_refs = []
            for ref in term_refs:
                if "." in ref:
                    old_cid, tid = ref.split(".", 1)
                    new_cid = id_mapping.get(old_cid, old_cid)
                    remapped_refs.append(f"{new_cid}.{tid}")
                else:
                    new_cid = id_mapping.get(ref, ref)
                    remapped_refs.append(new_cid)
            remapped_nets[net_id] = sorted(remapped_refs)

        # 4. Canonical sorting of nets by their lexicographically smallest terminal reference
        sorted_net_entries = sorted(
            remapped_nets.items(),
            key=lambda item: (min(item[1]) if item[1] else "", item[0])
        )

        canonical_nets: Dict[str, List[str]] = {}
        net_relabel: Dict[str, str] = {}
        net_idx = 1

        for old_nid, term_list in sorted_net_entries:
            # Special ground net handling
            is_ground = any("GND" in t for t in term_list)
            if is_ground:
                new_nid = "0"
            else:
                new_nid = f"NET{net_idx}"
                net_idx += 1

            net_relabel[old_nid] = new_nid
            canonical_nets[new_nid] = sorted(term_list)

        # 5. Update terminals with canonical net IDs
        term_to_net = {}
        for nid, t_list in canonical_nets.items():
            for t_ref in t_list:
                term_to_net[t_ref] = nid

        for comp in canonical_components:
            for term in comp.terminals:
                ref = f"{comp.id}.{term.id}"
                term.connected_net = term_to_net.get(ref, None)

        return CircuitGraph(
            components=canonical_components,
            nets=canonical_nets,
            metadata=graph.metadata
        )
