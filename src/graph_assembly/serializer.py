"""serializer.py: JSON, SPICE, and Dict Serialization for Circuit Graphs."""

from pathlib import Path
from typing import Dict, Any, Union
from src.common.schemas import CircuitGraph
from src.common.io import save_json, load_json, ensure_dir


class CircuitSerializer:
    """Serializes CircuitGraph to JSON, dictionary, or SPICE netlist text format."""

    @staticmethod
    def to_json_file(graph: CircuitGraph, file_path: Union[str, Path], indent: int = 2) -> None:
        """Writes canonical JSON representation to file."""
        save_json(graph.to_canonical_dict(), file_path, indent=indent)

    @staticmethod
    def to_spice_file(graph: CircuitGraph, file_path: Union[str, Path], title: str = "Extracted Circuit") -> None:
        """Writes SPICE-compatible netlist text to file."""
        ensure_dir(file_path)
        content = graph.to_spice_netlist(title=title)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content + "\n")

    @staticmethod
    def from_json_file(file_path: Union[str, Path]) -> CircuitGraph:
        """Loads CircuitGraph from JSON file."""
        data = load_json(file_path)
        return CircuitGraph.model_validate(data)
