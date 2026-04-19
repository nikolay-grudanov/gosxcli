"""Configuration for the converter."""

from enum import StrEnum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from .ir.model import CitationStyle


class MathMode(StrEnum):
    """Math rendering mode configuration.

    Attributes:
        NATIVE: Use native DOCX math rendering (OMML).
        IMAGE: Convert math to images.
        FALLBACK: Try native, fall back to image on error.
    """

    NATIVE = "native"
    IMAGE = "image"
    FALLBACK = "fallback"


class RefLabels(BaseModel):
    """Localized reference label names for GOST formatting.

    These labels are used when rendering cross-references in the document.
    Default values follow Russian GOST 7.32-2017 standard.

    Attributes:
        figure: Label for figure references (default: "Рис.").
        table: Label for table references (default: "Табл.").
        equation: Label for equation references (default: "Формула").
        section: Label for section/chapter references (default: "Глава").
        code: Label for code block references (default: "Листинг").
        appendix: Label for appendix references (default: "Приложение").
    """

    figure: str = "Рис."
    table: str = "Табл."
    equation: str = "Формула"
    section: str = "Глава"
    code: str = "Листинг"
    appendix: str = "Приложение"


class Config(BaseModel):
    """Configuration for the Typst to DOCX converter.

    Attributes:
        input_file: Path to the input Typst file.
        output_file: Path to the output DOCX file.
        reference_doc: Optional path to a reference DOCX for styling.
        assets_dir: Directory for assets (images, etc.). Defaults to input file parent.
        debug: Enable debug logging.
        dump_ir: Dump IR to JSON after parsing.
        dump_json: Dump raw JSON from Typst.
        strict_mode: Enable strict mode (exit on errors).
        math_mode: Math rendering mode (native, image, or fallback).
        bibliography_style: Citation style (numeric or author-year).
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        ref_labels: Localized reference label names for GOST formatting.
        benchmark_mode: Enable benchmark mode for performance measurement.
    """

    input_file: Path
    output_file: Path
    reference_doc: Optional[Path] = None
    assets_dir: Optional[Path] = None
    debug: bool = False
    dump_ir: bool = False
    dump_json: bool = False
    strict_mode: bool = False
    math_mode: MathMode = MathMode.FALLBACK
    bibliography_style: CitationStyle = CitationStyle.NUMERIC
    log_level: str = "INFO"
    ref_labels: RefLabels = Field(default_factory=RefLabels)
    benchmark_mode: bool = False

    def model_post_init(self, __context: object) -> None:
        """Initialize assets_dir after model construction."""
        if self.assets_dir is None:
            object.__setattr__(self, "assets_dir", self.input_file.parent)

    def get_label(self, ref_type: str) -> str:
        """Get localized label for reference type.

        Args:
            ref_type: Type of reference (figure, table, equation, chapter, listing).

        Returns:
            Localized label string.
        """
        label_map = {
            "figure": self.ref_labels.figure,
            "table": self.ref_labels.table,
            "equation": self.ref_labels.equation,
            "section": self.ref_labels.section,
            "chapter": self.ref_labels.section,
            "code": self.ref_labels.code,
            "listing": self.ref_labels.code,
            "appendix": self.ref_labels.appendix,
        }
        return label_map.get(ref_type, ref_type.capitalize())


__all__ = ["Config", "MathMode", "RefLabels"]
