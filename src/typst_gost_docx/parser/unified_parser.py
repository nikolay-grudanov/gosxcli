"""Unified parser - chooses best available extraction method.

This module provides the UnifiedParser class which selects between
TypstQueryParser (preferred) and RegexFallbackParser based on
availability of the typst binary.

Typical usage:
    from typst_gost_docx.parser import TypstParser
    doc = TypstParser("document.typ").extract()
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from ..ir.model import Document
from .regex_fallback_parser import RegexFallbackParser
from .typst_query_parser import TypstQueryParser

logger = logging.getLogger(__name__)

# Type alias for parser interfaces
Parser = TypstQueryParser | RegexFallbackParser


class UnifiedParser:
    """Unified parser that chooses best available extraction method.

    This parser checks for typst binary availability and selects:
    - TypstQueryParser if typst is available (preferred)
    - RegexFallbackParser if typst is not available

    Attributes:
        file_path: Path to the Typst source file.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self._parser: Parser = self._choose_parser()

    def _has_typst(self) -> bool:
        """Check if typst binary is available.

        Returns:
            True if typst binary is found in PATH.
        """
        return shutil.which("typst") is not None

    def _choose_parser(self) -> Parser:
        """Choose appropriate parser based on availability.

        Returns:
            TypstQueryParser if available, otherwise RegexFallbackParser.
        """
        if self._has_typst():
            logger.debug("Using TypstQueryParser (typst query)")
            return TypstQueryParser(str(self.file_path))
        else:
            logger.debug("Using RegexFallbackParser (regex-based)")
            return RegexFallbackParser(str(self.file_path))

    def extract(self) -> Document:
        """Extract document using the chosen parser.

        Returns:
            IR Document with all extracted elements.
        """
        return self._parser.extract()

    @property
    def parser_name(self) -> str:
        """Get the name of the active parser.

        Returns:
            Parser class name as string.
        """
        return self._parser.__class__.__name__


__all__ = ["UnifiedParser"]
