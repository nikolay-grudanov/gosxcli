"""Typst query parser - uses typst query as primary extraction mechanism.

This module provides the TypstQueryParser class which executes typst query
commands via subprocess to extract document structure (headings, figures, etc.)
and converts the results to IR nodes.

Typical usage:
    parser = TypstQueryParser("document.typ")
    doc = parser.extract()
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional, cast

import uuid

from ..ir.model import (
    Caption,
    Document,
    Equation,
    Figure,
    NodeType,
    NumberingKind,
    Section,
    SourceLocation,
    TableCellNode,
    TableHeaderNode,
    TableNode,
    TextRun,
)

logger = logging.getLogger(__name__)

# Selectors supported by typst query
HEADING_SELECTOR = "heading"
FIGURE_SELECTOR = "figure"
TABLE_SELECTOR = "table"
EQ_SELECTOR = "equation"


class TypstQueryParser:
    """Parser using typst query as primary mechanism.

    This parser executes typst query commands to extract document structure
    and converts the JSON output to IR nodes.

    Attributes:
        file_path: Path to the Typst source file.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self._has_typst = shutil.which("typst") is not None

    def extract(self) -> Document:
        """Extract complete document structure using typst query.

        Executes query commands for each supported selector and builds
        the IR document from the results.

        Returns:
            IR Document with all extracted elements.
        """
        doc = Document(id=str(uuid.uuid4()))

        if not self._has_typst:
            logger.warning("typst binary not available, using empty document")
            return doc

        # Extract headings (most reliable selector)
        headings = self.extract_headings()
        for heading in headings:
            doc.blocks.append(heading)

        # Extract figures
        figures = self.extract_figures()
        for figure in figures:
            doc.blocks.append(figure)

        # Extract tables
        tables = self.extract_tables()
        for table in tables:
            doc.blocks.append(table)

        # Extract equations
        equations = self.extract_equations()
        for eq in equations:
            doc.blocks.append(eq)

        return doc

    def extract_headings(self) -> list[Section]:
        """Extract headings using typst query heading selector.

        Returns:
            List of IR Section nodes.
        """
        if not self._has_typst:
            return []

        result = self._query(HEADING_SELECTOR)
        if not result:
            return []

        sections = []
        for i, item in enumerate(result):
            section = self._parse_heading(item, i)
            if section:
                sections.append(section)

        return sections

    def extract_figures(self) -> list[Figure]:
        """Extract figures using typst query figure selector.

        Returns:
            List of IR Figure nodes.
        """
        if not self._has_typst:
            return []

        result = self._query(FIGURE_SELECTOR)
        if not result:
            return []

        figures = []
        for item in result:
            figure = self._parse_figure(item)
            if figure:
                figures.append(figure)

        return figures

    def extract_tables(self) -> list[TableNode]:
        """Extract tables using typst query table selector.

        Returns:
            List of IR TableNode nodes.
        """
        if not self._has_typst:
            return []

        result = self._query(TABLE_SELECTOR)
        if not result:
            return []

        tables = []
        for item in result:
            table = self._parse_table(item)
            if table:
                tables.append(table)

        return tables

    def extract_equations(self) -> list[Equation]:
        """Extract equations using typst query equation selector.

        Returns:
            List of IR Equation nodes.
        """
        if not self._has_typst:
            return []

        result = self._query(EQ_SELECTOR)
        if not result:
            return []

        equations = []
        for item in result:
            equation = self._parse_equation(item)
            if equation:
                equations.append(equation)

        return equations

    def _query(self, selector: str) -> list[dict[str, object]]:
        """Execute typst query for a selector.

        Args:
            selector: The typst query selector (e.g., 'heading', 'figure').

        Returns:
            List of JSON objects from typst query, or empty list on error.
        """
        try:
            proc = subprocess.run(
                ["typst", "query", str(self.file_path), selector, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if proc.returncode != 0:
                logger.debug(f"Query '{selector}' failed: {proc.stderr}")
                return []

            try:
                result = json.loads(proc.stdout)
                return result if isinstance(result, list) else [result]
            except json.JSONDecodeError as e:
                logger.debug(f"Failed to parse JSON from query '{selector}': {e}")
                return []

        except subprocess.TimeoutExpired:
            logger.warning(f"Query '{selector}' timeout")
            return []
        except Exception as e:
            logger.debug(f"Query '{selector}' error: {e}")
            return []

    def _parse_heading(self, data: dict[str, object], index: int) -> Optional[Section]:
        """Parse heading data from typst query to IR Section.

        Args:
            data: JSON data from typst query.
            index: Heading index for ID generation.

        Returns:
            IR Section node, or None if parsing fails.
        """
        try:
            body = data.get("body", {})
            body_dict = cast(dict[str, Any], body)
            text = body_dict.get("text", "") if isinstance(body, dict) else str(body)

            level = cast(int, data.get("level", 1))
            line = cast(int, data.get("offset", 0)) + 1

            section = Section(
                id=str(uuid.uuid4()),
                level=level,
                source_location=SourceLocation(
                    file_path=str(self.file_path),
                    line=line,
                ),
                numbering_kind=NumberingKind.SECTION,
            )

            section.title = [
                TextRun(
                    node_type=NodeType.TEXT_RUN,
                    id=str(uuid.uuid4()),
                    text=text,
                )
            ]

            return section

        except Exception as e:
            logger.debug(f"Failed to parse heading: {e}")
            return None

    def _parse_figure(self, data: dict[str, object]) -> Optional[Figure]:
        """Parse figure data from typst query to IR Figure.

        Args:
            data: JSON data from typst query.

        Returns:
            IR Figure node, or None if parsing fails.
        """
        try:
            caption_data = data.get("caption", {})
            caption_dict = cast(dict[str, Any], caption_data)
            caption_text = (
                caption_dict.get("text", "")
                if isinstance(caption_data, dict)
                else ""
            )

            line = cast(int, data.get("offset", 0)) + 1

            figure = Figure(
                id=str(uuid.uuid4()),
                source_location=SourceLocation(
                    file_path=str(self.file_path),
                    line=line,
                ),
                numbering_kind=NumberingKind.FIGURE,
            )

            if caption_text:
                figure.caption = Caption(
                    id=str(uuid.uuid4()),
                    text=caption_text,
                    numbering_kind=NumberingKind.FIGURE,
                )

            return figure

        except Exception as e:
            logger.debug(f"Failed to parse figure: {e}")
            return None

    def _parse_table(self, data: dict[str, object]) -> Optional[TableNode]:
        """Parse table data from typst query to IR TableNode.

        Args:
            data: JSON data from typst query.

        Returns:
            IR TableNode, or None if parsing fails.
        """
        try:
            line = cast(int, data.get("offset", 0)) + 1

            table = TableNode(
                id=str(uuid.uuid4()),
                source_location=SourceLocation(
                    file_path=str(self.file_path),
                    line=line,
                ),
                numbering_kind=NumberingKind.TABLE,
            )

            # Extract header if present
            header_data = data.get("header", [])
            header_list = cast(list[object], header_data)
            if header_list and isinstance(header_list, list):
                cells = []
                for cell_obj in header_list:
                    cell_text = cast(dict[str, Any], cell_obj)
                    text = cell_text.get("text", "") if isinstance(cell_obj, dict) else str(cell_obj)
                    cells.append(
                        TableCellNode(
                            id=str(uuid.uuid4()),
                            content=[
                                TextRun(
                                    node_type=NodeType.TEXT_RUN,
                                    id=str(uuid.uuid4()),
                                    text=text,
                                )
                            ],
                        )
                    )
                table.header = TableHeaderNode(
                    id=str(uuid.uuid4()),
                    cells=cells,
                )
                table.has_header = True

            # Extract rows
            rows_data = data.get("rows", [])
            rows_list = cast(list[object], rows_data)
            if rows_list and isinstance(rows_list, list):
                for row_obj in rows_list:
                    row_data = cast(list[object], row_obj)
                    row_cells = []
                    for cell_obj in row_data:
                        text = cell_text.get("text", "") if isinstance(cell_text, dict) else str(cell_text)
                        row_cells.append(
                            TableCellNode(
                                id=str(uuid.uuid4()),
                                content=[
                                    TextRun(
                                        node_type=NodeType.TEXT_RUN,
                                        id=str(uuid.uuid4()),
                                        text=text,
                                    )
                                ],
                            )
                        )
                    table.rows.append(row_cells)

            return table

        except Exception as e:
            logger.debug(f"Failed to parse table: {e}")
            return None

    def _parse_equation(self, data: dict[str, object]) -> Optional[Equation]:
        """Parse equation data from typst query to IR Equation.

        Args:
            data: JSON data from typst query.

        Returns:
            IR Equation node, or None if parsing fails.
        """
        try:
            body = data.get("body", {})
            body_dict = cast(dict[str, Any], body)
            latex = body_dict.get("text", "") if isinstance(body, dict) else str(body)

            line = cast(int, data.get("offset", 0)) + 1

            equation = Equation(
                id=str(uuid.uuid4()),
                source_location=SourceLocation(
                    file_path=str(self.file_path),
                    line=line,
                ),
                latex=latex,
                numbering_kind=NumberingKind.EQUATION,
            )

            return equation

        except Exception as e:
            logger.debug(f"Failed to parse equation: {e}")
            return None


__all__ = ["TypstQueryParser"]