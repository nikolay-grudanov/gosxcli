"""Resolve references with chapter-aware numbering."""

from typing import Optional
from ..ir.model import (
    BaseNode,
    CrossReference,
    CrossRefMap,
    CrossRefNode,
    Figure,
    TableNode,
    Equation,
    Section,
)


class RefResolver:
    def __init__(self, cross_ref_map: CrossRefMap):
        self.cross_ref_map = cross_ref_map

    def resolve_refs(self, nodes: list[BaseNode]) -> list[str]:
        """Разрешает ссылки и заполняет ref_kind, number, chapter_number в CrossRefNode.

        Args:
            nodes: Список IR узлов для обработки ссылок.

        Returns:
            Список предупреждений о неразрешённых ссылках.
        """
        warnings = []

        for node in nodes:
            if isinstance(node, CrossReference):
                target = self.cross_ref_map.resolve(node.target_label)
                if target is None:
                    warnings.append(f"Unresolved reference: @{node.target_label}")
            elif isinstance(node, CrossRefNode):
                # Resolve reference and populate ref_kind, number, chapter_number
                self._resolve_cross_ref_node(node)
                target = self.cross_ref_map.resolve(node.target_label)
                if target is None:
                    warnings.append(f"Unresolved reference: @{node.target_label}")

        return warnings

    def _resolve_cross_ref_node(self, ref: CrossRefNode) -> None:
        """Заполняет ref_kind, number, chapter_number в CrossRefNode.

        Определяет тип ссылки по префиксу метки и извлекает номер из целевого узла.

        Args:
            ref: CrossRefNode для разрешения.
        """
        # Determine ref_kind from label prefix if not set
        if not ref.ref_kind:
            ref.ref_kind = self._infer_ref_kind(ref.target_label)

        # Resolve target node to get number and chapter_number
        target = self.cross_ref_map.resolve(ref.target_label)
        if target:
            if isinstance(target, Figure):
                ref.number = target.number
                ref.chapter_number = target.chapter_number
            elif isinstance(target, TableNode):
                ref.number = target.number
                ref.chapter_number = target.chapter_number
            elif isinstance(target, Equation):
                ref.number = target.number
                ref.chapter_number = target.chapter_number
            elif isinstance(target, Section):
                ref.number = target.number
                ref.chapter_number = target.chapter_number

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
