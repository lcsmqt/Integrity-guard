from __future__ import annotations

import logging
from typing import Optional

DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging(log_level: str = "INFO", logger_name: Optional[str] = None) -> logging.Logger:
    level = getattr(logging, str(log_level).upper(), logging.INFO)
    logging.basicConfig(level=level, format=DEFAULT_FORMAT, force=True)
    logger = logging.getLogger(logger_name or "file_integrity_guard")
    logger.setLevel(level)
    return logger
