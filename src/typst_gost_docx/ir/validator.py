"""Bidirectional validation of references and labels."""

import logging
from collections.abc import Sequence

from .model import (
    BaseNode,
    Document,
    CrossReference,
    CrossRefNode,
    Section,
    Paragraph,
    ValidationIssue,
    ValidationResult,
    CitationNode,
    BibliographyEntry,
)

logger = logging.getLogger(__name__)


# Issue kinds — string constants so they survive serialisation.
ISSUE_UNDEFINED_REF = "undefined_ref"
ISSUE_UNREFERENCED_LABEL = "unreferenced_label"
ISSUE_MISSING_CITATION = "missing_citation"


class ReferenceValidator:
    """Валидатор для bidirectional проверки ссылок и меток.

    Проверяет что:
    - Все ссылки (@label) имеют определения
    - Все метки (<label>) используются в ссылках
    - Все цитирования (@[key]) имеют соответствующие записи в библиографии

    Собирает ``ValidationIssue`` с source-location для каждой найденной
    проблемы, чтобы CLI мог показать ``file.typ:42: Undefined reference``
    вместо безликого ``@fig:missing``.

    Attributes:
        defined_labels: Словарь определённых меток {label: node}.
        referenced_labels: Множество ссылок на метки.
        referenced_locations: {label: SourceLocation} — где встретилась ссылка.
        defined_locations: {label: SourceLocation} — где определена метка.
        bibliography_entries: Словарь библиографических записей {key: entry}.
        referenced_citations: Множество citation keys, использованных в документе.
        citation_locations: {key: SourceLocation} — где встретилась citation.
    """

    def __init__(self, bibliography_entries: dict[str, BibliographyEntry] | None = None) -> None:
        """Инициализирует валидатор.

        Args:
            bibliography_entries: Опциональный словарь библиографических записей
                для проверки citation keys.
        """
        self.defined_labels: dict[str, BaseNode] = {}
        self.referenced_labels: set[str] = set()
        self.defined_locations: dict[str, object] = {}
        self.referenced_locations: dict[str, object] = {}
        self.bibliography_entries: dict[str, BibliographyEntry] = bibliography_entries or {}
        self.referenced_citations: set[str] = set()
        self.citation_locations: dict[str, object] = {}

    def collect_from_document(self, doc: Document) -> None:
        """Собирает все метки и ссылки из IR документа.

        Рекурсивно обходит дерево документа и собирает:
        - Метки из узлов с атрибутом label
        - Ссылки из узлов CrossReference и CrossRefNode
        - Citation keys из узлов CitationNode
        - SourceLocation для каждой найденной ссылки/метки

        Args:
            doc: IR документ для анализа.
        """
        self.defined_labels.clear()
        self.referenced_labels.clear()
        self.defined_locations.clear()
        self.referenced_locations.clear()
        self.referenced_citations.clear()
        self.citation_locations.clear()

        self._collect_from_nodes(doc.blocks)

    def _collect_from_nodes(self, nodes: Sequence[BaseNode]) -> None:
        """Рекурсивно собирает метки и ссылки из списка узлов.

        Args:
            nodes: Список IR узлов.
        """
        for node in nodes:
            # Собираем метки
            if hasattr(node, "label") and node.label:
                self.defined_labels[node.label] = node
                loc = getattr(node, "source_location", None)
                if loc is not None:
                    self.defined_locations[node.label] = loc

            # Собираем ссылки
            if isinstance(node, (CrossReference, CrossRefNode)):
                self.referenced_labels.add(node.target_label)
                loc = getattr(node, "source_location", None)
                if loc is not None:
                    # Keep the first location we see for each label.
                    self.referenced_locations.setdefault(node.target_label, loc)

            # Собираем citation keys
            if isinstance(node, CitationNode):
                self.referenced_citations.add(node.key)
                loc = getattr(node, "source_location", None)
                if loc is not None:
                    self.citation_locations.setdefault(node.key, loc)

            # Рекурсивно обходим вложенные узлы
            if isinstance(node, Document):
                self._collect_from_nodes(node.blocks)
            elif isinstance(node, Section):
                self._collect_from_nodes(node.blocks)
            elif isinstance(node, Paragraph):
                if hasattr(node, "runs"):
                    for run in node.runs:
                        if isinstance(run, (CrossReference, CrossRefNode)):
                            self.referenced_labels.add(run.target_label)
                            loc = getattr(run, "source_location", None)
                            if loc is not None:
                                self.referenced_locations.setdefault(
                                    run.target_label, loc
                                )
                        elif isinstance(run, CitationNode):
                            self.referenced_citations.add(run.key)
                            loc = getattr(run, "source_location", None)
                            if loc is not None:
                                self.citation_locations.setdefault(run.key, loc)

    def validate(self) -> ValidationResult:
        """Выполняет bidirectional валидацию ссылок и меток.

        Находит:
        - Неопределённые ссылки: ссылки, которые не имеют определения
        - Неиспользуемые метки: метки, на которые нет ссылок
        - Отсутствующие citation keys: @[key] citations, которые не найдены в .bib файле

        Returns:
            ValidationResult с результатами валидации. ``issues`` содержит
            подробные ``ValidationIssue`` с source-location, ``undefined_refs``
            и ``unreferenced_labels`` — это set-проекции для обратной
            совместимости.
        """
        undefined_refs = self.referenced_labels - self.defined_labels.keys()
        unreferenced_labels = self.defined_labels.keys() - self.referenced_labels

        issues: list[ValidationIssue] = []
        for ref in sorted(undefined_refs):
            loc = self.referenced_locations.get(ref)
            issues.append(
                ValidationIssue(
                    label=ref,
                    kind=ISSUE_UNDEFINED_REF,
                    file_path=getattr(loc, "file_path", "") or "",
                    line=getattr(loc, "line", 0) or 0,
                    column=getattr(loc, "column", 0) or 0,
                )
            )
        for label in sorted(unreferenced_labels):
            loc = self.defined_locations.get(label)
            issues.append(
                ValidationIssue(
                    label=label,
                    kind=ISSUE_UNREFERENCED_LABEL,
                    file_path=getattr(loc, "file_path", "") or "",
                    line=getattr(loc, "line", 0) or 0,
                    column=getattr(loc, "column", 0) or 0,
                )
            )

        # Citation checks (only if bibliography is provided).
        if self.bibliography_entries:
            missing_citations = self.referenced_citations - self.bibliography_entries.keys()
            for key in sorted(missing_citations):
                loc = self.citation_locations.get(key)
                issues.append(
                    ValidationIssue(
                        label=key,
                        kind=ISSUE_MISSING_CITATION,
                        file_path=getattr(loc, "file_path", "") or "",
                        line=getattr(loc, "line", 0) or 0,
                        column=getattr(loc, "column", 0) or 0,
                    )
                )

        result = ValidationResult(
            undefined_refs=undefined_refs,
            unreferenced_labels=unreferenced_labels,
            issues=issues,
        )

        # Spec 001 T087 — dedicated log levels: undefined = WARNING,
        # unreferenced = INFO, missing citations = WARNING.
        for issue in issues:
            if issue.kind == ISSUE_UNDEFINED_REF:
                logger.warning("Undefined reference: @%s", issue.label)
            elif issue.kind == ISSUE_UNREFERENCED_LABEL:
                logger.info("Unreferenced label: <%s>", issue.label)
            elif issue.kind == ISSUE_MISSING_CITATION:
                logger.warning("Citation key '@[%s]' not found in bibliography", issue.label)

        return result

    def get_defined_labels(self) -> dict[str, BaseNode]:
        """Возвращает словарь определённых меток.

        Returns:
            Словарь {label: node}.
        """
        return self.defined_labels.copy()

    def get_referenced_labels(self) -> set[str]:
        """Возвращает множество ссылок на метки.

        Returns:
            Множество меток, на которые есть ссылки.
        """
        return self.referenced_labels.copy()

    def get_validation_summary(self) -> dict[str, int]:
        """Возвращает статистику валидации.

        Returns:
            Словарь со статистикой:
                - total_labels: общее количество определённых меток
                - referenced_count: количество меток, на которые есть ссылки
                - unreferenced_count: количество меток, на которые нет ссылок
                - total_refs: общее количество ссылок
                - defined_count: количество ссылок с определениями
                - undefined_count: количество ссылок без определений
                - citation_keys_total / missing / defined
        """
        total_labels = len(self.defined_labels)
        referenced_count = len(self.defined_labels.keys() & self.referenced_labels)
        unreferenced_count = len(self.defined_labels.keys() - self.referenced_labels)

        total_refs = len(self.referenced_labels)
        defined_count = len(self.referenced_labels & self.defined_labels.keys())
        undefined_count = len(self.referenced_labels - self.defined_labels.keys())

        citation_total = len(self.referenced_citations)
        citation_missing = (
            len(self.referenced_citations - self.bibliography_entries.keys())
            if self.bibliography_entries
            else 0
        )
        citation_defined = (
            len(self.referenced_citations & self.bibliography_entries.keys())
            if self.bibliography_entries
            else 0
        )

        return {
            "total_labels": total_labels,
            "referenced_count": referenced_count,
            "unreferenced_count": unreferenced_count,
            "total_refs": total_refs,
            "defined_count": defined_count,
            "undefined_count": undefined_count,
            "citation_keys_total": citation_total,
            "citation_keys_defined": citation_defined,
            "citation_keys_missing": citation_missing,
        }


__all__ = ["ReferenceValidator", "ISSUE_UNDEFINED_REF", "ISSUE_UNREFERENCED_LABEL", "ISSUE_MISSING_CITATION"]
