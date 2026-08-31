"""terminal_templates.py: Class-Aware Terminal Template Manager."""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from src.common.io import load_yaml, load_json
from src.common.logging import logger


class TerminalTemplateManager:
    """Provides class-specific terminal geometry templates and port definitions."""

    def __init__(
        self,
        config_path: str = "configs/terminal_templates.yaml",
        ports_json_path: str = "classes_ports.json"
    ):
        self.config_path = Path(config_path)
        self.ports_json_path = Path(ports_json_path)
        self.templates: Dict[str, Any] = {}
        self.default_template: Dict[str, Any] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        if self.config_path.exists():
            cfg = load_yaml(self.config_path)
            self.default_template = cfg.get("default_fallback", {})
            self.templates = cfg.get("templates", {})
            logger.debug(f"Loaded {len(self.templates)} terminal templates from {self.config_path}")
        elif self.ports_json_path.exists():
            ports = load_json(self.ports_json_path)
            self._build_templates_from_ports(ports)
        else:
            self._load_builtins()

    def _build_templates_from_ports(self, ports_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Converts raw classes_ports.json into template structure."""
        self.default_template = {
            "terminals": [
                {"id": "T1", "name": "connector", "position": [0.0, 0.5], "direction": [-1.0, 0.0]},
                {"id": "T2", "name": "connector", "position": [1.0, 0.5], "direction": [1.0, 0.0]}
            ],
            "is_symmetric": True
        }
        for cls_name, port_list in ports_data.items():
            terminals = []
            for idx, p in enumerate(port_list):
                term_id = f"T{idx+1}"
                name = p.get("name", "connector")
                if name in ["anode", "cathode", "base", "collector", "emitter", "gate", "drain", "source", "positive", "negative"]:
                    term_id = name[:3].upper()
                terminals.append({
                    "id": term_id,
                    "name": name,
                    "position": p.get("position", [0.5, 0.5]),
                    "direction": [-1.0 if p.get("position", [0.5, 0.5])[0] < 0.5 else 1.0, 0.0]
                })
            self.templates[cls_name] = {
                "terminals": terminals,
                "is_symmetric": len(terminals) == 2 and terminals[0]["name"] == terminals[1]["name"]
            }

    def _load_builtins(self) -> None:
        self.default_template = {
            "terminals": [
                {"id": "T1", "name": "connector", "position": [0.0, 0.5], "direction": [-1.0, 0.0]},
                {"id": "T2", "name": "connector", "position": [1.0, 0.5], "direction": [1.0, 0.0]}
            ],
            "is_symmetric": True
        }

    def get_template(self, class_name: str) -> Dict[str, Any]:
        """Retrieves terminal template for a symbol class with fallback to generic 2-terminal."""
        # Exact match
        if class_name in self.templates:
            return self.templates[class_name]

        # Base category match (e.g. "resistor.photo" -> "resistor")
        base_cat = class_name.split(".")[0]
        if base_cat in self.templates:
            return self.templates[base_cat]

        return self.default_template
