"""Tests for table handling."""

from typst_gost_docx.parser.scanner import TypstScanner
from typst_gost_docx.parser.extractor import TypstExtractor


def test_basic_table():
    text = """
#table(
  columns: 2,
  [Cell 1][Cell 2],
  [Cell 3][Cell 4],
)
"""
    scanner = TypstScanner(text)
    extractor = TypstExtractor(scanner, "test.typ")

    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    assert len(tables[0].rows) == 2
    assert len(tables[0].rows[0].cells) == 2


def test_table_with_header():
    text = """
#table(
  columns: 2,
  table.header([Header 1][Header 2]),
  [Cell 1][Cell 2],
  [Cell 3][Cell 4],
)
"""
    scanner = TypstScanner(text)
    extractor = TypstExtractor(scanner, "test.typ")

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
    scanner = TypstScanner(text)
    extractor = TypstExtractor(scanner, "test.typ")

    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
    assert len(tables[0].rows[0].cells) == 3


def test_empty_table():
    text = """
#table(
  columns: 1,
)
"""
    scanner = TypstScanner(text)
    extractor = TypstExtractor(scanner, "test.typ")

    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
