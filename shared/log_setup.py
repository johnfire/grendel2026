"""Structured JSON logging setup for all Grendel nodes."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


class _JSONFormatter(logging.Formatter):
    """Emits one JSON object per log line with ISO 8601 timestamps."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "source": f"{record.module}.{record.funcName}",
            "message": record.getMessage(),
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry)


def setup_logging(node_name: str, log_level: str = "INFO") -> logging.Logger:
    """Configure structured logging for a Grendel node.

    Writes JSON logs to both stdout and ~/logs/grendel/<node_name>.log.
    Creates the log directory if it does not exist.

    Args:
        node_name: Name of the node (e.g. "brain", "hearing").
        log_level: Logging level string — DEBUG, INFO, WARNING, ERROR, CRITICAL.

    Returns:
        Configured root logger.
    """
    log_dir = Path.home() / "logs" / "grendel"
    log_dir.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, log_level.upper(), logging.INFO)
    formatter = _JSONFormatter()

    # Stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # File handler — one log file per node
    file_handler = logging.FileHandler(log_dir / f"{node_name}.log")
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(stdout_handler)
    root.addHandler(file_handler)

    # Silence noisy third-party loggers
    logging.getLogger("paho").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return root
