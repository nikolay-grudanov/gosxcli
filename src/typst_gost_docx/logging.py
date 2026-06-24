"""Logging configuration."""

import logging

from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Настройка логирования с Rich handler.

    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR).

    Returns:
        Настроенный логгер.
    """
    logger = logging.getLogger("typst_gost_docx")
    logger.setLevel(getattr(logging, level.upper()))

    # Предотвращаем дублирование handlers при повторных вызовах
    if not logger.handlers:
        handler = RichHandler(rich_tracebacks=True)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    return logger
