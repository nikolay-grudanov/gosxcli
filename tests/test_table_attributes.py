"""Tests for table attribute parsing (T034-T039)."""

from typing import cast

from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2
from typst_gost_docx.ir.model import TableNode


def test_columns_with_fraction() -> None:
    """Test parsing columns with fraction widths (T035)."""
    text = """
#table(
  columns: (1fr, 2fr, 1fr),
  [A][B][C],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    assert len(table.columns) == 3
    assert table.columns[0].width == 1.0
    assert table.columns[1].width == 2.0
    assert table.columns[2].width == 1.0


def test_columns_with_percentage() -> None:
    """Test parsing columns with percentage widths (T035)."""
    text = """
#table(
  columns: (17%, 83%),
  [A][B],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    assert len(table.columns) == 2
    assert table.columns[0].width_percent == 17.0
    assert table.columns[1].width_percent == 83.0


def test_columns_mixed() -> None:
    """Test parsing columns with mixed formats (T035)."""
    text = """
#table(
  columns: (auto, 1fr, 20%),
  [A][B][C],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    assert len(table.columns) == 3


def test_stroke_spec() -> None:
    """Test parsing stroke specification (T036)."""
    text = """
#table(
  stroke: 0.7pt,
  columns: 2,
  [A][B],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    assert table.border_width == 0.7


def test_stroke_mm() -> None:
    """Test parsing stroke in mm units (T036)."""
    text = """
#table(
  stroke: 1mm,
  columns: 2,
  [A][B],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    assert table.border_width == 1.0


def test_fill_lambda() -> None:
    """Test parsing fill lambda for header (T037)."""
    text = """
#table(
  fill: (col, row) => if row == 0 { luma(220) },
  table.header([H1][H2]),
  [A][B],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    assert table.header is not None
    assert len(table.header.cells) == 2
    # First header cell should have fill color
    assert table.header.cells[0].fill == "220"


def test_align_lambda() -> None:
    """Test parsing align lambda for header (T038)."""
    text = """
#table(
  align: (col, row) => if row == 0 { center },
  table.header([H1][H2]),
  [A][B],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    assert table.header is not None
    assert len(table.header.cells) == 2
    # First header cell should have alignment
    assert table.header.cells[0].align == "center"


def test_colspan() -> None:
    """Test parsing colspan attribute (T039)."""
    text = """
#table(
  columns: 2,
  table.cell(colspan: 2)[Cell spanning both],
  [C][D],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    # First row should have one cell with colspan=2
    assert len(table.rows[0]) == 1
    assert table.rows[0][0].colspan == 2
    # Second row should have two cells
    assert len(table.rows[1]) == 2


def test_rowspan() -> None:
    """Test parsing rowspan attribute (T039)."""
    text = """
#table(
  columns: 2,
  table.cell(rowspan: 2)[Tall],
  [B],
  [C],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    # First cell should have rowspan
    assert table.rows[0][0].rowspan == 2


def test_complex_table_all_attributes() -> None:
    """Test parsing a complex table with all attributes (T034-T039, T047)."""
    text = """
#table(
  columns: (1fr, 2fr),
  stroke: 0.7pt,
  fill: (col, row) => if row == 0 { luma(220) },
  align: (col, row) => if row == 0 { center },
  table.header([Parameter][Description]),
  [Alpha][First element],
  [Beta][Second element],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    # Check columns
    assert len(table.columns) == 2
    assert table.columns[0].width == 1.0
    assert table.columns[1].width == 2.0

    # Check stroke
    assert table.border_width == 0.7

    # Check header
    assert table.header is not None
    assert len(table.header.cells) == 2
    assert table.header.cells[0].fill == "220"
    assert table.header.cells[0].align == "center"

    # Check rows
    assert len(table.rows) == 2
    assert len(table.rows[0]) == 2
    assert len(table.rows[1]) == 2


def test_simple_columns_number() -> None:
    """Test parsing simple columns: N format (T035)."""
    text = """
#table(
  columns: 3,
  [A][B][C],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    assert len(table.columns) == 3
    # All columns should have default ColSpec
    for col in table.columns:
        assert col.width is None
        assert col.width_percent is None


def test_columns_with_alignment() -> None:
    """Test parsing columns with alignment keywords (T035)."""
    text = """
#table(
  columns: (left, center, right),
  [A][B][C],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [cast(TableNode, b) for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    table = tables[0]

    assert len(table.columns) == 3
    assert table.columns[0].align == "left"
    assert table.columns[1].align == "center"
    assert table.columns[2].align == "right"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
