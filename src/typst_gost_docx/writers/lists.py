"""List rendering: bullets, numbered lists, multilevel.

Wraps the python-docx numbering plumbing so the writer can emit a list
item as a single call. Without proper ``numPr`` the items render as plain
paragraphs and the user sees a wall of un-bulleted text — which is what
was happening before this module existed.

Public API:
    ListsManager(doc)  — created per-document.
    manager.add_item(text, kind)  — add a single list item paragraph.
    manager.add_item_with_runs(runs, kind)  — add item with inline runs.

Each manager owns a single numbering definition per kind, so consecutive
bullet items share the same numId (Word restarts at 1 only when the
numbering is broken).
"""

from __future__ import annotations

from typing import Any, Iterator, Sequence

from docx.document import Document as _Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from ..ir.model import ListBlock, ListKind


_BULLET_NUM_ID = 100
_NUMBERED_NUM_ID = 101


class ListsManager:
    """Renders ``ListBlock`` items with proper Word numbering."""

    def __init__(self, doc: _Document) -> None:
        self.doc = doc
        self._initialized: set[int] = set()
        self._next_index: dict[int, int] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def write_list(self, list_block: ListBlock) -> None:
        """Write every item in ``list_block`` as a numbered paragraph."""
        num_id = self._ensure_numbering(list_block.kind)
        for item in list_block.items:
            para = self.doc.add_paragraph()
            self._apply_numbering(para, num_id, list_block.kind)
            for run in self._render_content(item.content):
                para._p.append(run)

    def add_item(self, text: str, kind: ListKind) -> None:
        """Append a single text-only list item (for tests)."""
        para = self.doc.add_paragraph(text)
        num_id = self._ensure_numbering(kind)
        self._apply_numbering(para, num_id, kind)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ensure_numbering(self, kind: ListKind) -> int:
        """Create the numbering definition if missing, return its numId."""
        num_id = _BULLET_NUM_ID if kind == ListKind.BULLET else _NUMBERED_NUM_ID
        if num_id in self._initialized:
            return num_id

        numbering_part = self.doc.part.numbering_part
        if numbering_part is None:
            # python-docx auto-creates a numbering part the first time you
            # touch it; force that by asking for it.

            numbering_part = self.doc.part.numbering_part
            if numbering_part is None:
                # Fallback: create via list_number style on a throwaway
                # paragraph. python-docx ≥1.x exposes _part_factory for this.
                # In practice python-docx always has one by the time we run
                # the writer, because the template brings it in.
                raise RuntimeError(
                    "Document is missing a numbering part. "
                    "The reference template must provide one for lists to render."
                )

        numbering = numbering_part.element

        # Choose bullet or decimal numbering.
        if kind == ListKind.BULLET:
            num_fmt = "bullet"
            lvl_text = "\u2022"  # •
            indent_left = 720  # 0.5"
        else:
            num_fmt = "decimal"
            lvl_text = "%1."
            indent_left = 720

        abstract_id = num_id
        # Build <w:abstractNum>.
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), str(abstract_id))
        for ilvl in range(3):  # support 3 indent levels
            lvl = OxmlElement("w:lvl")
            lvl.set(qn("w:ilvl"), str(ilvl))
            start = OxmlElement("w:start")
            start.set(qn("w:val"), "1")
            num_fmt_el = OxmlElement("w:numFmt")
            num_fmt_el.set(qn("w:val"), num_fmt)
            lvl_text_el = OxmlElement("w:lvlText")
            lvl_text_el.set(qn("w:val"), lvl_text)
            lvl_jc = OxmlElement("w:lvlJc")
            lvl_jc.set(qn("w:val"), "left")
            p_pr = OxmlElement("w:pPr")
            ind = OxmlElement("w:ind")
            ind.set(qn("w:left"), str(indent_left + ilvl * 360))
            ind.set(qn("w:hanging"), "360")
            p_pr.append(ind)
            for el in (start, num_fmt_el, lvl_text_el, lvl_jc, p_pr):
                lvl.append(el)
            abstract.append(lvl)

        # Build <w:num> that references the abstract.
        num = OxmlElement("w:num")
        num.set(qn("w:numId"), str(num_id))
        abs_ref = OxmlElement("w:abstractNumId")
        abs_ref.set(qn("w:val"), str(abstract_id))
        num.append(abs_ref)

        # Insert abstractNum BEFORE any <w:num> (OOXML schema requires this order).
        # Find the first <w:num> and insert before it; otherwise append.
        first_num = numbering.find(qn("w:num"))
        if first_num is not None:
            first_num.addprevious(abstract)
        else:
            numbering.append(abstract)
        numbering.append(num)

        self._initialized.add(num_id)
        self._next_index[num_id] = 0
        return num_id

    @staticmethod
    def _apply_numbering(para: Any, num_id: int, kind: ListKind) -> None:
        pPr = para._p.get_or_add_pPr()
        numPr = OxmlElement("w:numPr")
        ilvl = OxmlElement("w:ilvl")
        ilvl.set(qn("w:val"), "0")
        num_id_el = OxmlElement("w:numId")
        num_id_el.set(qn("w:val"), str(num_id))
        numPr.append(ilvl)
        numPr.append(num_id_el)
        pPr.append(numPr)

    @staticmethod
    def _render_content(content: Sequence[object]) -> Iterator[Any]:
        """Convert a sequence of inline IR nodes into lxml <w:r> elements."""
        for node in content:
            text = getattr(node, "text", None)
            if isinstance(text, str) and text:
                run = OxmlElement("w:r")
                t = OxmlElement("w:t")
                t.text = text
                t.set(qn("xml:space"), "preserve")
                run.append(t)
                yield run


__all__ = ["ListsManager"]
