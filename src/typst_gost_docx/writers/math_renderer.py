"""Math renderer for converting LaTeX to OMML."""

from __future__ import annotations

import logging
from typing import Literal

from lxml.etree import Element  # type: ignore[import-untyped]


class MathRenderer:
    """Renderer for LaTeX math equations to OMML format.

    Supports three rendering modes:
    - native: Only OMML, raises exception on conversion failure
    - fallback: Tries OMML, falls back to text placeholder on error
    - image: Only image-based rendering (not implemented yet)

    Attributes:
        mode: Rendering mode ('native', 'fallback', or 'image').
        logger: Logger instance for error tracking.
    """

    def __init__(self, mode: Literal["native", "fallback", "image"] = "fallback") -> None:
        """Initialize the math renderer with specified mode.

        Args:
            mode: Rendering mode selection. Defaults to 'fallback'.
                'native' - Only OMML conversion, raises on error.
                'fallback' - OMML with text fallback on error.
                'image' - Image-based rendering (not implemented).

        Raises:
            ValueError: If mode is not one of 'native', 'fallback', or 'image'.
        """
        valid_modes = ["native", "fallback", "image"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {valid_modes}")

        self.mode = mode
        self.logger = logging.getLogger("typst_gost_docx")

        if mode == "image":
            self.logger.warning("Image mode is not implemented yet")

    def render(self, latex: str) -> str:
        """Render LaTeX math to OMML string or fallback text.

        Converts LaTeX mathematical expressions to Office Math Markup Language (OMML)
        format. Handles conversion errors according to the configured mode.

        Args:
            latex: LaTeX math expression string.

        Returns:
            OMML XML string or fallback text representation.

        Raises:
            ValueError: If latex is empty string.
            RuntimeError: In 'native' mode when conversion fails.

        Example:
            >>> renderer = MathRenderer(mode="fallback")
            >>> omml = renderer.render("E = mc^2")
        """
        if not latex or not latex.strip():
            raise ValueError("LaTeX expression cannot be empty")

        try:
            from latex2mathml import converter

            omml = converter.convert(latex)

            # Verify the result is valid
            if not omml or len(omml.strip()) == 0:
                raise RuntimeError("Conversion produced empty result")

            self.logger.debug(f"Successfully rendered LaTeX: {latex[:50]}...")
            return omml

        except Exception as e:
            self.logger.warning(f"Failed to render LaTeX to OMML: {latex[:50]}... Error: {e}")

            if self.mode == "native":
                raise RuntimeError(
                    f"Failed to render LaTeX in native mode: {e}"
                ) from e

            # Fallback mode: return text placeholder
            return self._create_fallback(latex)

    def render_to_element(self, latex: str) -> Element:
        """Render LaTeX math to lxml Element with OMML or fallback.

        This method provides a convenient way to get an lxml Element that can be
        directly inserted into DOCX documents via the element tree.

        Args:
            latex: LaTeX math expression string.

        Returns:
            lxml Element containing OMML or fallback text.

        Raises:
            ValueError: If latex is empty string.
            RuntimeError: In 'native' mode when conversion fails.

        Example:
            >>> renderer = MathRenderer(mode="fallback")
            >>> element = renderer.render_to_element("\\frac{a}{b}")
        """
        if not latex or not latex.strip():
            raise ValueError("LaTeX expression cannot be empty")

        try:
            from latex2mathml import converter

            omml = converter.convert(latex)

            # Parse the OMML string into an Element
            from lxml import etree  # type: ignore[import-untyped]

            element = etree.fromstring(omml.encode("utf-8"))

            self.logger.debug(f"Successfully rendered LaTeX to element: {latex[:50]}...")
            return element

        except Exception as e:
            self.logger.warning(
                f"Failed to render LaTeX to element: {latex[:50]}... Error: {e}"
            )

            if self.mode == "native":
                raise RuntimeError(
                    f"Failed to render LaTeX to element in native mode: {e}"
                ) from e

            # Fallback mode: create text element
            return self._create_fallback_element(latex)

    def _create_fallback(self, latex: str) -> str:
        """Create fallback text representation for failed conversions.

        Args:
            latex: Original LaTeX expression.

        Returns:
            Fallback text string.
        """
        # Truncate very long LaTeX for readability
        display_latex = latex[:100] + "..." if len(latex) > 100 else latex
        return f"[FORMULA: {display_latex}]"

    def _create_fallback_element(self, latex: str) -> Element:
        """Create fallback lxml Element for failed conversions.

        Creates a minimal valid OMML structure with text content that can be
        inserted into a document when OMML conversion fails.

        Args:
            latex: Original LaTeX expression.

        Returns:
            lxml Element containing fallback text.
        """
        from lxml import etree

        # Truncate very long LaTeX for readability
        display_latex = latex[:100] + "..." if len(latex) > 100 else latex
        fallback_text = f"[FORMULA: {display_latex}]"

        # Create a minimal valid OMML structure
        element = etree.Element(
            "m:oMathPara",
            nsmap={
                "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"
            },
        )
        elem = etree.SubElement(element, "m:oMath")
        r = etree.SubElement(elem, "m:r")
        t = etree.SubElement(r, "m:t")
        t.text = fallback_text

        return element
