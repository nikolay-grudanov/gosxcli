"""Logging configuration."""

import logging
from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("typst_gost_docx")
    logger.setLevel(getattr(logging, level.upper()))

    handler = RichHandler(rich_tracebacks=True)
    handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(handler)
    return logger
