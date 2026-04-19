"""Tests for table handling."""

from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2


def test_basic_table():
    text = """
#table(
  columns: 2,
  [Cell 1][Cell 2],
  [Cell 3][Cell 4],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    assert len(tables[0].rows) == 2
    assert len(tables[0].rows[0]) == 2


def test_table_with_header():
    text = """
#table(
  columns: 2,
  table.header([Header 1][Header 2]),
  [Cell 1][Cell 2],
  [Cell 3][Cell 4],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    assert tables[0].has_header is True


def test_table_single_row():
    text = """
#table(
  columns: 3,
  [A][B][C],
)
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    assert len(tables[0].rows[0]) == 3


def test_empty_table():
    text = """
#table(
  columns: 1,
)
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
