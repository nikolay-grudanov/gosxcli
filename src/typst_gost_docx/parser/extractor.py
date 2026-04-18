"""Extract document structure into IR."""

import re
import uuid
from typing import Optional
from ..ir.model import (
    Document,
    Section,
    Paragraph,
    TextRun,
    ListBlock,
    ListItem,
    Figure,
    Caption,
    Table,
    TableRow,
    TableCell,
    Equation,
    CrossReference,
    BaseNode,
    SourceLocation,
    NumberingKind,
    ListKind,
    NodeType,
)
from .scanner import TypstScanner


class TypstExtractor:
    def __init__(self, scanner: TypstScanner, file_path: str):
        self.scanner = scanner
        self.file_path = file_path
        self.tokens = list(scanner.scan())
        self.pos = 0

    def extract(self) -> Document:
        doc = Document(id=str(uuid.uuid4()))
        blocks = []

        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token.type == "HEADING":
                section = self._extract_section()
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
            elif token.type == "NEWLINE":
                self.pos += 1
            else:
                paragraph = self._extract_paragraph()
                if paragraph:
                    blocks.append(paragraph)

        doc.blocks = blocks
        return doc

    def _extract_section(self) -> Optional[Section]:
        token = self.tokens[self.pos]
        level = len(token.value.strip())

        self.pos += 1
        title_text = self._get_text_until_newline()

        section = Section(
            id=str(uuid.uuid4()),
            level=level,
            source_location=SourceLocation(self.file_path, token.line, token.column),
        )
        section.title = [
            TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=title_text)
        ]

        return section

    def _extract_paragraph(self) -> Optional[Paragraph]:
        token = self.tokens[self.pos]
        text = self._get_text_until_newline()

        if not text.strip():
            return None

        paragraph = Paragraph(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(self.file_path, token.line, token.column),
        )
        paragraph.content = self._parse_inline_content(text)

        return paragraph

    def _parse_inline_content(self, text: str) -> list[BaseNode]:
        nodes: list[BaseNode] = []
        pattern = r"@(fig|tbl|eq)-([a-zA-Z0-9_-]+)"

        last_end = 0
        for match in re.finditer(pattern, text):
            if match.start() > last_end:
                plain_text = text[last_end : match.start()]
                nodes.append(
                    TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=plain_text)
                )

            label = match.group(0)
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

    def _extract_list(self) -> Optional[ListBlock]:
        token = self.tokens[self.pos]
        kind = ListKind.BULLET if token.type == "BULLET" else ListKind.NUMBERED

        list_block = ListBlock(
            id=str(uuid.uuid4()),
            kind=kind,
            source_location=SourceLocation(self.file_path, token.line, token.column),
        )

        while self.pos < len(self.tokens):
            current_token = self.tokens[self.pos]
            if current_token.type == "BULLET" or current_token.type == "NUMBERED":
                self.pos += 1
                text = self._get_text_until_newline()
                content: list[BaseNode] = [
                    TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=text)
                ]
                item = ListItem(
                    id=str(uuid.uuid4()),
                    content=content,
                )
                list_block.items.append(item)
            elif current_token.type == "TEXT" or current_token.type == "NEWLINE":
                self.pos += 1
            else:
                break

        return list_block

    def _extract_figure(self) -> Optional[Figure]:
        token = self.tokens[self.pos]
        self.pos += 1

        content = self._extract_until_closing_paren()
        image_path = self._extract_image_path(content)
        caption_text = self._extract_caption_text(content)

        figure = Figure(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(self.file_path, token.line, token.column),
            image_path=image_path,
        )

        if caption_text:
            figure.caption = Caption(
                id=str(uuid.uuid4()),
                text=caption_text,
                numbering_kind=NumberingKind.FIGURE,
            )

        return figure

    def _extract_table(self) -> Optional[Table]:
        token = self.tokens[self.pos]
        self.pos += 1

        content = self._extract_until_closing_paren()

        table = Table(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(self.file_path, token.line, token.column),
        )

        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "table.header(" in line:
                cells = self._extract_header_cells(line)
                if cells:
                    row = TableRow(id=str(uuid.uuid4()))
                    row.cells.extend(cells)
                    table.rows.append(row)
                    table.has_header = True
            elif line.startswith("["):
                cells = self._extract_row_cells(line)
                if cells:
                    row = TableRow(id=str(uuid.uuid4()))
                    row.cells.extend(cells)
                    table.rows.append(row)

        return table

    def _extract_header_cells(self, line: str) -> list[TableCell]:
        cells: list[TableCell] = []
        content = line[line.find("table.header(") + len("table.header(") :]
        content = content.rstrip(")").strip()

        while content.startswith("["):
            end_bracket = content.find("]")
            if end_bracket == -1:
                break

            cell_text = content[1:end_bracket].strip()
            cell_content: list[BaseNode] = [
                TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=cell_text)
            ]
            cell = TableCell(
                id=str(uuid.uuid4()),
                content=cell_content,
            )
            cells.append(cell)

            content = content[end_bracket + 1 :].strip()

        return cells

    def _extract_row_cells(self, line: str) -> list[TableCell]:
        cells: list[TableCell] = []
        content = line.strip()

        while content.startswith("["):
            end_bracket = content.find("]")
            if end_bracket == -1:
                break

            cell_text = content[1:end_bracket].strip()
            cell_content: list[BaseNode] = [
                TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=cell_text)
            ]
            cell = TableCell(
                id=str(uuid.uuid4()),
                content=cell_content,
            )
            cells.append(cell)

            content = content[end_bracket + 1 :].strip()

        return cells

    def _extract_equation(self) -> Optional[Equation]:
        token = self.tokens[self.pos]
        self.pos += 1

        latex = self._extract_until_block_math()

        equation = Equation(
            id=str(uuid.uuid4()),
            source_location=SourceLocation(self.file_path, token.line, token.column),
            latex=latex,
            numbering_kind=NumberingKind.EQUATION,
        )

        return equation

    def _get_text_until_newline(self) -> str:
        text = ""
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.type == "NEWLINE":
                break
            text += token.value
            self.pos += 1
        return text

    def _extract_until_closing_paren(self) -> str:
        content = ""
        paren_level = 1
        start_pos = self.pos

        while self.pos < len(self.tokens) and paren_level > 0:
            token = self.tokens[self.pos]
            if token.value == "(":
                paren_level += 1
            elif token.value == ")":
                paren_level -= 1
            if paren_level > 0:
                content += token.value
            self.pos += 1

        return content

    def _extract_until_block_math(self) -> str:
        latex = ""
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.type == "BLOCK_MATH_DELIM":
                self.pos += 1
                break
            latex += token.value
            self.pos += 1
        return latex

    def _extract_image_path(self, content: str) -> Optional[str]:
        match = re.search(r'image\s*\(\s*"([^"]+)"', content)
        return match.group(1) if match else None

    def _extract_caption_text(self, content: str) -> Optional[str]:
        match = re.search(r"caption\s*:\s*\[([^]]+)\]", content)
        return match.group(1) if match else None
