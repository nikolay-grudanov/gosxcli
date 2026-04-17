"""Resolve references."""

from typing import Optional
from ..ir.model import (
    BaseNode,
    CrossReference,
    CrossRefMap,
)


class RefResolver:
    def __init__(self, cross_ref_map: CrossRefMap):
        self.cross_ref_map = cross_ref_map

    def resolve_refs(self, nodes: list[BaseNode]) -> list[str]:
        warnings = []

        for node in nodes:
            if isinstance(node, CrossReference):
                target = self.cross_ref_map.resolve(node.target_label)
                if target is None:
                    warnings.append(f"Unresolved reference: @{node.target_label}")

        return warnings
