"""Convert Typst JSON structure to IR models."""

import uuid
from typing import Any, Dict, List, Optional
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
    NodeType,
    NumberingKind,
)


class TypstJsonToIRConverter:
    """Convert Typst JSON from typst query to IR."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def convert(self, typst_json: Dict[str, Any]) -> Document:
        """Convert Typst JSON to IR Document.

        Args:
            typst_json: JSON structure from typst query

        Returns:
            IR Document
        """
        doc = Document(id=str(uuid.uuid4()))
        blocks = []

        if typst_json.get("func") == "sequence":
            children = typst_json.get("children", [])
            for child in children:
                block = self._convert_node(child)
                if block:
                    blocks.append(block)
        else:
            block = self._convert_node(typst_json)
            if block:
                blocks.append(block)

        doc.blocks = blocks
        return doc

    def _convert_node(self, node: Dict[str, Any]) -> Optional[Any]:
        """Convert a single Typst node to IR node.

        Args:
            node: Typst JSON node

        Returns:
            IR node or None
        """
        func = node.get("func", "")

        if func == "heading":
            return self._convert_heading(node)
        elif func == "parbreak":
            return None
        elif func == "text":
            return self._convert_text(node)
        elif func == "sequence":
            return self._convert_sequence(node)
        elif func == "figure":
            return self._convert_figure(node)
        elif func == "table":
            return self._convert_table(node)
        elif func == "equation":
            return self._convert_equation(node)
        elif func == "ref":
            return self._convert_ref(node)
        elif func == "strong":
            return self._convert_strong(node)
        elif func == "emph":
            return self._convert_emph(node)
        else:
            return self._convert_generic(node)

    def _convert_heading(self, node: Dict[str, Any]) -> Section:
        """Convert heading to Section.

        Args:
            node: Typst heading node

        Returns:
            IR Section
        """
        depth = node.get("depth", 1)
        body = node.get("body", {})

        title_nodes = [self._convert_node(body)] if body else []

        section = Section(
            id=str(uuid.uuid4()),
            level=depth,
            title=title_nodes,
            numbering_kind=NumberingKind.SECTION,
        )

        return section

    def _convert_text(self, node: Dict[str, Any]) -> TextRun:
        """Convert text node to TextRun.

        Args:
            node: Typst text node

        Returns:
            IR TextRun
        """
        text = node.get("text", "")
        return TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=text)

    def _convert_sequence(self, node: Dict[str, Any]) -> Paragraph:
        """Convert sequence to Paragraph.

        Args:
            node: Typst sequence node

        Returns:
            IR Paragraph
        """
        children = node.get("children", [])
        content_nodes = []

        for child in children:
            ir_node = self._convert_node(child)
            if ir_node:
                content_nodes.append(ir_node)

        paragraph = Paragraph(id=str(uuid.uuid4()), content=content_nodes)
        return paragraph

    def _convert_figure(self, node: Dict[str, Any]) -> Optional[Figure]:
        """Convert figure to IR Figure.

        Args:
            node: Typst figure node

        Returns:
            IR Figure or None
        """
        children = node.get("children", [])
        caption_text = None
        image_path = None
        label = node.get("label", "")

        for child in children:
            if child.get("func") == "image":
                path = child.get("path", "")
                if path:
                    image_path = path
            elif child.get("func") == "caption":
                caption_text = self._extract_caption_text(child)

        figure = Figure(
            id=str(uuid.uuid4()),
            image_path=image_path,
            label=label if label else None,
        )

        if caption_text:
            figure.caption = Caption(
                id=str(uuid.uuid4()),
                text=caption_text,
                numbering_kind=NumberingKind.FIGURE,
            )

        return figure

    def _convert_table(self, node: Dict[str, Any]) -> Optional[Table]:
        """Convert table to IR Table.

        Args:
            node: Typst table node

        Returns:
            IR Table or None
        """
        children = node.get("children", [])
        table = Table(id=str(uuid.uuid4()))

        for child in children:
            if child.get("func") == "tablex.header":
                rows = self._convert_table_rows(child)
                if rows:
                    table.rows.extend(rows)
                    table.has_header = True
            elif child.get("func") in ["tablex.hline", "tablex.vline"]:
                continue
            else:
                rows = self._convert_table_rows(child)
                if rows:
                    table.rows.extend(rows)

        label = node.get("label", "")
        if label:
            table.label = label

        return table

    def _convert_table_rows(self, node: Dict[str, Any]) -> List[TableRow]:
        """Convert table rows.

        Args:
            node: Typst table row node

        Returns:
            List of IR TableRows
        """
        rows = []
        children = node.get("children", [])

        for child in children:
            if child.get("func") == "tablex.row":
                cells = self._convert_table_cells(child)
                if cells:
                    row = TableRow(id=str(uuid.uuid4()), cells=cells)
                    rows.append(row)

        return rows

    def _convert_table_cells(self, node: Dict[str, Any]) -> List[TableCell]:
        """Convert table cells.

        Args:
            node: Typst table row node

        Returns:
            List of IR TableCells
        """
        cells = []
        children = node.get("children", [])

        for child in children:
            if child.get("func") == "tablex.cell":
                content_nodes = []
                cell_children = child.get("children", [])

                for cell_child in cell_children:
                    ir_node = self._convert_node(cell_child)
                    if ir_node:
                        content_nodes.append(ir_node)

                cell = TableCell(id=str(uuid.uuid4()), content=content_nodes)
                cells.append(cell)

        return cells

    def _convert_equation(self, node: Dict[str, Any]) -> Equation:
        """Convert equation to IR Equation.

        Args:
            node: Typst equation node

        Returns:
            IR Equation
        """
        block = node.get("block", False)
        body = node.get("body", {})
        label = node.get("label", "")

        latex = self._extract_latex(body)

        equation = Equation(
            id=str(uuid.uuid4()),
            latex=latex,
            label=label if label else None,
            numbering_kind=NumberingKind.EQUATION,
        )

        return equation

    def _convert_ref(self, node: Dict[str, Any]) -> CrossReference:
        """Convert reference to IR CrossReference.

        Args:
            node: Typst ref node

        Returns:
            IR CrossReference
        """
        target = node.get("target", "")
        supplement = node.get("supplement", "")

        ref = CrossReference(
            node_type=NodeType.CROSS_REFERENCE,
            id=str(uuid.uuid4()),
            target_label=target,
            ref_text=supplement if supplement else None,
        )

        return ref

    def _convert_strong(self, node: Dict[str, Any]) -> TextRun:
        """Convert strong text to TextRun.

        Args:
            node: Typst strong node

        Returns:
            IR TextRun (simplified)
        """
        body = node.get("body", {})
        text = self._extract_text_content(body)

        return TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=text)

    def _convert_emph(self, node: Dict[str, Any]) -> TextRun:
        """Convert emphasis to TextRun.

        Args:
            node: Typst emph node

        Returns:
            IR TextRun (simplified)
        """
        body = node.get("body", {})
        text = self._extract_text_content(body)

        return TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=text)

    def _convert_generic(self, node: Dict[str, Any]) -> Optional[TextRun]:
        """Convert generic node to TextRun.

        Args:
            node: Typst node

        Returns:
            IR TextRun or None
        """
        text = self._extract_text_content(node)
        if text:
            return TextRun(node_type=NodeType.TEXT_RUN, id=str(uuid.uuid4()), text=text)
        return None

    def _extract_caption_text(self, node: Dict[str, Any]) -> Optional[str]:
        """Extract text from caption node.

        Args:
            node: Typst caption node

        Returns:
            Caption text or None
        """
        body = node.get("body", {})
        return self._extract_text_content(body)

    def _extract_latex(self, node: Dict[str, Any]) -> str:
        """Extract LaTeX from math node.

        Args:
            node: Typst math node

        Returns:
            LaTeX string
        """
        return self._extract_text_content(node)

    def _extract_text_content(self, node: Dict[str, Any]) -> str:
        """Extract text content from node recursively.

        Args:
            node: Typst node

        Returns:
            Text content
        """
        if not node:
            return ""

        if node.get("func") == "text":
            return node.get("text", "")

        children = node.get("children", [])
        if children:
            return "".join([self._extract_text_content(child) for child in children])

        body = node.get("body")
        if body:
            return self._extract_text_content(body)

        return ""
