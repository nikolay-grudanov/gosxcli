"""DOCX writer for converting IR to Word documents."""

from pathlib import Path
from typing import Any, Optional
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
    TOCNode,
    CitationNode,
    BibliographySection,
    BibliographyEntry,
    TextRun,
    InlineRunNode,
    InlineCodeNode,
    CodeBlockNode,
    NumberingKind,
    ListKind,
    CitationStyle,
    ChapterContext,
    ValidationResult,
)
from ..config import MathMode, RefLabels
from ..parser.validator import ReferenceValidator
from .bookmarks import BookmarksManager
from .styles import StylesManager
from .images import ImagesManager
from .tables import TablesManager


class DocxWriter:
    def __init__(
        self,
        reference_doc: Optional[Path] = None,
        math_mode: MathMode = MathMode.FALLBACK,
        ref_labels: Optional[RefLabels] = None,
        bibliography_style: CitationStyle = CitationStyle.NUMERIC,
    ):
        """Инициализирует DOCX writer.

        Args:
            reference_doc: Путь к шаблону DOCX для стилизации.
            math_mode: Режим рендеринга математических выражений.
            ref_labels: Локализованные метки для ссылок.
            bibliography_style: Стиль цитирования (numeric или author-year).
        """
        self.reference_doc = reference_doc
        self.math_mode = math_mode
        self.citation_style = bibliography_style
        self.entry_lookup: dict[str, BibliographyEntry] = {}
        self.doc = None
        self.bookmarks_manager = BookmarksManager()
        self.styles_manager = StylesManager()
        self.images_manager = ImagesManager()
        self.tables_manager = TablesManager()
        self.chapter_context = ChapterContext()
        self.ref_labels = ref_labels or RefLabels()

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
        elif isinstance(block, TableNode):
            self._write_table(block)
        elif isinstance(block, Equation):
            self._write_equation(block)
        elif isinstance(block, TOCNode):
            self._write_toc(block)
        elif isinstance(block, BibliographySection):
            self._write_bibliography(block)
        elif isinstance(block, CodeBlockNode):
            self._write_code_block(block)
        elif isinstance(block, CrossReference):
            pass

    def _write_section(self, section: Section) -> None:
        self.stats["headings"] += 1

        # Chapter-aware numbering: increment chapter on level 1 sections
        if section.level == 1:
            # Store current chapter number in the section
            section.chapter_number = self.chapter_context.chapter_number
            # Increment chapter number for next chapter
            self.chapter_context.chapter_number += 1
            # Reset counters when starting a new chapter
            self.chapter_context.figure_counter = 0
            self.chapter_context.table_counter = 0
            self.chapter_context.equation_counter = 0
        else:
            # Non-level-1 sections use current chapter number
            section.chapter_number = self.chapter_context.chapter_number

        section.number = self.chapter_context.section_counter

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

    def _write_inline_nodes(self, para: Any, nodes: list[BaseNode]) -> None:
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
                self._write_cross_ref_node(node, para)
            elif isinstance(node, CitationNode):
                self._write_citation(node, para)
            elif hasattr(node, "content"):
                self._write_inline_nodes(para, node.content)

    def _write_list(self, list_block: ListBlock) -> None:
        style = "List Bullet" if list_block.kind == ListKind.BULLET else "List Number"

        for item in list_block.items:
            text = self._nodes_to_text(item.content)
            self.doc.add_paragraph(text, style=style)

    def _write_figure(self, figure: Figure) -> None:
        # Check if figure contains a table instead of an image
        if figure.table:
            # Treat table figure as a table (uses table counter)
            self._write_table(figure.table)
            # Update figure's caption number with table's number
            if figure.caption:
                figure.caption.number = figure.table.number
                figure.caption.chapter_number = figure.table.chapter_number
            # Write caption if present
            if figure.caption:
                self._write_caption(figure.caption)
            return

        # Regular image figure
        self.stats["figures"] += 1

        # Increment figure counter and store in figure
        self.chapter_context.figure_counter += 1
        figure.number = self.chapter_context.figure_counter
        # Use current chapter number (chapter_context.chapter_number - 1 because we increment at section start)
        current_chapter = max(1, self.chapter_context.chapter_number - 1)
        figure.chapter_number = current_chapter

        # Update caption with number info
        if figure.caption:
            figure.caption.number = figure.number
            figure.caption.chapter_number = figure.chapter_number

        if figure.image_path:
            try:
                self.images_manager.add_image(self.doc, figure.image_path, width=Inches(5.0))
            except Exception:
                self.stats["warnings"] += 1

        if figure.caption:
            self._write_caption(figure.caption)

    def _write_table(self, table: TableNode) -> None:
        self.stats["tables"] += 1

        # Increment table counter and store in table
        self.chapter_context.table_counter += 1
        table.number = self.chapter_context.table_counter
        # Use current chapter number (chapter_context.chapter_number - 1 because we increment at section start)
        current_chapter = max(1, self.chapter_context.chapter_number - 1)
        table.chapter_number = current_chapter

        # Update caption with number info
        if table.caption:
            table.caption.number = table.number
            table.caption.chapter_number = table.chapter_number

        self.tables_manager.add_table(self.doc, table)

    def _write_equation(self, equation: Equation) -> None:
        """Записывает математическое уравнение в документ.

        Использует math_mode для выбора метода рендеринга:
        - NATIVE: латекс → OMML через latex2mathml
        - IMAGE: заглушка с текстом (для MVP)
        - FALLBACK: сначала NATIVE, при ошибке → IMAGE

        Args:
            equation: IR узел уравнения.
        """
        self.stats["equations"] += 1

        # Increment equation counter and store in equation
        self.chapter_context.equation_counter += 1
        equation.number = self.chapter_context.equation_counter
        # Use current chapter number (chapter_context.chapter_number - 1 because we increment at section start)
        current_chapter = max(1, self.chapter_context.chapter_number - 1)
        equation.chapter_number = current_chapter

        # Update caption with number info
        if equation.caption:
            equation.caption.number = equation.number
            equation.caption.chapter_number = equation.chapter_number

        def _render_as_image(latex: str) -> None:
            """Рендерит уравнение как текстовую заглушку (MVP)."""
            para = self.doc.add_paragraph(style="Normal")
            para.add_run(f"[FORMULA: {latex}]")
            self.stats["warnings"] += 1

        def _render_as_native(latex: str) -> bool:
            """Рендерит уравнение как OMML.

            Returns:
                True если успешно, False при ошибке.
            """
            try:
                from latex2mathml import converter

                omml = converter.convert(latex)

                para = self.doc.add_paragraph(style="Normal")
                run = para.add_run()
                run._element.append(omml)
                return True
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to render equation as OMML: {e}. Latex: {latex}")
                return False

        # Логика выбора режима рендеринга
        if self.math_mode == MathMode.IMAGE:
            _render_as_image(equation.latex)
        elif self.math_mode == MathMode.NATIVE:
            success = _render_as_native(equation.latex)
            if not success:
                self.stats["warnings"] += 1
        elif self.math_mode == MathMode.FALLBACK:
            success = _render_as_native(equation.latex)
            if not success:
                _render_as_image(equation.latex)

        if equation.caption:
            self._write_caption(equation.caption)

    def _write_toc(self, toc: TOCNode) -> None:
        """Записывает оглавление в документ.

        Использует простой подход: заголовок + placeholder текст.
        python-docx имеет ограниченную поддержку TOC fields,
        поэтому в MVP используем placeholder.

        Args:
            toc: IR узел оглавления.
        """
        # Add TOC title as Heading 1
        self.doc.add_paragraph(toc.title, style="Heading 1")

        # Add placeholder paragraph for TOC content
        # In a full implementation, this would be a TOC field
        # For MVP, we add a placeholder that indicates where TOC should be
        placeholder = self.doc.add_paragraph(style="Normal")
        placeholder.add_run(
            "[Table of Contents will be generated here - Right-click and select Update Field]"
        )
        placeholder.runs[0].italic = True
        placeholder.runs[0].font.color.rgb = None  # Use default color

    def _write_bibliography(self, bib_section: BibliographySection) -> None:
        """Записывает библиографическую секцию в документ.

        Генерирует секцию "Список литературы" с форматированием по ГОСТ 7.32-2017.

        Стили цитирования:
        - AUTHOR_YEAR: Записи сортируются по алфавиту (author → year), формат (Author, Year)
        - NUMERIC: Записи в порядке цитирования, формат [1], [2], [3]

        Форматирование по ГОСТ 7.32-2017:
        - Hanging indent: 1.25 см (первая строка с отступом влево, остальные вправо)
        - Заголовок: "Список литературы" (стиль Heading 1)

        Args:
            bib_section: IR узел библиографической секции.
        """
        from docx.shared import Cm
        from ..ir.model import CitationStyle

        # Add bibliography heading
        # Uses Heading 1 style for consistent document structure
        self.doc.add_paragraph(bib_section.heading, style="Heading 1")

        # Get entries to write (sorted if AUTHOR_YEAR style)
        entries = bib_section.entries
        if bib_section.style == CitationStyle.AUTHOR_YEAR:
            # Sort alphabetically by author last name, then by year
            # Sorting is handled by _get_bibliography_sort_key
            entries = sorted(entries, key=self._get_bibliography_sort_key)

        # Write each bibliography entry with hanging indent
        for i, entry in enumerate(entries, start=1):
            # Format entry text based on citation style
            entry_text = self._format_bibliography_entry(
                entry, i, bib_section.style
            )
            para = self.doc.add_paragraph(style="Normal")

            # Apply hanging indent (1.25cm as per ГОСТ 7.32-2017)
            # First line indent is negative (hanging), rest is positive
            # This creates the classic bibliography formatting where
            # the first line is left-aligned and subsequent lines are indented
            para.paragraph_format.first_line_indent = Cm(-1.25)
            para.paragraph_format.left_indent = Cm(1.25)

            # Add formatted entry text to paragraph
            para.add_run(entry_text)

    def _get_bibliography_sort_key(self, entry: BibliographyEntry) -> tuple[str, str]:
        """Получает ключ сортировки для библиографической записи.

        Используется для сортировки записей в AUTHOR_YEAR стиле.
        Ключ сортировки: (фамилия_автора, год)

        Логика сортировки:
        - Извлекает фамилию автора (первое слово перед запятой или пробелом)
        - Преобразует в lowercase для case-insensitive сортировки
        - Записи без автора помещаются в конец (last_name = "zzz")
        - Записи без года сортируются первыми (year = "0000")

        Args:
            entry: Библиографическая запись для сортировки.

        Returns:
            Кортеж из (фамилия_автора, год) для сортировки.
        """
        # Extract last name for sorting
        author = entry.author or ""
        # Author format may be "Иванов А.А." or "Ivanov A.A., Petrov B.B."
        # Take first word (last name) and convert to lowercase
        # This handles both single-author and multi-author entries
        last_name = author.split()[0].lower() if author else "zzz"
        # Use "zzz" for entries without author to place them at the end
        year = entry.year or "0000"
        # Use "0000" for entries without year to place them first among same author
        return (last_name, year)

    def _format_bibliography_entry(
        self, entry: BibliographyEntry, number: int, style: CitationStyle = CitationStyle.NUMERIC
    ) -> str:
        """Форматирует библиографическую запись по ГОСТ 7.32-2017.

        Форматы по ГОСТ 7.32-2017:

        **Статья (ARTICLE):**
        Автор А.А. Название // Журнал. — Год. — С. XX-XX.

        **Книга (BOOK):**
        Автор Б.Б. Название. — Город: Издательство, Год. — 256 с.

        **Материалы конференции (INPROCEEDINGS):**
        Автор В.В. Название // Труды конференции. — Год. — С. XX-XX.

        **Разное (MISC, TECHREPORT, etc.):**
        Автор. Название. — Год.

        Особенности форматирования:
        - Точки в конце полей удаляются (rstrip("."))
        - Поля соединяются через ". " (точка + пробел)
        - Для NUMERIC стиля добавляется номер: "1. Автор. Название..."
        - Для AUTHOR_YEAR стиля используется отдельный метод

        Args:
            entry: BibliographyEntry для форматирования.
            number: Порядковый номер записи (для NUMERIC стиля).
            style: Стиль цитирования (numeric или author-year).

        Returns:
            Отформатированная строка записи.
        """
        from ..ir.model import BibliographyType

        parts = []

        if entry.entry_type == BibliographyType.ARTICLE:
            # Article format: Автор А.А. Название // Журнал. — Год. — С. XX-XX.
            # Use placeholder for missing fields
            if entry.author:
                parts.append(entry.author.rstrip("."))
            else:
                parts.append("[Без автора]")
            if entry.title:
                parts.append(entry.title.rstrip("."))
            else:
                parts.append("[Без названия]")
            if entry.journal:
                parts.append(entry.journal.rstrip("."))
            if entry.year:
                parts.append(entry.year)
            if entry.pages:
                parts.append(f"С. {entry.pages}")

        elif entry.entry_type == BibliographyType.BOOK:
            # Book format: Автор Б.Б. Название. — Город: Издательство, Год. — 256 с.
            if entry.author:
                parts.append(entry.author.rstrip("."))
            else:
                parts.append("[Без автора]")
            if entry.title:
                parts.append(entry.title.rstrip("."))
            else:
                parts.append("[Без названия]")
            # Publisher may already include address (e.g., "Москва: Наука")
            if entry.publisher:
                pub = entry.publisher.rstrip(".")
                if entry.address and entry.address not in pub:
                    parts.append(f"{entry.address}: {pub}")
                else:
                    parts.append(pub)
            if entry.year:
                parts.append(entry.year)
            if entry.pages:
                parts.append(f"{entry.pages} с.")

        elif entry.entry_type == BibliographyType.INPROCEEDINGS:
            # Inproceedings format: Автор В.В. Название // Труды конференции. — Год. — С. XX-XX.
            if entry.author:
                parts.append(entry.author.rstrip("."))
            else:
                parts.append("[Без автора]")
            if entry.title:
                parts.append(entry.title.rstrip("."))
            else:
                parts.append("[Без названия]")
            if entry.booktitle:
                parts.append(entry.booktitle.rstrip("."))
            if entry.year:
                parts.append(entry.year)
            if entry.pages:
                parts.append(f"С. {entry.pages}")

        else:
            # Generic format for other types (MISC, TECHREPORT, PHDTHESIS, etc.)
            if entry.author:
                parts.append(entry.author.rstrip("."))
            else:
                parts.append("[Без автора]")
            if entry.title:
                parts.append(entry.title.rstrip("."))
            else:
                parts.append("[Без названия]")
            if entry.year:
                parts.append(entry.year)

        # Join parts with '. ' (period space) as per GOST
        entry_text = ". ".join(parts)

        # Format based on citation style
        if style == CitationStyle.AUTHOR_YEAR:
            # AUTHOR_YEAR style: Use separate formatting method
            return self._format_bibliography_entry_author_year(entry)
        else:
            # NUMERIC style: "1. Author Title..."
            return f"{number}. {entry_text}"

    def _format_bibliography_entry_author_year(self, entry: BibliographyEntry) -> str:
        """Форматирует библиографическую запись в стиле author-year (ГОСТ Р 7.0.5-2008).

        Форматы по ГОСТ Р 7.0.5-2008 (автор-год):

        **Статья (ARTICLE):**
        Автор А.А. (Год) Название // Журнал. — С. XX-XX.

        **Книга (BOOK):**
        Автор Б.Б. (Год) Название. — Город: Издательство. — 256 с.

        **Материалы конференции (INPROCEEDINGS):**
        Автор В.В. (Год) Название // Труды конференции. — С. XX-XX.

        **Разное (MISC, TECHREPORT, etc.):**
        Автор (Год) Название.

        Особенности форматирования:
        - Год в скобках после автора: (2023)
        - Для статей и материалов конференции используется "//" перед названием журнала/конференции
        - Поля соединяются через пробел
        - Не добавляется номер записи (в отличие от NUMERIC стиля)
        - Используется эм-даш (—) между частями

        Args:
            entry: BibliographyEntry для форматирования.

        Returns:
            Отформатированная строка записи без нумерации.
        """
        from ..ir.model import BibliographyType

        parts = []
        year = entry.year or ""

        if entry.entry_type == BibliographyType.ARTICLE:
            # Article format: Автор А.А. (Год) Название // Журнал. — С. XX-XX.
            if entry.author:
                parts.append(entry.author.rstrip("."))
            if year:
                parts.append(f"({year})")
            if entry.title:
                parts.append(entry.title.rstrip("."))
            else:
                parts.append("[Без названия]")
            if entry.journal:
                parts.append(f"// {entry.journal.rstrip('.')}")
            if entry.pages:
                parts.append(f"— С. {entry.pages}")

        elif entry.entry_type == BibliographyType.BOOK:
            # Book format: Автор Б.Б. (Год) Название. — Город: Издательство. — 256 с.
            if entry.author:
                parts.append(entry.author.rstrip("."))
            if year:
                parts.append(f"({year})")
            if entry.title:
                parts.append(entry.title.rstrip("."))
            else:
                parts.append("[Без названия]")
            if entry.publisher:
                pub = entry.publisher.rstrip(".")
                if entry.address and entry.address not in pub:
                    parts.append(f"— {entry.address}: {pub}")
                else:
                    parts.append(f"— {pub}")
            if entry.pages:
                parts.append(f"— {entry.pages} с.")

        elif entry.entry_type == BibliographyType.INPROCEEDINGS:
            # Inproceedings format: Автор В.В. (Год) Название // Труды конференции. — С. XX-XX.
            if entry.author:
                parts.append(entry.author.rstrip("."))
            if year:
                parts.append(f"({year})")
            if entry.title:
                parts.append(entry.title.rstrip("."))
            else:
                parts.append("[Без названия]")
            if entry.booktitle:
                parts.append(f"// {entry.booktitle.rstrip('.')}")
            if entry.pages:
                parts.append(f"— С. {entry.pages}")

        else:
            # Generic format for other types (MISC, TECHREPORT, PHDTHESIS, etc.)
            if entry.author:
                parts.append(entry.author.rstrip("."))
            if year:
                parts.append(f"({year})")
            if entry.title:
                parts.append(entry.title.rstrip("."))
            else:
                parts.append("[Без названия]")

        # Join parts with single space (author-year style uses space separator)
        return " ".join(parts)

    def _write_cross_reference(self, ref: CrossReference, para: Any) -> None:
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

    def _write_cross_ref_node(self, ref: CrossRefNode, para) -> None:
        """Записывает CrossRefNode с chapter-aware нумерацией.

        Args:
            ref: CrossRefNode для записи.
            para: Параграф для добавления текста ссылки.
        """
        # Format reference text based on ref_kind and numbering
        ref_text = self._format_cross_ref(ref)

        # Check if target bookmark exists
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
            wt.text = ref_text
            run.append(wt)

            hyperlink.append(run)
            para._element.append(hyperlink)

            self.stats["refs_resolved"] += 1
        else:
            run = para.add_run(ref_text)
            self.stats["refs_unresolved"] += 1
            self.stats["warnings"] += 1

    def _write_citation(self, citation: CitationNode, para: Any) -> None:
        """Записывает inline citation marker.

        Supports both NUMERIC and AUTHOR_YEAR citation styles:
        - NUMERIC: [1], [2], [3]
        - AUTHOR_YEAR: (Иванов, 2023), (Петров, 2022)

        Note: For NUMERIC style, brackets [] are captured as TEXT tokens
        by the scanner, so we only output the number here.

        Args:
            citation: CitationNode с ключом и номером.
            para: Paragraph для добавления маркера.
        """
        if self.citation_style == CitationStyle.AUTHOR_YEAR:
            entry = self.entry_lookup.get(citation.key)
            if entry and entry.author and entry.year:
                # Extract last name (first word before comma or first word)
                author_last = entry.author.split(',')[0].split()[0] if entry.author else ""
                citation_text = f"({author_last}, {entry.year})"
            else:
                # Fallback to numeric if no author/year
                citation_text = f"[{citation.number}]"
        else:
            # NUMERIC style: brackets are added by scanner
            citation_text = f"{citation.number}"

        run = para.add_run(citation_text)
        run.italic = True

    def _format_cross_ref(self, ref: CrossRefNode) -> str:
        """Форматирует текст перекрёстной ссылки с chapter-aware нумерацией.

        Args:
            ref: CrossRefNode для форматирования.

        Returns:
            Отформатированная строка ссылки (например, "Рис. 1.2", "Таблица 2.1").
        """
        # Determine ref kind from target label prefix if not set
        if not ref.ref_kind:
            ref.ref_kind = self._infer_ref_kind(ref.target_label)

        # Get localized label from config
        label = ""
        if ref.ref_kind == "fig":
            label = self.ref_labels.figure
        elif ref.ref_kind == "tbl":
            label = self.ref_labels.table
        elif ref.ref_kind == "eq":
            label = self.ref_labels.equation
        elif ref.ref_kind == "ch":
            label = self.ref_labels.section

        # Format based on ref kind
        if label:
            if ref.ref_kind == "eq":
                # Equations use parentheses: "Формула (1.3)"
                formatted = f"{label} ({ref.chapter_number}.{ref.number})"
            else:
                # Others use standard format: "Рис. 1.2", "Таблица 2.1"
                formatted = f"{label} {ref.chapter_number}.{ref.number}"
        else:
            # Fallback to label.number format
            formatted = f"{ref.chapter_number}.{ref.number}"

        return formatted

    def _infer_ref_kind(self, label: str) -> Optional[str]:
        """Определяет тип ссылки по префиксу метки.

        Args:
            label: Метка ссылки (например, "fig:results", "tbl:data").

        Returns:
            Тип ссылки ("fig", "tbl", "eq", "ch") или None если не удалось определить.
        """
        if label.startswith("fig:"):
            return "fig"
        elif label.startswith("tbl:") or label.startswith("table:"):
            return "tbl"
        elif label.startswith("eq:") or label.startswith("equation:"):
            return "eq"
        elif label.startswith("ch:") or label.startswith("chapter:"):
            return "ch"
        return None

    def _write_caption(self, caption: Caption) -> None:
        # Get localized label from config
        label = ""
        if caption.numbering_kind == NumberingKind.FIGURE:
            label = self.ref_labels.figure
        elif caption.numbering_kind == NumberingKind.TABLE:
            label = self.ref_labels.table
        elif caption.numbering_kind == NumberingKind.EQUATION:
            label = self.ref_labels.equation

        # Format: "Рис. 1.2 - Caption text" or "Таблица 2.1 - Caption text"
        # For equations, use parentheses: "Формула (1.3)"
        if label:
            if caption.numbering_kind == NumberingKind.EQUATION:
                formatted = f"{label} ({caption.chapter_number}.{caption.number})"
            else:
                formatted = f"{label} {caption.chapter_number}.{caption.number}"
        else:
            formatted = f"{caption.chapter_number}.{caption.number}"

        # Add separator if there's text
        if caption.text:
            formatted = f"{formatted} — {caption.text}"  # em-dash for GOST style

        para = self.doc.add_paragraph(style="Caption")
        para.add_run(formatted)

    def _write_code_block(self, code_block: CodeBlockNode) -> None:
        """Записывает блок кода в документ.

        Использует моноширинный шрифт (Courier New/Consolas) для отображения кода.
        Сохраняет отступы и переносы строк. Экранирует XML спецсимволы.

        Args:
            code_block: IR узел блока кода.
        """
        from docx.shared import Pt
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement

        # Разбиваем содержимое на строки
        lines = code_block.content.split("\n")

        # Применяем фоновое затенение к каждому параграфу кода
        for line in lines:
            # Создаем параграф для каждой строки кода
            para = self.doc.add_paragraph(style="Normal")

            # Применяем фоновое затенение (серый цвет)
            # Добавляем shading через OxmlElement
            shading_elm = OxmlElement("w:shd")
            shading_elm.set(qn("w:fill"), "F0F0F0")  # Светло-серый цвет
            para._element.get_or_add_pPr().insert_element_before(
                shading_elm, "w:spacing" if para._element.pPr is not None else None
            )

            # Экранируем XML спецсимволы и добавляем текст
            escaped_line = self._escape_xml_text(line)
            run = para.add_run(escaped_line)

            # Применяем моноширинный шрифт
            run.font.name = "Courier New"
            # Устанавливаем шрифт для East Asian characters (для совместимости)
            run._element.rPr.rFonts.set(qn("w:eastAsia"), "Courier New")
            run.font.size = Pt(9)  # Мелкий шрифт для кода

            # Удаляем интерлиньяж (межстрочный интервал)
            para.paragraph_format.space_before = Pt(0)
            para.paragraph_format.space_after = Pt(0)
            para.paragraph_format.line_spacing = 1.0  # Одиночный интервал

    def _escape_xml_text(self, text: str) -> str:
        """Экранирует XML спецсимволы для безопасного использования в DOCX.

        Экранирует символы: & → &amp;, < → &lt;, > → &gt;
        Это необходимо для корректного XML well-formed output.

        Args:
            text: Текст для экранирования.

        Returns:
            Экранированный текст, безопасный для XML/DOCX.
        """
        # Порядок важен: сначала & (чтобы не экранировать уже экранированные)
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

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

    def validate_references(self, ir_document: IRDocument) -> ValidationResult:
        """Выполняет bidirectional валидацию ссылок и меток.

        Сравнивает определённые метки со ссылками и находит:
        - Неопределённые ссылки (@label без определения)
        - Неиспользуемые метки (<label> без ссылок)

        Args:
            ir_document: IR документ для валидации.

        Returns:
            ValidationResult с результатами валидации.
        """
        validator = ReferenceValidator()
        validator.collect_from_document(ir_document)
        result = validator.validate()

        # Обновляем статистику
        self.stats["refs_unresolved"] = len(result.undefined_refs)
        if result.unreferenced_labels:
            self.stats["warnings"] += len(result.unreferenced_labels)

        return result
