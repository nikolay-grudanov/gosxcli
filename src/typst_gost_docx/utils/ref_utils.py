"""Reference utility functions."""

from __future__ import annotations


def infer_ref_kind(label: str) -> str | None:
    """Определяет тип ссылки по префиксу метки.

    Args:
        label: Метка ссылки (например, "fig:results", "tbl:data").

    Returns:
        Тип ссылки ("fig", "tbl", "eq", "ch") или None.
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
