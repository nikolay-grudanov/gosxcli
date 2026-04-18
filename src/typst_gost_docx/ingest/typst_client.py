"""Typst client using typst-py library."""

import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TypstClient:
    """Client for interacting with Typst compiler via typst-py."""

    def __init__(self):
        self._typst_available = self._check_typst_available()

    def _check_typst_available(self) -> bool:
        """Check if typst-py is available."""
        try:
            import typst

            return True
        except ImportError:
            logger.warning("typst-py not available, falling back to scanner-based parser")
            return False

    def is_available(self) -> bool:
        """Check if typst-py is available."""
        return self._typst_available

    def query_document_structure(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """Extract document structure using typst query.

        Args:
            input_path: Path to Typst file

        Returns:
            JSON structure or None if typst-py unavailable
        """
        if not self._typst_available:
            return None

        try:
            import typst

            result_json = typst.query(
                str(input_path),
                "<all>",
                field="value",
                one=True,
            )

            return json.loads(result_json)
        except Exception as e:
            logger.error(f"Error querying document structure: {e}")
            return None

    def compile_to_pdf(self, input_path: Path, output_path: Path) -> bool:
        """Compile Typst document to PDF.

        Args:
            input_path: Path to Typst file
            output_path: Path for output PDF

        Returns:
            True if successful
        """
        if not self._typst_available:
            return False

        try:
            import typst

            typst.compile(str(input_path), output=str(output_path))
            return True
        except Exception as e:
            logger.error(f"Error compiling to PDF: {e}")
            return False

    def query_labels(self, input_path: Path) -> Dict[str, Any]:
        """Extract all labels from document.

        Args:
            input_path: Path to Typst file

        Returns:
            Dict mapping labels to their locations/types
        """
        if not self._typst_available:
            return {}

        try:
            import typst

            result_json = typst.query(str(input_path), "<label>", field="value", one=False)

            if result_json:
                labels_data = json.loads(result_json)
                return {label.get("label", ""): label for label in labels_data}

            return {}
        except Exception as e:
            logger.error(f"Error querying labels: {e}")
            return {}

    def query_heading(self, input_path: Path) -> Optional[Dict[str, Any]]:
        """Extract heading structure.

        Args:
            input_path: Path to Typst file

        Returns:
            Heading structure or None
        """
        if not self._typst_available:
            return None

        try:
            import typst

            result_json = typst.query(
                str(input_path),
                "heading",
                field="value",
                one=False,
            )

            if result_json:
                return json.loads(result_json)

            return None
        except Exception as e:
            logger.error(f"Error querying headings: {e}")
            return None
