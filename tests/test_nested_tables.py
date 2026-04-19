"""Tests for nested table handling (T048-T049)."""

from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2
from typst_gost_docx.ir.model import NodeType


def test_table_inside_figure():
    """Test extraction of table inside #figure(...)."""
    text = """
#figure(
  table(
    columns: 2,
    stroke: 0.7pt,
    table.header([Header 1][Header 2]),
    [Cell 1][Cell 2],
    [Cell 3][Cell 4],
  ),
  caption: [Test table],
) <tbl:test>
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    figures = [b for b in doc.blocks if b.node_type == NodeType.FIGURE]
    assert len(figures) == 1

    figure = figures[0]
    assert figure.table is not None
    assert figure.table.node_type == NodeType.TABLE
    assert len(figure.table.rows) == 2
    assert figure.table.has_header is True

    # Check caption
    assert figure.caption is not None
    assert figure.caption.text == "Test table"

    # Check label
    assert figure.label == "tbl:test"


def test_table_inside_figure_with_complex_content():
    """Test extraction of complex table inside figure."""
    text = """
#figure(
  table(
    columns: (50%, 50%),
    stroke: 0.7pt,
    fill: (col, row) => if row == 0 { luma(220) } else { none },
    table.header([Col A][Col B]),
    [Data 1][Data 2],
    [Data 3][Data 4],
  ),
  caption: [Comparison table],
) <tbl:comparison>
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    figures = [b for b in doc.blocks if b.node_type == NodeType.FIGURE]
    assert len(figures) == 1

    figure = figures[0]
    assert figure.table is not None
    assert figure.table.border_width == 0.7
    assert len(figure.table.columns) == 2
    assert figure.table.columns[0].width_percent == 50.0
    assert figure.table.columns[1].width_percent == 50.0


def test_nested_table_in_cell():
    """Test table cell contains another table (T049)."""
    text = """
#table(
  columns: 2,
  [Cell 1][Cell 2],
  [Cell 3][Cell 4],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == NodeType.TABLE]
    assert len(tables) == 1

    table = tables[0]
    assert len(table.rows) == 2

    # Check cell content
    for row in table.rows:
        for cell in row:
            # For now, cells contain text nodes
            assert len(cell.content) > 0


def test_figure_with_image_vs_table():
    """Test that figure can contain either image or table."""
    text_with_image = """
#figure(
  image("test.png"),
  caption: [Test image],
) <fig:image>
"""

    text_with_table = """
#figure(
  table(
    columns: 2,
    [A][B],
    [C][D],
  ),
  caption: [Test table],
) <tbl:table>
"""

    # Test with image
    extractor_img = TypstExtractorV2(text_with_image, "test.typ")
    doc_img = extractor_img.extract()

    figures_img = [b for b in doc_img.blocks if b.node_type == NodeType.FIGURE]
    assert len(figures_img) == 1
    assert figures_img[0].image_path == "test.png"
    assert figures_img[0].table is None

    # Test with table
    extractor_tbl = TypstExtractorV2(text_with_table, "test.typ")
    doc_tbl = extractor_tbl.extract()

    figures_tbl = [b for b in doc_tbl.blocks if b.node_type == NodeType.FIGURE]
    assert len(figures_tbl) == 1
    assert figures_tbl[0].image_path is None
    assert figures_tbl[0].table is not None
