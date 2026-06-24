"""Typst document parser.

This package provides the parser layer of the converter:

    - ``TypstScanner`` — tokenises Typst source into a flat stream of
      ``Token`` instances.
    - ``TypstExtractorV2`` — walks the token stream and produces the
      IR (``Document``) used by the writer and the validator.
    - ``ChapterNumberer`` — fills in chapter-local numbering on every
      Section, Figure, Table, and Equation so that cross-references can
      be resolved deterministically.
    - ``RefResolver`` — resolves every ``CrossReference`` IR node,
      populating ``ref_text`` (e.g. ``"Рис. 1.1"``) so the writer
      can render it directly.

The pre-v0.5 alternative parsers (UnifiedParser, TypstQueryParser,
RegexFallbackParser) were retired because the IR-based scanner +
extractor covers everything they were meant to provide. See
``state.md`` for the cleanup history.
"""

from .extractor_v2 import TypstExtractorV2
from .numbering import ChapterNumberer
from .refs import RefResolver
from .scanner import TypstScanner, Token

__all__ = [
    "TypstExtractorV2",
    "TypstScanner",
    "Token",
    "ChapterNumberer",
    "RefResolver",
]
