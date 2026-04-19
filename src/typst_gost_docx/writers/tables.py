"""Tables manager for handling table creation."""

from docx import Document
from ..ir.model import TableNode as IRTable


class TablesManager:
    def __init__(self):
        self.table_counter = 0

    def add_table(self, doc: Document, table: IRTable) -> None:
        self.table_counter += 1

        if not table.rows and not table.header:
            return

        # Calculate number of columns
        num_cols = 0
        if table.header and table.header.cells:
            num_cols = len(table.header.cells)
        elif table.rows and table.rows[0]:
            num_cols = len(table.rows[0])

        if num_cols == 0:
            return

        # Calculate number of rows
        num_rows = 0
        if table.has_header and table.header:
            num_rows += 1
        num_rows += len(table.rows)

        word_table = doc.add_table(rows=num_rows, cols=num_cols)
        word_table.style = "Table Grid"

        # Write header row
        row_idx = 0
        if table.has_header and table.header:
            for col_idx, cell in enumerate(table.header.cells):
                cell_text = self._cell_content_to_text(cell.content)
                word_table.rows[row_idx].cells[col_idx].text = cell_text
            row_idx += 1

        # Write data rows
        for table_row in table.rows:
            for col_idx, cell in enumerate(table_row):
                if col_idx < num_cols:
                    cell_text = self._cell_content_to_text(cell.content)
                    word_table.rows[row_idx].cells[col_idx].text = cell_text
            row_idx += 1

    def _cell_content_to_text(self, nodes: list) -> str:
        text_parts = []
        for node in nodes:
            if hasattr(node, "text"):
                text_parts.append(node.text)
            elif hasattr(node, "code"):
                text_parts.append(node.code)
            elif hasattr(node, "content"):
                text_parts.append(self._cell_content_to_text(node.content))
        return "".join(text_parts)
