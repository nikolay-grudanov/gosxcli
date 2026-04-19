"""State-machine based Typst extractor."""

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
    Equation,
    CrossReference,
    NodeType,
    NumberingKind,
    ListKind,
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

    def extract(self) -> Document:
        """Extract document structure from tokens.

        Returns:
            IR Document
        """
        doc = Document(id=str(uuid.uuid4()))
        blocks = []

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
            elif token.type == "BLOCK_MATH_DELIM":
                equation = self._extract_equation()
                if equation:
                    blocks.append(equation)
            elif token.type == "LABEL":
                self._process_label()
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
            source_location=SourceLocation(file_path=self.file_path, line=token.line, column=token.column),
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
            source_location=SourceLocation(file_path=self.file_path, line=token.line, column=token.column),
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
            source_location=SourceLocation(file_path=self.file_path, line=token.line, column=token.column),
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
            source_location=SourceLocation(file_path=self.file_path, line=token.line, column=token.column),
        )

        image_path = self._extract_image_path(content)
        caption_text = self._extract_caption_text(content)

        if image_path:
            figure.image_path = image_path

        if caption_text:
            figure.caption = Caption(
                id=str(uuid.uuid4()),
                text=caption_text,
                numbering_kind=NumberingKind.FIGURE,
            )

        if self.current_label:
            figure.label = self.current_label
            self.current_label = None

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
            source_location=SourceLocation(file_path=self.file_path, line=token.line, column=token.column),
        )

        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "table.header(" in line:
                header_cells = self._extract_header_cells(line)
                if header_cells:
                    table.header = TableHeaderNode(
                        id=str(uuid.uuid4()),
                        cells=header_cells,
                    )
                    table.has_header = True
            elif line.startswith("["):
                row_cells = self._extract_row_cells(line)
                if row_cells:
                    table.rows.append(row_cells)

        if self.current_label:
            table.label = self.current_label
            self.current_label = None

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
            source_location=SourceLocation(file_path=self.file_path, line=token.line, column=token.column),
            latex=latex,
            numbering_kind=NumberingKind.EQUATION,
        )

        if self.current_label:
            equation.label = self.current_label
            self.current_label = None

        return equation

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

    def _extract_header_cells(self, line: str) -> list[TableCellNode]:
        """Extract header cells from table header line.

        Args:
            line: Table header line

        Returns:
            List of IR TableCellNode
        """
        cells: list[TableCellNode] = []
        content = line[line.find("table.header(") + len("table.header(") :]
        content = content.rstrip(")").strip()

        while content.startswith("["):
            end_bracket = content.find("]")
            if end_bracket == -1:
                break

            cell_text = content[1:end_bracket].strip()
            cell_content: list[InlineNode] = [
                TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=cell_text)
            ]
            cell = TableCellNode(
                id=str(uuid.uuid4()),
                content=cell_content,
            )
            cells.append(cell)

            content = content[end_bracket + 1 :].strip()

        return cells

    def _extract_row_cells(self, line: str) -> list[TableCellNode]:
        """Extract cells from table row line.

        Args:
            line: Table row line

        Returns:
            List of IR TableCellNode
        """
        cells: list[TableCellNode] = []
        content = line.strip()

        while content.startswith("["):
            end_bracket = content.find("]")
            if end_bracket == -1:
                break

            cell_text = content[1:end_bracket].strip()
            cell_content: list[InlineNode] = [
                TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=cell_text)
            ]
            cell = TableCellNode(
                id=str(uuid.uuid4()),
                content=cell_content,
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
