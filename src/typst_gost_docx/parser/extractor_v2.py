"""State-machine based Typst extractor."""

import logging
import uuid
from typing import Optional, List, Any
from enum import Enum, auto

from ..ir.model import (
    Document,
    Section,
    Paragraph,
    TextRun,
    InlineRunNode,
    InlineCodeNode,
    InlineNode,
    ListBlock,
    ListItem,
    Figure,
    Caption,
    TableNode,
    TableHeaderNode,
    TableCellNode,
    ColSpec,
    Equation,
    CrossReference,
    TOCNode,
    CitationNode,
    BibliographySection,
    CodeBlockNode,
    NodeType,
    NumberingKind,
    ListKind,
    CitationStyle,
    SourceLocation,
)
from .scanner import TypstScanner


class ParserState(Enum):
    """Parser state machine states."""

    DOCUMENT = auto()
    HEADING = auto()
    PARAGRAPH = auto()
    LIST = auto()
    FIGURE = auto()
    TABLE = auto()
    EQUATION = auto()
    LABEL = auto()


class TypstExtractorV2:
    """State-machine based Typst extractor."""

    def __init__(self, text: str, file_path: str):
        self.text = text
        self.file_path = file_path
        self.scanner = TypstScanner(text)
        self.tokens = list(self.scanner.scan())
        self.pos = 0

        self.state = ParserState.DOCUMENT
        self.paren_stack: List[int] = []
        self.bracket_stack: List[int] = []
        self.current_label: Optional[str] = None

        # Citation tracking
        self._citation_keys: dict[str, int] = {}  # key -> number
        self._citation_order: list[str] = []  # keys in order of first appearance

        # Logger for warnings
        self.logger = logging.getLogger("typst_gost_docx")

    def extract(self) -> Document:
        """Extract document structure from tokens.

        Returns:
            IR Document
        """
        from ..ir.model import IRNode

        doc = Document(id=str(uuid.uuid4()))
        blocks: list[IRNode] = []

        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token.type == "HEADING":
                section = self._extract_heading()
                if section:
                    blocks.append(section)
            elif token.type == "BULLET" or token.type == "NUMBERED":
                list_block = self._extract_list()
                if list_block:
                    blocks.append(list_block)
            elif token.type == "FIGURE_START":
                figure = self._extract_figure()
                if figure:
                    blocks.append(figure)
            elif token.type == "TABLE_START":
                table = self._extract_table()
                if table:
                    blocks.append(table)
            elif token.type == "OUTLINE_START":
                outline = self._extract_outline()
                if outline:
                    blocks.append(outline)
            elif token.type == "BIBLIOGRAPHY_START":
                bibliography = self._extract_bibliography()
                if bibliography:
                    blocks.append(bibliography)
            elif token.type == "BLOCK_MATH_DELIM":
                equation = self._extract_equation()
                if equation:
                    blocks.append(equation)
            elif token.type == "CODE_BLOCK_DELIM":
                code_block = self._extract_code_block()
                if code_block:
                    blocks.append(code_block)
            elif token.type == "LABEL":
                self._process_label()
            elif token.type == "CITATION":
                self._extract_citation()
            elif token.type == "REF_INLINE":
                ref = self._extract_ref()
                if ref:
                    pass
            elif token.type == "NEWLINE":
                self.pos += 1
            else:
                paragraph = self._extract_paragraph()
                if paragraph:
                    blocks.append(paragraph)

        doc.blocks = blocks
        return doc

    def _extract_heading(self) -> Optional[Section]:
        """Extract heading from tokens.

        Returns:
            IR Section or None
        """
        token = self.tokens[self.pos]
        level = len(token.value.strip())

        self.pos += 1
        title_text = self._get_text_until_newline()

        section = Section(
            id=str(uuid.uuid4()),
            level=level,
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
            numbering_kind=NumberingKind.SECTION,
        )

        section.title = [
            TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=title_text)
        ]

        if self.current_label:
            section.label = self.current_label
            self.current_label = None

        return section

    def _extract_paragraph(self) -> Optional[Paragraph]:
        """Extract paragraph from tokens.

        Returns:
            IR Paragraph or None
        """
        token = self.tokens[self.pos]
        runs = self._extract_paragraph_content()

        if not runs:
            return None

        paragraph = Paragraph(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
            runs=runs,
        )

        if self.current_label:
            paragraph.label = self.current_label
            self.current_label = None

        return paragraph

    def _extract_paragraph_content(self) -> list[InlineNode]:
        """Extract paragraph content nodes with inline formatting.

        Returns:
            List of IR nodes (TextRun, InlineRunNode, InlineCodeNode, etc.)
        """
        nodes: list[InlineNode] = []
        current_text = ""

        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token.type == "NEWLINE":
                self.pos += 1
                break
            elif token.type == "CITATION":
                if current_text.strip():
                    nodes.extend(self._parse_inline_formatting(current_text))
                    current_text = ""

                citation = self._extract_citation()
                if citation:
                    nodes.append(citation)
            elif token.type == "REF":
                if current_text.strip():
                    nodes.extend(self._parse_inline_formatting(current_text))
                    current_text = ""

                ref = self._extract_ref()
                if ref:
                    nodes.append(ref)
            elif token.type == "LABEL":
                self._process_label()
            else:
                current_text += token.value
                self.pos += 1

        if current_text.strip():
            nodes.extend(self._parse_inline_formatting(current_text))

        return nodes

    def _extract_list(self) -> Optional[ListBlock]:
        """Extract list from tokens.

        Returns:
            IR ListBlock or None
        """
        token = self.tokens[self.pos]
        kind = ListKind.BULLET if token.type == "BULLET" else ListKind.NUMBERED

        list_block = ListBlock(
            id=str(uuid.uuid4()),
            kind=kind,
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
        )

        while self.pos < len(self.tokens):
            current_token = self.tokens[self.pos]
            if current_token.type == "BULLET" or current_token.type == "NUMBERED":
                self.pos += 1
                text = self._get_text_until_newline()

                # Skip NEWLINE tokens to reach next list item or end of list
                while self.pos < len(self.tokens) and self.tokens[self.pos].type == "NEWLINE":
                    self.pos += 1

                item = ListItem(
                    id=str(uuid.uuid4()),
                    content=[TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=text)],
                )
                list_block.items.append(item)
            else:
                break

        return list_block

    def _extract_figure(self) -> Optional[Figure]:
        """Extract figure from tokens.

        Returns:
            IR Figure or None
        """
        token = self.tokens[self.pos]
        self.pos += 1

        content = self._extract_until_matching_paren()

        # Skip the closing paren token (paren_level went to 0)
        self.pos += 1

        figure = Figure(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
        )

        image_path = self._extract_image_path(content)
        caption_text = self._extract_caption_text(content)

        # Check if figure contains a nested table
        nested_table = self._extract_nested_table_from_figure(content)

        if image_path:
            figure.image_path = image_path
        elif nested_table:
            # Figure contains a table instead of an image
            figure.table = nested_table

        if caption_text:
            figure.caption = Caption(
                id=str(uuid.uuid4()),
                text=caption_text,
                numbering_kind=NumberingKind.TABLE if nested_table else NumberingKind.FIGURE,
            )

        # Check for label immediately after figure
        # Labels can appear as <label> or be set via current_label
        if self.current_label:
            figure.label = self.current_label
            self.current_label = None
        elif self.pos < len(self.tokens) and self.tokens[self.pos].type == "LABEL":
            # Process label token that appears right after figure
            label_token = self.tokens[self.pos]
            label_match = label_token.value
            if label_match.startswith("<") and label_match.endswith(">"):
                label_name = label_match[1:-1].strip()
                figure.label = label_name
            self.pos += 1

        return figure

    def _extract_table(self) -> Optional[TableNode]:
        """Extract table from tokens.

        Returns:
            IR TableNode or None
        """
        token = self.tokens[self.pos]
        self.pos += 1

        content = self._extract_until_matching_paren()

        # Skip the closing paren token (paren_level went to 0)
        self.pos += 1

        table = TableNode(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
        )

        # Parse table attributes
        table.columns = self._parse_columns_spec(content)
        table.border_width = self._parse_stroke_spec(content)
        fill_lambda = self._parse_fill_lambda(content)
        align_lambda = self._parse_align_lambda(content)

        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "table.header(" in line:
                header_cells = self._extract_header_cells(line, fill_lambda, align_lambda)
                if header_cells:
                    table.header = TableHeaderNode(
                        id=str(uuid.uuid4()),
                        cells=header_cells,
                    )
                    table.has_header = True
            elif line.startswith("[") or "table.cell(" in line:
                row_cells = self._extract_row_cells(line, fill_lambda, align_lambda)
                if row_cells:
                    table.rows.append(row_cells)

        # Check for label immediately after table
        # Labels can appear as <label> or be set via current_label
        if self.current_label:
            table.label = self.current_label
            self.current_label = None
        elif self.pos < len(self.tokens) and self.tokens[self.pos].type == "LABEL":
            # Process label token that appears right after table
            label_token = self.tokens[self.pos]
            label_match = label_token.value
            if label_match.startswith("<") and label_match.endswith(">"):
                label_name = label_match[1:-1].strip()
                table.label = label_name
            self.pos += 1

        return table

    def _extract_nested_table_from_figure(self, content: str) -> Optional[TableNode]:
        """Extract nested table from figure content.

        Looks for `table(` pattern inside figure content and extracts it as TableNode.

        Args:
            content: Figure content string (inside #figure(...))

        Returns:
            IR TableNode or None if no table found
        """
        import re

        # Look for table( pattern (with or without leading #)
        table_match = re.search(r"table\s*\(", content)
        if not table_match:
            return None

        # Extract table content from the opening table( to matching closing paren
        table_start = table_match.start()
        paren_count = 0
        in_table = False
        table_content = ""

        i = table_start
        while i < len(content):
            char = content[i]

            if char == "(":
                if not in_table:
                    in_table = True
                paren_count += 1
            elif char == ")":
                paren_count -= 1
                if in_table and paren_count == 0:
                    # Found the matching closing paren
                    break

            if in_table:
                table_content += char

            i += 1

        if not table_content:
            return None

        # Now parse the table content (similar to _extract_table logic)
        table = TableNode(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(
                file_path=self.file_path,
                line=self.tokens[self.pos - 1].line if self.pos > 0 else 0,
                column=0,
            ),
        )

        # Parse table attributes
        table.columns = self._parse_columns_spec(table_content)
        table.border_width = self._parse_stroke_spec(table_content)
        fill_lambda = self._parse_fill_lambda(table_content)
        align_lambda = self._parse_align_lambda(table_content)

        lines = table_content.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "table.header(" in line:
                header_cells = self._extract_header_cells(line, fill_lambda, align_lambda)
                if header_cells:
                    table.header = TableHeaderNode(
                        id=str(uuid.uuid4()),
                        cells=header_cells,
                    )
                    table.has_header = True
            elif line.startswith("[") or "table.cell(" in line:
                row_cells = self._extract_row_cells(line, fill_lambda, align_lambda)
                if row_cells:
                    table.rows.append(row_cells)

        return table

    def _extract_equation(self) -> Optional[Equation]:
        """Extract equation from tokens.

        Returns:
            IR Equation or None
        """
        token = self.tokens[self.pos]
        self.pos += 1

        latex = self._get_text_until_block_math_end()

        equation = Equation(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
            latex=latex,
            numbering_kind=NumberingKind.EQUATION,
        )

        # Check for label immediately after equation
        # Labels can appear as <label> or be set via current_label
        if self.current_label:
            equation.label = self.current_label
            self.current_label = None
        elif self.pos < len(self.tokens) and self.tokens[self.pos].type == "LABEL":
            # Process label token that appears right after equation
            label_token = self.tokens[self.pos]
            label_match = label_token.value
            if label_match.startswith("<") and label_match.endswith(">"):
                label_name = label_match[1:-1].strip()
                equation.label = label_name
            self.pos += 1

        return equation

    def _extract_code_block(self) -> Optional[CodeBlockNode]:
        """Extract code block from tokens.

        Pattern: ```[language]\ncontent\n```

        Returns:
            IR CodeBlockNode or None
        """
        token = self.tokens[self.pos]
        delimiter_value = token.value

        # Extract language identifier from delimiter (e.g., "```python")
        # Pattern: ```language or ```
        language = None
        if delimiter_value.startswith("```"):
            lang_part = delimiter_value[3:].strip()
            if lang_part:
                language = lang_part

        # Move past the delimiter token
        self.pos += 1

        # Collect content until the closing delimiter
        content_lines = []

        while self.pos < len(self.tokens):
            current_token = self.tokens[self.pos]

            if current_token.type == "CODE_BLOCK_DELIM":
                # Found closing delimiter
                self.pos += 1
                break

            # Add token value to content
            content_lines.append(current_token.value)
            self.pos += 1

        # Join content lines
        content = "".join(content_lines)

        # Create CodeBlockNode
        code_block = CodeBlockNode(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
            content=content,
            language=language,
        )

        return code_block

    def _extract_outline(self) -> Optional[TOCNode]:
        """Extract outline (table of contents) from tokens.

        Returns:
            IR TOCNode or None
        """
        token = self.tokens[self.pos]
        self.pos += 1

        # Extract content until matching closing paren
        content = self._extract_until_matching_paren()

        # Skip the closing paren token (paren_level went to 0)
        self.pos += 1

        # Parse title from content if provided
        title = "Содержание"  # Default title

        # Check for title: "..." parameter
        import re

        title_match = re.search(r'title\s*:\s*"([^"]+)"', content)
        if title_match:
            title = title_match.group(1)

        toc_node = TOCNode(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
            title=title,
        )

        return toc_node

    def _extract_bibliography(self) -> Optional[BibliographySection]:
        """Extract bibliography section from #bibliography() command.

        Parses #bibliography("file.bib") and loads the BibTeX file.

        Returns:
            IR BibliographySection or None
        """
        token = self.tokens[self.pos]
        token_value = token.value

        # Extract path from token value like #bibliography("refs.bib")
        import re

        bib_path_match = re.search(r'"([^"]+\.bib)"', token_value)
        if not bib_path_match:
            self.logger.warning("No .bib file path found in #bibliography()")
            self.pos += 1
            return None

        bib_file_path = bib_path_match.group(1)

        # Skip past the token
        self.pos += 1

        # Resolve relative path from project root
        from pathlib import Path

        bib_path = Path(self.file_path).parent / bib_file_path

        # Load and parse BibTeX file
        if not bib_path.exists():
            self.logger.warning(f"Bibliography file not found: {bib_path}")
            return None

        try:
            bib_content = bib_path.read_text(encoding="utf-8")
        except Exception as e:
            self.logger.warning(f"Failed to read bibliography file: {e}")
            return None

        # Parse bibliography
        from .bibliography import parse_bibliography

        bib_file = parse_bibliography(bib_content)

        if bib_file.parse_errors:
            for error in bib_file.parse_errors:
                self.logger.warning(f"BibTeX parse error: {error}")

        # Create BibliographySection with only the cited entries
        # Filter entries to only include those that were actually cited
        cited_entries = []
        for key in self._citation_order:
            if key in bib_file.entries:
                cited_entries.append(bib_file.entries[key])

        bib_section = BibliographySection(
            id=str(uuid.uuid4()),
            heading="Список литературы",
            entries=cited_entries,
            style=CitationStyle.NUMERIC,
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
        )

        return bib_section

    def _process_label(self) -> None:
        """Process label token."""
        token = self.tokens[self.pos]
        label_match = token.value

        if label_match.startswith("<") and label_match.endswith(">"):
            label_name = label_match[1:-1].strip()
            self.current_label = label_name

        self.pos += 1

    def _extract_ref(self) -> Optional[CrossReference]:
        """Extract reference from tokens.

        Returns:
            IR CrossReference or None
        """
        token = self.tokens[self.pos]
        ref_match = token.value

        if ref_match.startswith("@"):
            target_label = ref_match[1:].strip()

            ref = CrossReference(
                node_type=NodeType.CROSS_REFERENCE,
                id=str(uuid.uuid4()),
                target_label=target_label,
            )

            self.pos += 1
            return ref

        self.pos += 1
        return None

    def _extract_citation(self) -> Optional[CitationNode]:
        """Extract citation from tokens.

        Parses @[key] pattern and assigns sequential citation numbers.

        Returns:
            IR CitationNode or None
        """
        token = self.tokens[self.pos]
        token_value = token.value

        # Extract key from @[key] pattern (including brackets)
        if token_value.startswith("@[") and token_value.endswith("]"):
            key = token_value[2:-1]
        else:
            self.pos += 1
            return None

        # Assign citation number (sequential, starting from 1)
        if key not in self._citation_keys:
            self._citation_keys[key] = len(self._citation_keys) + 1
            self._citation_order.append(key)

        citation_number = self._citation_keys[key]

        citation = CitationNode(
            node_type=NodeType.CITATION,
            id=str(uuid.uuid4()),
            key=key,
            number=citation_number,
            source_location=SourceLocation(
                file_path=self.file_path, line=token.line, column=token.column
            ),
        )

        self.pos += 1
        return citation

    def _parse_columns_spec(self, content: str) -> list[ColSpec]:
        """Parse columns specification from table content.

        Parses formats like:
        - columns: 2
        - columns: (1fr, 2fr)
        - columns: (17%, 83%)
        - columns: (auto, 1fr, 20%)

        Args:
            content: Table content string

        Returns:
            List of ColSpec objects with width/width_percent/align
        """
        import re

        columns: list[ColSpec] = []

        # Pattern: columns: (spec1, spec2, ...)
        match = re.search(r"columns:\s*\(([^)]+)\)", content)
        if not match:
            # Try simple format: columns: 2
            simple_match = re.search(r"columns:\s*(\d+)", content)
            if simple_match:
                num_cols = int(simple_match.group(1))
                return [ColSpec() for _ in range(num_cols)]
            return columns

        specs_str = match.group(1)
        specs = [s.strip() for s in specs_str.split(",")]

        for spec in specs:
            if not spec:
                continue

            col_spec = ColSpec()

            # Parse percentage: 17%
            pct_match = re.match(r"^([\d.]+)%$", spec)
            if pct_match:
                col_spec.width_percent = float(pct_match.group(1))
                columns.append(col_spec)
                continue

            # Parse fraction: 1fr
            fr_match = re.match(r"^([\d.]+)fr$", spec)
            if fr_match:
                # Store as width (normalized later by writer)
                col_spec.width = float(fr_match.group(1))
                columns.append(col_spec)
                continue

            # Parse auto or align keywords
            if spec == "auto":
                columns.append(col_spec)
            elif spec in ("left", "center", "right", "top", "bottom", "horizon"):
                col_spec.align = spec
                columns.append(col_spec)
            else:
                # Try combined: 1fr + center (simplified)
                parts = spec.split()
                if len(parts) >= 2:
                    if parts[0].endswith("fr"):
                        col_spec.width = float(parts[0].replace("fr", ""))
                    elif parts[0].endswith("%"):
                        col_spec.width_percent = float(parts[0].replace("%", ""))
                    if parts[1] in ("left", "center", "right"):
                        col_spec.align = parts[1]
                columns.append(col_spec)

        return columns

    def _parse_stroke_spec(self, content: str) -> float:
        """Parse stroke specification from table content.

        Parses formats like:
        - stroke: 0.7pt
        - stroke: 1pt

        Args:
            content: Table content string

        Returns:
            Border width in points
        """
        import re

        # Pattern: stroke: 0.7pt
        match = re.search(r"stroke:\s*([0-9.]+)(?:pt|mm)", content)
        if match:
            return float(match.group(1))
        return 0.0

    def _parse_fill_lambda(self, content: str) -> Optional[str]:
        """Parse fill lambda specification from table content.

        Parses formats like:
        - fill: (col, row) => if row == 0 { luma(220) }
        - fill: (col, row) => if row == 0 { rgb("#eee") }

        Args:
            content: Table content string

        Returns:
            Fill lambda expression string or None
        """
        import re

        # Pattern: fill: (col, row) => if row == 0 { ... }
        match = re.search(r"fill:\s*\(col,\s*row\)\s*=>\s*if\s+row\s*==\s*0\s*\{[^}]+\}", content)
        if match:
            return match.group(0)
        return None

    def _parse_align_lambda(self, content: str) -> Optional[str]:
        """Parse align lambda specification from table content.

        Parses formats like:
        - align: (col, row) => if row == 0 { center }
        - align: (col, row) => if row == 0 { center } else { left }

        Args:
            content: Table content string

        Returns:
            Align lambda expression string or None
        """
        import re

        # Pattern: align: (col, row) => if row == 0 { ... }
        match = re.search(
            r"align:\s*\(col,\s*row\)\s*=>\s*if\s+row\s*==\s*0\s*\{([^}]+)\}", content
        )
        if match:
            # Extract alignment value
            align_value = match.group(1).strip()
            return align_value
        return None

    def _extract_header_cells(
        self, line: str, fill_lambda: Optional[str] = None, align_lambda: Optional[str] = None
    ) -> list[TableCellNode]:
        """Extract header cells from table header line.

        Args:
            line: Table header line
            fill_lambda: Optional fill lambda expression from table
            align_lambda: Optional align lambda expression from table

        Returns:
            List of IR TableCellNode
        """
        cells: list[TableCellNode] = []
        content = line[line.find("table.header(") + len("table.header(") :]
        content = content.rstrip(")").strip()

        # Extract fill color from lambda if present
        fill_color = None
        if fill_lambda:
            import re

            fill_match = re.search(r"\{\s*(luma|rgb)\(([^)]+)\)", fill_lambda)
            if fill_match:
                fill_color = fill_match.group(2)

        col_index = 0

        while content.startswith("["):
            end_bracket = content.find("]")
            if end_bracket == -1:
                break

            cell_text = content[1:end_bracket].strip()
            from typing import cast
            from ..ir.model import IRNode

            cell_content: list[InlineNode] = [
                TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=cell_text)
            ]

            # Create cell with fill and align
            cell = TableCellNode(
                id=str(uuid.uuid4()),
                content=cast(list[IRNode], cell_content),
                fill=fill_color,
                align=align_lambda if col_index == 0 else None,  # Simplified: apply to first column
            )
            cells.append(cell)
            col_index += 1

            content = content[end_bracket + 1 :].strip()

        return cells

    def _extract_row_cells(
        self, line: str, fill_lambda: Optional[str] = None, align_lambda: Optional[str] = None
    ) -> list[TableCellNode]:
        """Extract cells from table row line.

        Supports table.cell(colspan: 2)[...] and table.cell(rowspan: 2)[...] patterns.

        Args:
            line: Table row line
            fill_lambda: Optional fill lambda expression from table
            align_lambda: Optional align lambda expression from table

        Returns:
            List of IR TableCellNode
        """
        cells: list[TableCellNode] = []
        content = line.strip()

        while content.startswith("[") or "table.cell(" in content:
            colspan = 1
            rowspan = 1

            # Check for table.cell(colspan: N) or table.cell(rowspan: N)
            import re

            colspan_match = re.search(r"table\.cell\(colspan:\s*(\d+)\)", content)
            rowspan_match = re.search(r"table\.cell\(rowspan:\s*(\d+)\)", content)

            if colspan_match:
                colspan = int(colspan_match.group(1))
                # Skip past table.cell(colspan: N)[
                content = content[colspan_match.end() :].strip()
            elif rowspan_match:
                rowspan = int(rowspan_match.group(1))
                # Skip past table.cell(rowspan: N)[
                content = content[rowspan_match.end() :].strip()

            # Extract cell content
            end_bracket = content.find("]")
            if end_bracket == -1:
                break

            cell_text = content[1:end_bracket].strip()
            from typing import cast
            from ..ir.model import IRNode

            cell_content: list[InlineNode] = [
                TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=cell_text)
            ]

            # Create cell with colspan/rowspan
            cell = TableCellNode(
                id=str(uuid.uuid4()),
                content=cast(list[IRNode], cell_content),
                colspan=colspan,
                rowspan=rowspan,
            )
            cells.append(cell)

            content = content[end_bracket + 1 :].strip()

        return cells

    def _parse_inline_content(self, text: str) -> List[Any]:
        """Parse inline content for references.

        Args:
            text: Text content

        Returns:
            List of IR nodes
        """
        import re

        nodes: List[Any] = []
        pattern = r"@(fig|tbl|eq)-([a-zA-Z0-9_-]+)"

        last_end = 0
        for match in re.finditer(pattern, text):
            if match.start() > last_end:
                plain_text = text[last_end : match.start()]
                nodes.append(
                    TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=plain_text)
                )

            target_label = match.group(0)
            nodes.append(
                CrossReference(
                    node_type=NodeType.CROSS_REFERENCE,
                    id=str(uuid.uuid4()),
                    target_label=target_label,
                )
            )

            last_end = match.end()

        if last_end < len(text):
            plain_text = text[last_end:]
            nodes.append(
                TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=plain_text)
            )

        if not nodes:
            nodes = [TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=text)]

        return nodes

    def _parse_inline_formatting(self, text: str) -> list[InlineNode]:
        """Parse inline formatting from text.

        Supports:
        - *text* → bold
        - _text_ → italic
        - `code` → inline code

        Args:
            text: Text content to parse

        Returns:
            List of IR nodes with proper formatting
        """
        import re

        nodes: list[InlineNode] = []

        # Pattern for bold (*text*), italic (_text_), and code (`code`)
        pattern = r"(\*([^*]+)\*)|(_([^_]+)_)|(`([^`]+)`)"

        last_end = 0
        for match in re.finditer(pattern, text):
            # Add plain text before the match
            if match.start() > last_end:
                plain_text = text[last_end : match.start()]
                if plain_text:
                    nodes.append(
                        TextRun(
                            node_type=NodeType.TEXT_RUN,
                            id=str(uuid.uuid4()),
                            text=plain_text,
                        )
                    )

            # Determine the formatting type based on which group matched
            if match.group(1):  # bold: *text*
                nodes.append(
                    InlineRunNode(
                        node_type=NodeType.INLINE_RUN,
                        id=str(uuid.uuid4()),
                        text=match.group(2),
                        bold=True,
                    )
                )
            elif match.group(3):  # italic: _text_
                nodes.append(
                    InlineRunNode(
                        node_type=NodeType.INLINE_RUN,
                        id=str(uuid.uuid4()),
                        text=match.group(4),
                        italic=True,
                    )
                )
            elif match.group(5):  # code: `code`
                nodes.append(
                    InlineCodeNode(
                        node_type=NodeType.INLINE_CODE,
                        id=str(uuid.uuid4()),
                        code=match.group(6),
                    )
                )

            last_end = match.end()

        # Add remaining plain text after last match
        if last_end < len(text):
            remaining = text[last_end:]
            if remaining:
                nodes.append(
                    TextRun(
                        node_type=NodeType.TEXT_RUN,
                        id=str(uuid.uuid4()),
                        text=remaining,
                    )
                )

        # If no matches, return the whole text as plain text
        if not nodes and text:
            nodes.append(
                TextRun(
                    node_type=NodeType.TEXT_RUN,
                    id=str(uuid.uuid4()),
                    text=text,
                )
            )

        return nodes

    def _get_text_until_newline(self) -> str:
        """Get text until next newline token.

        Returns:
            Text content
        """
        text = ""
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.type == "NEWLINE":
                break
            text += token.value
            self.pos += 1
        return text

    def _get_text_until_block_math_end(self) -> str:
        """Get LaTeX content until block math end delimiter.

        Returns:
            LaTeX string
        """
        latex = ""
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.type == "BLOCK_MATH_DELIM":
                self.pos += 1
                break
            latex += token.value
            self.pos += 1
        return latex

    def _extract_until_matching_paren(self) -> str:
        """Extract content until matching closing parenthesis.

        Returns:
            Content string (excluding the final closing parenthesis).
        """
        content = ""
        paren_level = 1

        while self.pos < len(self.tokens) and paren_level > 0:
            token = self.tokens[self.pos]

            # Count parens in token value (not exact match)
            open_count = token.value.count("(")
            close_count = token.value.count(")")
            paren_level += open_count
            paren_level -= close_count

            if paren_level > 0:
                content += token.value
            else:
                # Don't include the closing paren(s) - find first ')' and truncate there
                first_close = token.value.find(")")
                if first_close >= 0:
                    content += token.value[:first_close]
                break

            self.pos += 1

        return content

    def _extract_image_path(self, content: str) -> Optional[str]:
        """Extract image path from figure content.

        Args:
            content: Figure content string

        Returns:
            Image path or None
        """
        import re

        match = re.search(r'image\s*\(\s*"([^"]+)"', content)
        return match.group(1) if match else None

    def _extract_caption_text(self, content: str) -> Optional[str]:
        """Extract caption text from figure content.

        Args:
            content: Figure content string

        Returns:
            Caption text or None
        """
        import re

        match = re.search(r"caption\s*:\s*\[([^]]+)\]", content)
        return match.group(1) if match else None
