"""DOCX writer for converting IR to Word documents."""

from pathlib import Path
from typing import Optional
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from ..ir.model import (
    Document as IRDocument,
    BaseNode,
    Section,
    Paragraph,
    ListBlock,
    ListItem,
    Table,
    Figure,
    Caption,
    NumberingKind,
    ListKind,
    NodeType,
)
from .bookmarks import BookmarksManager
from .styles import StylesManager
from .images import ImagesManager
from .tables import TablesManager


class DocxWriter:
    def __init__(self, reference_doc: Optional[Path] = None):
        self.reference_doc = reference_doc
        self.doc = None
        self.bookmarks_manager = BookmarksManager()
        self.styles_manager = StylesManager()
        self.images_manager = ImagesManager()
        self.tables_manager = TablesManager()

        self.stats = {
            "headings": 0,
            "paragraphs": 0,
            "tables": 0,
            "figures": 0,
            "equations": 0,
            "refs_resolved": 0,
            "refs_unresolved": 0,
            "warnings": 0,
        }

    def write(self, ir_document: IRDocument, output_path: Path) -> dict:
        if self.reference_doc and self.reference_doc.exists():
            self.doc = Document(str(self.reference_doc))
        else:
            self.doc = Document()

        self._write_document(ir_document)

        self.doc.save(str(output_path))
        return self.stats

    def _write_document(self, ir_doc: IRDocument) -> None:
        for block in ir_doc.blocks:
            self._write_block(block)

    def _write_block(self, block: BaseNode) -> None:
        if isinstance(block, Section):
            self._write_section(block)
        elif isinstance(block, Paragraph):
            self._write_paragraph(block)
        elif isinstance(block, ListBlock):
            self._write_list(block)
        elif isinstance(block, Figure):
            self._write_figure(block)
        elif isinstance(block, Table):
            self._write_table(block)

    def _write_section(self, section: Section) -> None:
        self.stats["headings"] += 1

        style_name = self._get_heading_style(section.level)

        if section.title:
            title_text = self._nodes_to_text(section.title)
            para = self.doc.add_paragraph(title_text, style=style_name)
            self.bookmarks_manager.add_bookmark_if_needed(para, section.label)

    def _write_paragraph(self, paragraph: Paragraph) -> None:
        self.stats["paragraphs"] += 1

        text = self._nodes_to_text(paragraph.content)
        para = self.doc.add_paragraph(text, style="Normal")
        self.bookmarks_manager.add_bookmark_if_needed(para, paragraph.label)

    def _write_list(self, list_block: ListBlock) -> None:
        style = "List Bullet" if list_block.kind == ListKind.BULLET else "List Number"

        for item in list_block.items:
            text = self._nodes_to_text(item.content)
            para = self.doc.add_paragraph(text, style=style)

    def _write_figure(self, figure: Figure) -> None:
        self.stats["figures"] += 1

        if figure.image_path:
            try:
                self.images_manager.add_image(self.doc, figure.image_path, width=Inches(5.0))
            except Exception:
                self.stats["warnings"] += 1

        if figure.caption:
            self._write_caption(figure.caption)

    def _write_table(self, table: Table) -> None:
        self.stats["tables"] += 1
        self.tables_manager.add_table(self.doc, table)

    def _write_caption(self, caption: Caption) -> None:
        prefix = ""
        if caption.numbering_kind == NumberingKind.FIGURE:
            prefix = "Рис. "
        elif caption.numbering_kind == NumberingKind.TABLE:
            prefix = "Таблица "
        elif caption.numbering_kind == NumberingKind.EQUATION:
            prefix = "Формула "

        para = self.doc.add_paragraph(style="Caption")
        run = para.add_run(f"{prefix}{caption.text}")

    def _nodes_to_text(self, nodes: list[BaseNode]) -> str:
        text_parts = []
        for node in nodes:
            if hasattr(node, "text"):
                text_parts.append(node.text)
            elif hasattr(node, "content"):
                text_parts.append(self._nodes_to_text(node.content))
        return "".join(text_parts)

    def _get_heading_style(self, level: int) -> str:
        styles = {1: "Heading 1", 2: "Heading 2", 3: "Heading 3"}
        return styles.get(level, "Heading 1")
