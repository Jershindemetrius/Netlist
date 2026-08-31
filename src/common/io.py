"""io.py: Safe I/O Utilities and Intermediate Pipeline Caching."""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
import cv2
import numpy as np


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensures parent directories exist and returns Path object."""
    p = Path(path)
    if p.suffix:
        p.parent.mkdir(parents=True, exist_ok=True)
    else:
        p.mkdir(parents=True, exist_ok=True)
    return p


def load_json(path: Union[str, Path]) -> Any:
    """Safely loads a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, path: Union[str, Path], indent: int = 2) -> None:
    """Safely writes data to a JSON file."""
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """Safely loads a YAML configuration file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(data: Dict[str, Any], path: Union[str, Path]) -> None:
    """Safely writes a dictionary to a YAML file."""
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_image(path: Union[str, Path], grayscale: bool = False) -> np.ndarray:
    """Loads an image with OpenCV handling path conversion."""
    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imread(str(path), flag)
    if img is None:
        raise FileNotFoundError(f"Failed to load image from: {path}")
    return img


def save_image(img: np.ndarray, path: Union[str, Path]) -> None:
    """Saves an image to disk ensuring directory exists."""
    ensure_dir(path)
    cv2.imwrite(str(path), img)


class PipelineCache:
    """Manages intermediate pipeline artifact caching by image ID."""
    
    def __init__(self, cache_dir: Union[str, Path] = "data/cache"):
        self.cache_dir = Path(cache_dir)
        ensure_dir(self.cache_dir)

    def _get_path(self, image_id: str, stage_name: str, ext: str) -> Path:
        clean_id = Path(image_id).stem
        return self.cache_dir / f"{clean_id}_{stage_name}.{ext}"

    def get_json(self, image_id: str, stage_name: str) -> Optional[Any]:
        path = self._get_path(image_id, stage_name, "json")
        if path.exists():
            return load_json(path)
        return None

    def set_json(self, image_id: str, stage_name: str, data: Any) -> None:
        path = self._get_path(image_id, stage_name, "json")
        save_json(data, path)

    def get_image(self, image_id: str, stage_name: str, grayscale: bool = False) -> Optional[np.ndarray]:
        path = self._get_path(image_id, stage_name, "png")
        if path.exists():
            return load_image(path, grayscale=grayscale)
        return None

    def set_image(self, image_id: str, stage_name: str, img: np.ndarray) -> None:
        path = self._get_path(image_id, stage_name, "png")
        save_image(img, path)
