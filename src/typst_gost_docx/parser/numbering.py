"""Chapter-aware numbering pass for IR.

Runs after parsing and before reference resolution. Walks the document
in order and assigns:

* ``section.chapter_number`` / ``section.number``
* ``figure.chapter_number`` / ``figure.number`` (and caption equivalents)
* ``table.chapter_number`` / ``table.number``
* ``equation.chapter_number`` / ``equation.number``

Without this pass, ``Figure.number == 0`` from the parser and only the
writer ever computes real values, which made cross-references unresolvable
at the parser layer. Now the writer can simply read pre-computed numbers.
"""


from ..ir.model import (
    BaseNode,
    Caption,
    Document,
    Equation,
    Figure,
    Section,
    TableNode,
)


class ChapterNumberer:
    """Assigns chapter-local numbers to every IR node that needs them.

    Mirrors the rules previously inlined in :class:`DocxWriter`. Each
    ``Heading 1`` (``Section(level=1)``) starts a new chapter and resets
    the per-chapter counters. Numbering is consumed downstream by the
    reference resolver and the writer.
    """

    def __init__(self) -> None:
        self.chapter_number = 0
        self.figure_counter = 0
        self.table_counter = 0
        self.equation_counter = 0
        self.section_counter = 0

    def number_document(self, document: Document) -> None:
        for block in document.blocks:
            self._visit(block)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _visit(self, node: BaseNode) -> None:
        if isinstance(node, Section):
            self._number_section(node)
        elif isinstance(node, Figure):
            self._number_figure(node)
        elif isinstance(node, TableNode):
            self._number_table(node)
        elif isinstance(node, Equation):
            self._number_equation(node)

        # Recurse into nested blocks where applicable.
        if isinstance(node, Section):
            for child in node.blocks:
                self._visit(child)
        elif isinstance(node, Document):
            for child in node.blocks:
                self._visit(child)

    # ------------------------------------------------------------------
    # Per-kind helpers
    # ------------------------------------------------------------------
    def _number_section(self, section: Section) -> None:
        self.section_counter += 1
        if section.level == 1:
            self.chapter_number += 1
            self.figure_counter = 0
            self.table_counter = 0
            self.equation_counter = 0
        section.chapter_number = self.chapter_number
        section.number = self.section_counter

    def _number_figure(self, figure: Figure) -> None:
        if self.chapter_number == 0:
            # Figures before any Heading 1 live in chapter 1 by convention.
            self.chapter_number = 1
        self.figure_counter += 1
        figure.number = self.figure_counter
        figure.chapter_number = self.chapter_number
        if figure.caption is not None:
            self._assign_caption(figure.caption, self.figure_counter)

    def _number_table(self, table: TableNode) -> None:
        if self.chapter_number == 0:
            self.chapter_number = 1
        self.table_counter += 1
        table.number = self.table_counter
        table.chapter_number = self.chapter_number
        if table.caption is not None:
            self._assign_caption(table.caption, self.table_counter)

    def _number_equation(self, equation: Equation) -> None:
        if self.chapter_number == 0:
            self.chapter_number = 1
        self.equation_counter += 1
        equation.number = self.equation_counter
        equation.chapter_number = self.chapter_number
        if equation.caption is not None:
            self._assign_caption(equation.caption, self.equation_counter)

    @staticmethod
    def _assign_caption(caption: Caption, number: int) -> None:
        """Make sure ``caption.number`` matches the parent node's number."""
        if not getattr(caption, "number", None):
            caption.number = number


__all__ = ["ChapterNumberer"]
