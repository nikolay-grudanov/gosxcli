"""Smoke tests for basic conversion."""

from pathlib import Path
import tempfile
from typst_gost_docx.ingest.project_loader import TypstProjectLoader
from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2
from typst_gost_docx.writers.docx_writer import DocxWriter


def test_minimal_document_load():
    text = """= Heading 1

This is a paragraph.
"""
    _loader = TypstProjectLoader(Path("test.typ"))
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    assert doc.node_type == "document"
    assert len(doc.blocks) >= 1


def test_headings_extraction():
    text = """= Heading 1
== Heading 2
=== Heading 3
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    sections = [b for b in doc.blocks if b.node_type == "section"]
    assert len(sections) == 3
    assert sections[0].level == 1
    assert sections[1].level == 2
    assert sections[2].level == 3


def test_paragraphs_extraction():
    text = """First paragraph.

Second paragraph.
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
    assert len(paragraphs) == 2


def test_list_extraction():
    text = """- First item
- Second item
- Third item
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    lists = [b for b in doc.blocks if b.node_type == "list_block"]
    assert len(lists) == 1
    assert lists[0].kind == "bullet"
    assert len(lists[0].items) == 3


def test_numbered_list_extraction():
    text = """1. First item
2. Second item
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    lists = [b for b in doc.blocks if b.node_type == "list_block"]
    assert len(lists) == 1
    assert lists[0].kind == "numbered"


def test_scanner_basic_tokens():
    from typst_gost_docx.parser.scanner import TypstScanner

    text = """= Heading

- Bullet
1. Numbered

$inline math$
$$block math$$
"""
    scanner = TypstScanner(text)
    tokens = list(scanner.scan())

    token_types = [t.type for t in tokens]
    assert "HEADING" in token_types
    assert "BULLET" in token_types
    assert "NUMBERED" in token_types
    assert "INLINE_MATH_DELIM" in token_types
    assert "BLOCK_MATH_DELIM" in token_types


def test_e2e_conversion():
    """End-to-end test of minimal document conversion."""
    text = """= Заголовок

Это параграф со ссылкой @fig-test.

#figure(
  image("test.png"),
  caption: [Тестовый рисунок],
) <fig-test>
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    assert doc.node_type == "document"
    assert len(doc.blocks) >= 1

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.docx"
        writer = DocxWriter()
        stats = writer.write(doc, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0
        assert stats["headings"] > 0
        assert stats["paragraphs"] > 0
        assert stats["figures"] > 0
