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
    parser.add_argument("--epochs", type=int, default=None, help="Override number of training epochs")
    parser.add_argument("--batch-size", type=int, default=None, help="Override batch size")
    args = parser.parse_args()

    train_yolo_detector(
        config_path=args.config,
        resume=args.resume,
        override_epochs=args.epochs,
        override_batch=args.batch_size,
    )
