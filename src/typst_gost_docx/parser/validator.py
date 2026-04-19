"""Bidirectional validation of references and labels."""

import logging
from collections.abc import Sequence

from ..ir.model import (
    BaseNode,
    Document,
    CrossReference,
    CrossRefNode,
    Section,
    Paragraph,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class ReferenceValidator:
    """Валидатор для bidirectional проверки ссылок и меток.

    Проверяет что:
    - Все ссылки (@label) имеют определения
    - Все метки (<label>) используются в ссылках

    Attributes:
        defined_labels: Словарь определённых меток {label: node}.
        referenced_labels: Множество ссылок на метки.
    """

    def __init__(self) -> None:
        """Инициализирует валидатор."""
        self.defined_labels: dict[str, BaseNode] = {}
        self.referenced_labels: set[str] = set()

    def collect_from_document(self, doc: Document) -> None:
        """Собирает все метки и ссылки из IR документа.

        Рекурсивно обходит дерево документа и собирает:
        - Метки из узлов с атрибутом label
        - Ссылки из узлов CrossReference и CrossRefNode

        Args:
            doc: IR документ для анализа.
        """
        self.defined_labels.clear()
        self.referenced_labels.clear()

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

            # Собираем ссылки
            if isinstance(node, (CrossReference, CrossRefNode)):
                self.referenced_labels.add(node.target_label)

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

    def validate(self) -> ValidationResult:
        """Выполняет bidirectional валидацию ссылок и меток.

        Находит:
        - Неопределённые ссылки: ссылки, которые не имеют определения
        - Неиспользуемые метки: метки, на которые нет ссылок

        Returns:
            ValidationResult с результатами валидации.
        """
        undefined_refs = self.referenced_labels - self.defined_labels.keys()
        unreferenced_labels = self.defined_labels.keys() - self.referenced_labels

        result = ValidationResult(
            undefined_refs=undefined_refs,
            unreferenced_labels=unreferenced_labels,
        )

        # Логируем результаты
        if result.has_errors:
            for ref in sorted(result.undefined_refs):
                logger.warning(f"Undefined reference: @{ref}")

        if result.has_warnings:
            for label in sorted(result.unreferenced_labels):
                logger.info(f"Unreferenced label: <{label}>")

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
        """
        total_labels = len(self.defined_labels)
        referenced_count = len(self.defined_labels.keys() & self.referenced_labels)
        unreferenced_count = len(self.defined_labels.keys() - self.referenced_labels)

        total_refs = len(self.referenced_labels)
        defined_count = len(self.referenced_labels & self.defined_labels.keys())
        undefined_count = len(self.referenced_labels - self.defined_labels.keys())

        return {
            "total_labels": total_labels,
            "referenced_count": referenced_count,
            "unreferenced_count": unreferenced_count,
            "total_refs": total_refs,
            "defined_count": defined_count,
            "undefined_count": undefined_count,
        }


__all__ = ["ReferenceValidator"]
