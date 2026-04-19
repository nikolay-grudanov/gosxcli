"""Typst document parser.

This package provides parsers for extracting document structure from
Typst source files.

Main exports:
    TypstParser: Unified parser that auto-selects best method.
    TypstQueryParser: Parser using typst query command.
    RegexFallbackParser: Fallback parser using regex-based extraction.
"""

# Primary interface - UnifiedParser that chooses best available method
from .unified_parser import UnifiedParser as TypstParser

# Individual parsers (for specialized use cases)
from .typst_query_parser import TypstQueryParser
from .regex_fallback_parser import RegexFallbackParser

__all__ = [
    "TypstParser",
    "TypstQueryParser",
    "RegexFallbackParser",
]
