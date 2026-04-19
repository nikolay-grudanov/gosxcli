"""Fallback parser using scanner + TypstExtractorV2.

This module provides RegexFallbackParser which uses the existing scanner
and TypstExtractorV2 for regex-based parsing when typst binary is not available.

Typical usage:
    parser = RegexFallbackParser("document.typ")
    doc = parser.extract()
"""

from __future__ import annotations

import logging
from pathlib import Path

import uuid

from ..ir.model import Document
from .extractor_v2 import TypstExtractorV2

logger = logging.getLogger(__name__)


class RegexFallbackParser:
    """Fallback parser using scanner + TypstExtractorV2.

    This parser uses regex-based tokenization (TypstScanner) and
    state-machine extraction (TypstExtractorV2) to parse
    Typst documents when typst binary is not available.

    Attributes:
        file_path: Path to the Typst source file.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def extract(self) -> Document:
        """Extract document structure using regex-based parsing.

        Uses the TypstScanner and TypstExtractorV2 to parse
        the document.

        Returns:
            IR Document with all extracted elements.
        """
        try:
            text = self.file_path.read_text(encoding="utf-8")
        except OSError as e:
            logger.error(f"Failed to read file {self.file_path}: {e}")
            return Document(id=str(uuid.uuid4()))

        extractor = TypstExtractorV2(text, str(self.file_path))
        return extractor.extract()


__all__ = ["RegexFallbackParser"]