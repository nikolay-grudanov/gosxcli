"""Tables manager for handling table creation."""

from docx import Document
from ..ir.model import Table as IRTable


class TablesManager:
    def __init__(self):
        self.table_counter = 0

    def add_table(self, doc: Document, table: IRTable) -> None:
        self.table_counter += 1

        if not table.rows:
            return

        num_rows = len(table.rows)
        num_cols = len(table.rows[0].cells) if table.rows else 1

        word_table = doc.add_table(rows=num_rows, cols=num_cols)
        word_table.style = "Table Grid"

        for row_idx, table_row in enumerate(table.rows):
            for col_idx, cell in enumerate(table_row.cells):
                cell_text = self._cell_content_to_text(cell.content)
                word_cell = word_table.rows[row_idx].cells[col_idx]
                word_cell.text = cell_text

    def _cell_content_to_text(self, nodes: list) -> str:
        text_parts = []
        for node in nodes:
            if hasattr(node, "text"):
                text_parts.append(node.text)
            elif hasattr(node, "content"):
                text_parts.append(self._cell_content_to_text(node.content))
        return "".join(text_parts)
