"""Tests for real VKR document conversion."""

from pathlib import Path
from typst_gost_docx.ingest.project_loader import TypstProjectLoader
from typst_gost_docx.parser.scanner import TypstScanner
from typst_gost_docx.parser.extractor import TypstExtractor
from typst_gost_docx.parser.labels import LabelExtractor


def test_vvedenie_headings():
    """Test heading extraction from real VKR introduction."""
    vvedenie_path = Path("fixtures/real_vkr/main_doc/chapters/00-vvedenie.typ")
    loader = TypstProjectLoader(vvedenie_path)
    files = loader.load()

    scanner = TypstScanner(files[str(vvedenie_path)])
    extractor = TypstExtractor(scanner, str(vvedenie_path))
    doc = extractor.extract()

    sections = [b for b in doc.blocks if b.node_type == "section"]
    assert len(sections) >= 1
    assert sections[0].level == 1


def test_vvedenie_references():
    """Test reference extraction from real VKR introduction."""
    vvedenie_path = Path("fixtures/real_vkr/main_doc/chapters/00-vvedenie.typ")
    loader = TypstProjectLoader(vvedenie_path)
    files = loader.load()

    label_extractor = LabelExtractor(str(vvedenie_path))
    nodes = label_extractor.extract_labels_and_refs(files[str(vvedenie_path)])

    refs = [n for n in nodes if n.node_type == "cross_reference"]
    assert len(refs) > 10


def test_literature_review_headings():
    """Test heading extraction from literature review."""
    lit_review_path = Path("fixtures/real_vkr/main_doc/chapters/01-literature-review.typ")
    loader = TypstProjectLoader(lit_review_path)
    files = loader.load()

    scanner = TypstScanner(files[str(lit_review_path)])
    extractor = TypstExtractor(scanner, str(lit_review_path))
    doc = extractor.extract()

    sections = [b for b in doc.blocks if b.node_type == "section"]
    assert len(sections) >= 3


def test_literature_review_tables():
    """Test table extraction from literature review."""
    lit_review_path = Path("fixtures/real_vkr/main_doc/chapters/01-literature-review.typ")
    loader = TypstProjectLoader(lit_review_path)
    files = loader.load()

    scanner = TypstScanner(files[str(lit_review_path)])
    extractor = TypstExtractor(scanner, str(lit_review_path))
    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) >= 1


def test_literature_review_figures():
    """Test figure extraction from literature review."""
    lit_review_path = Path("fixtures/real_vkr/main_doc/chapters/01-literature-review.typ")
    loader = TypstProjectLoader(lit_review_path)
    files = loader.load()

    scanner = TypstScanner(files[str(lit_review_path)])
    extractor = TypstExtractor(scanner, str(lit_review_path))
    doc = extractor.extract()

    figures = [b for b in doc.blocks if b.node_type == "figure"]
    assert len(figures) >= 2


def test_literature_review_labels():
    """Test label extraction from literature review."""
    lit_review_path = Path("fixtures/real_vkr/main_doc/chapters/01-literature-review.typ")
    loader = TypstProjectLoader(lit_review_path)
    files = loader.load()

    label_extractor = LabelExtractor(str(lit_review_path))
    nodes = label_extractor.extract_labels_and_refs(files[str(lit_review_path)])

    labels = [n for n in nodes if n.node_type == "bookmark"]
    assert len(labels) >= 2


def test_paragraphs_extraction():
    """Test paragraph extraction from real VKR."""
    vvedenie_path = Path("fixtures/real_vkr/main_doc/chapters/00-vvedenie.typ")
    loader = TypstProjectLoader(vvedenie_path)
    files = loader.load()

    scanner = TypstScanner(files[str(vvedenie_path)])
    extractor = TypstExtractor(scanner, str(vvedenie_path))
    doc = extractor.extract()

    paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
    assert len(paragraphs) >= 10


def test_complex_typst_patterns():
    """Test complex patterns from real VKR."""
    lit_review_path = Path("fixtures/real_vkr/main_doc/chapters/01-literature-review.typ")
    loader = TypstProjectLoader(lit_review_path)
    files = loader.load()

    text = files[str(lit_review_path)]

    scanner = TypstScanner(text)
    tokens = list(scanner.scan())

    token_types = [t.type for t in tokens]
    assert "HEADING" in token_types
    assert "REF" in token_types
    assert "TABLE_START" in token_types
    assert "FIGURE_START" in token_types
