"""train_detector.py: Standalone CLI Launcher for Detector Training."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
from src.detection.train import train_yolo_detector

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLO symbol detector.")
    parser.add_argument("--config", default="configs/detection.yaml", help="Path to config YAML")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    args = parser.parse_args()

    train_yolo_detector(config_path=args.config, resume=args.resume)
