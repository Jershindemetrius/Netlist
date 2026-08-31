"""logging.py: Structured and Pretty Logging for Project NETLIST."""

import logging
import sys
from typing import Optional

def setup_logger(name: str = "netlist", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a formatted logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()
