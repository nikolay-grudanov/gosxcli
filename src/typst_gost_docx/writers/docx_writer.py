"""DOCX writer for converting IR to Word documents."""

from pathlib import Path
from typing import Optional
from docx import Document
from docx.shared import Inches
from ..ir.model import (
    Document as IRDocument,
    BaseNode,
    Section,
    Paragraph,
    ListBlock,
    TableNode,
    Figure,
    Caption,
    Equation,
    CrossReference,
    CrossRefNode,
    TextRun,
    InlineRunNode,
    InlineCodeNode,
    NumberingKind,
    ListKind,
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
        from ..ir.model import Equation, CrossReference

        if isinstance(block, Section):
            self._write_section(block)
        elif isinstance(block, Paragraph):
            self._write_paragraph(block)
        elif isinstance(block, ListBlock):
            self._write_list(block)
        elif isinstance(block, Figure):
            self._write_figure(block)
        elif isinstance(block, TableNode):
            self._write_table(block)
        elif isinstance(block, Equation):
            self._write_equation(block)
        elif isinstance(block, CrossReference):
            pass

    def _write_section(self, section: Section) -> None:
        self.stats["headings"] += 1

        style_name = self._get_heading_style(section.level)

        if section.title:
            title_text = self._nodes_to_text(section.title)
            para = self.doc.add_paragraph(title_text, style=style_name)
            self.bookmarks_manager.add_bookmark_if_needed(para, section.label)

    def _write_paragraph(self, paragraph: Paragraph) -> None:
        self.stats["paragraphs"] += 1

        para = self.doc.add_paragraph(style="Normal")
        self._write_inline_nodes(para, paragraph.runs)
        self.bookmarks_manager.add_bookmark_if_needed(para, paragraph.label)

    def _write_inline_nodes(self, para, nodes: list[BaseNode]) -> None:
        for node in nodes:
            if isinstance(node, TextRun):
                para.add_run(node.text)
            elif isinstance(node, InlineRunNode):
                run = para.add_run(node.text)
                if node.bold:
                    run.bold = True
                if node.italic:
                    run.italic = True
                if node.underline:
                    run.underline = True
            elif isinstance(node, InlineCodeNode):
                run = para.add_run(node.code)
                try:
                    run.style = "Code"
                except KeyError:
                    # Fallback: use Courier font if Code style doesn't exist
                    run.font.name = "Courier New"
            elif isinstance(node, CrossReference):
                self._write_cross_reference(node, para)
            elif isinstance(node, CrossRefNode):
                run = para.add_run(node.ref_text if node.ref_text else node.target_label)
            elif hasattr(node, "content"):
                self._write_inline_nodes(para, node.content)

    def _write_list(self, list_block: ListBlock) -> None:
        style = "List Bullet" if list_block.kind == ListKind.BULLET else "List Number"

        for item in list_block.items:
            text = self._nodes_to_text(item.content)
            self.doc.add_paragraph(text, style=style)

    def _write_figure(self, figure: Figure) -> None:
        self.stats["figures"] += 1

        if figure.image_path:
            try:
                self.images_manager.add_image(self.doc, figure.image_path, width=Inches(5.0))
            except Exception:
                self.stats["warnings"] += 1

        if figure.caption:
            self._write_caption(figure.caption)

    def _write_table(self, table: TableNode) -> None:
        self.stats["tables"] += 1
        self.tables_manager.add_table(self.doc, table)

    def _write_equation(self, equation: Equation) -> None:
        self.stats["equations"] += 1

        try:
            from latex2mathml import converter

            omml = converter.convert(equation.latex)

            para = self.doc.add_paragraph(style="Normal")
            run = para.add_run()

            run._element.append(omml)

            self.stats["warnings"] += 1
        except Exception:
            para = self.doc.add_paragraph(style="Normal")
            run = para.add_run(f"[FORMULA: {equation.latex}]")
            self.stats["warnings"] += 1

        if equation.caption:
            self._write_caption(equation.caption)

    def _write_cross_reference(self, ref: CrossReference, para) -> None:
        target = self.bookmarks_manager.get_bookmark(ref.target_label)

        if target:
            from docx.oxml.shared import OxmlElement, qn

            hyperlink = OxmlElement("w:hyperlink")
            hyperlink.set(qn("w:anchor"), ref.target_label)

            run = OxmlElement("w:r")
            rPr = OxmlElement("w:rPr")

            wcolor = OxmlElement("w:color")
            wcolor.set(qn("w:val"), "0000FF")
            rPr.append(wcolor)

            wu = OxmlElement("w:u")
            wu.set(qn("w:val"), "single")
            rPr.append(wu)

            run.append(rPr)

            wt = OxmlElement("w:t")
            wt.text = ref.ref_text if ref.ref_text else ref.target_label
            run.append(wt)

            hyperlink.append(run)
            para._element.append(hyperlink)

            self.stats["refs_resolved"] += 1
        else:
            run = para.add_run(ref.ref_text if ref.ref_text else ref.target_label)
            self.stats["refs_unresolved"] += 1
            self.stats["warnings"] += 1

    def _write_caption(self, caption: Caption) -> None:
        prefix = ""
        if caption.numbering_kind == NumberingKind.FIGURE:
            prefix = "Рис. "
        elif caption.numbering_kind == NumberingKind.TABLE:
            prefix = "Таблица "
        elif caption.numbering_kind == NumberingKind.EQUATION:
            prefix = "Формула "

        para = self.doc.add_paragraph(style="Caption")
        para.add_run(f"{prefix}{caption.text}")

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
