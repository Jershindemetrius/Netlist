"""train.py: Ultralytics YOLO11 Training Script for Hand-Drawn Circuit Detections."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import os
import argparse
from typing import Dict, Any, Optional

from src.common.logging import logger
from src.common.io import load_yaml, ensure_dir


def train_yolo_detector(
    config_path: str = "configs/detection.yaml",
    resume: bool = False,
    override_epochs: Optional[int] = None,
    override_batch: Optional[int] = None,
) -> None:
    """Configures and runs YOLO11 symbol detector training."""
    cfg = load_yaml(config_path)

    model_name = cfg.get("model", {}).get("name", "yolo11s") + ".pt"
    dataset_yaml = cfg.get("data", {}).get("dataset_yaml", "data/processed/yolo/dataset.yaml")
    epochs = override_epochs if override_epochs is not None else cfg.get("training", {}).get("epochs", 100)
    batch_size = override_batch if override_batch is not None else cfg.get("training", {}).get("batch_size", 8)
    img_size = cfg.get("data", {}).get("img_size", 960)
    patience = cfg.get("training", {}).get("patience", 20)
    workers = cfg.get("training", {}).get("workers", 4)
    lr0 = cfg.get("training", {}).get("learning_rate", 0.01)
    optimizer = cfg.get("training", {}).get("optimizer", "AdamW")
    device = cfg.get("training", {}).get("device", "auto")

    checkpoint_dir = Path(cfg.get("training", {}).get("checkpoint_dir", "models/checkpoints"))
    ensure_dir(checkpoint_dir)

    print("=" * 65)
    print("           NETLIST SYMBOL DETECTOR TRAINING")
    print("=" * 65)
    print(f"Model Architecture: {model_name}")
    print(f"Dataset YAML:       {dataset_yaml}")
    print(f"Resolution:         {img_size}x{img_size}")
    print(f"Epochs:             {epochs}")
    print(f"Batch Size:         {batch_size}")
    print(f"Optimizer:          {optimizer} (lr={lr0})")
    print(f"Target Device:      {device}")
    print("=" * 65)

    if not Path(dataset_yaml).exists():
        logger.error(f"YOLO dataset configuration missing at: {dataset_yaml}")
        logger.error("Please run 'python scripts/prepare_dataset.py' first.")
        return

    try:
        import torch
        from ultralytics import YOLO

        cuda_available = torch.cuda.is_available()
        logger.info(f"CUDA Available: {cuda_available}")
        if cuda_available:
            logger.info(f"GPU Device: {torch.cuda.get_device_name(0)}")

        # Load model pretrained backbone
        model = YOLO(model_name)

        # Train model
        results = model.train(
            data=dataset_yaml,
            epochs=epochs,
            imgsz=img_size,
            batch=batch_size,
            workers=workers,
            patience=patience,
            optimizer=optimizer,
            lr0=lr0,
            device=0 if cuda_available else "cpu",
            project=str(checkpoint_dir),
            name="yolo11_circuit",
            exist_ok=True,
            resume=resume,
            amp=cuda_available
        )

        logger.info("Training completed successfully!")
        best_path = checkpoint_dir / "yolo11_circuit" / "weights" / "best.pt"
        if best_path.exists():
            logger.info(f"Best model weights saved to: {best_path}")

    except Exception as e:
        logger.error(f"Error initiating training: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLO11 symbol detector.")
    parser.add_argument("--config", default="configs/detection.yaml", help="Path to detection.yaml")
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
