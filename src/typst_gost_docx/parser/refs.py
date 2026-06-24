"""Resolve references with chapter-aware numbering.

Single resolver for the canonical ``CrossReference`` IR node. Walks the entire
document tree (including nested Paragraph.runs and Section.children) and
populates ``ref_kind``, ``number``, ``chapter_number`` and ``ref_text`` on
every reference.

``ref_text`` is what the writer renders as the visible hyperlink text. By
computing it here we eliminate a class of bugs where the writer had to
re-implement resolution with its own label-number map.
"""

from typing import Iterator, Optional, Sequence

from ..ir.model import (
    BaseNode,
    CrossReference,
    Document,
    Paragraph,
    Section,
    ValidationIssue,
    ValidationResult,
)
from ..ir.validator import ISSUE_UNDEFINED_REF
from ..utils.ref_utils import infer_ref_kind

_REF_TEXT_TEMPLATES: dict[str, str] = {
    "fig": "Рис. {chapter}.{number}",
    "tbl": "Табл. {chapter}.{number}",
    "eq": "Формула {chapter}.{number}",
    "section": "Раздел {chapter}.{number}",
}


class RefResolver:
    """Resolves every ``CrossReference`` in a document.

    Builds a label map by traversing the document (figures, tables, equations,
    sections), then fills the matching fields on each ``CrossReference`` it
    finds. Unresolved references are reported as warnings but do not raise.
    """

    def __init__(self, cross_ref_map: Optional[object] = None) -> None:
        # cross_ref_map kept for legacy callers; we rebuild the map from the
        # document directly so callers can pass `None` or omit the argument.
        self.cross_ref_map = cross_ref_map

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def resolve_document(self, document: Document) -> list[str]:
        """Resolve every reference inside ``document.blocks``.

        Returns a list of human-readable warnings for unresolved references.
        """
        label_map = self._build_label_map(document)
        warnings: list[str] = []
        for ref in self._iter_references(document.blocks):
            warning = self._resolve_one(ref, label_map)
            if warning is not None:
                warnings.append(warning)
        return warnings

    # Backwards-compatible shim used by ``validator.py`` and tests.
    def resolve_refs(self, nodes: Sequence[BaseNode]) -> list[str]:
        label_map = self._build_label_map_from_nodes(nodes)
        warnings: list[str] = []
        for ref in self._iter_references(nodes):
            warning = self._resolve_one(ref, label_map)
            if warning is not None:
                warnings.append(warning)
        return warnings

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    @staticmethod
    def _iter_references(nodes: Sequence[BaseNode]) -> Iterator[BaseNode]:
        """Yield every CrossReference nested inside ``nodes``."""
        for node in nodes:
            yield from RefResolver._walk(node)

    @staticmethod
    def _walk(node: BaseNode) -> Iterator[BaseNode]:
        if isinstance(node, CrossReference):
            yield node
        elif isinstance(node, Document):
            yield from RefResolver._walk_blocks(node.blocks)
        elif isinstance(node, Section):
            yield from RefResolver._walk_blocks(node.blocks)
        elif isinstance(node, Paragraph):
            runs = getattr(node, "runs", None) or []
            for run in runs:
                yield from RefResolver._walk(run)

    @staticmethod
    def _walk_blocks(blocks: Sequence[BaseNode]) -> Iterator[BaseNode]:
        for b in blocks:
            yield from RefResolver._walk(b)

    @staticmethod
    def _build_label_map(document: Document) -> dict[str, BaseNode]:
        return RefResolver._build_label_map_from_nodes(document.blocks)

    @staticmethod
    def _build_label_map_from_nodes(nodes: Sequence[BaseNode]) -> dict[str, BaseNode]:
        labels: dict[str, BaseNode] = {}
        for node in nodes:
            RefResolver._collect_labels(node, labels)
        return labels

    @staticmethod
    def _collect_labels(node: BaseNode, out: dict[str, BaseNode]) -> None:
        label = getattr(node, "label", None)
        if label and label not in out:
            out[label] = node
        if isinstance(node, Document):
            for b in node.blocks:
                RefResolver._collect_labels(b, out)
        elif isinstance(node, Section):
            for b in node.blocks:
                RefResolver._collect_labels(b, out)
        elif isinstance(node, Paragraph):
            for run in getattr(node, "runs", None) or []:
                RefResolver._collect_labels(run, out)

    @staticmethod
    def _resolve_one(ref: BaseNode, label_map: dict[str, BaseNode]) -> Optional[str]:
        if not isinstance(ref, CrossReference):
            return None
        if not ref.ref_kind:
            ref.ref_kind = infer_ref_kind(ref.target_label) or ""
        target = label_map.get(ref.target_label)
        if target is None:
            return f"Unresolved reference: @{ref.target_label}"

        chapter_number, number = RefResolver._extract_numbers(target)
        ref.number = number
        ref.chapter_number = chapter_number
        if ref.ref_kind and chapter_number > 0 and number > 0:
            template = _REF_TEXT_TEMPLATES.get(ref.ref_kind)
            if template is not None:
                ref.ref_text = template.format(chapter=chapter_number, number=number)
        return None

    @staticmethod
    def _extract_numbers(target: BaseNode) -> tuple[int, int]:
        """Return (chapter_number, number) for any IR node that carries both."""
        chapter = getattr(target, "chapter_number", 0) or 0
        number = getattr(target, "number", 0) or 0
        if chapter == 0 and number == 0:
            caption = getattr(target, "caption", None)
            if caption is not None:
                chapter = getattr(caption, "chapter_number", 0) or 0
                number = getattr(caption, "number", 0) or 0
        return chapter, number

    @staticmethod
    def build_validation_report(
        document: Document,
        unresolved_warnings: Sequence[str],
    ) -> ValidationResult:
        """Build a ValidationResult from the resolver's collected state.

        ``unresolved_warnings`` is the list of ``"Unresolved reference: @x"``
        strings returned by :meth:`resolve_document`. The function lifts
        them back into structured ``ValidationIssue`` entries with the
        file location of the offending cross-reference.

        Spec 001 T088: dedicated report generator living next to the
        resolver that produced the data, so the CLI can render
        actionable messages without re-walking the IR.
        """
        issues: list[ValidationIssue] = []

        for warning in unresolved_warnings:
            # "Unresolved reference: @fig:missing" → "fig:missing"
            label = warning.split("@", 1)[-1].strip() if "@" in warning else warning
            location = RefResolver._find_reference_location(document, label)
            issues.append(
                ValidationIssue(
                    label=label,
                    kind=ISSUE_UNDEFINED_REF,
                    file_path=getattr(location, "file_path", "") or "",
                    line=getattr(location, "line", 0) or 0,
                    column=getattr(location, "column", 0) or 0,
                )
            )

        return ValidationResult(
            undefined_refs={i.label for i in issues},
            issues=issues,
        )

    @staticmethod
    def _find_reference_location(document: Document, target_label: str) -> object | None:
        """Return the first ``SourceLocation`` where ``@target_label`` appears."""
        for node in RefResolver._walk(document):
            if isinstance(node, CrossReference) and node.target_label == target_label:
                return getattr(node, "source_location", None)
        return None
