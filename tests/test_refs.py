"""Tests for labels and references.

Migrated from a flat regex-based ``LabelExtractor`` to the canonical
``TypstExtractorV2`` + ``RefResolver`` pipeline. The flat extractor
was retired along with ``parser/labels.py`` (see v0.5.0 cleanup) and
its tests now go through the same code path the CLI uses.
"""

from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2
from typst_gost_docx.parser.numbering import ChapterNumberer
from typst_gost_docx.parser.refs import RefResolver


def _parse_number_resolve(text: str):
    """Run extract → number → resolve so tests don't repeat the boilerplate."""
    doc = TypstExtractorV2(text, "test.typ").extract()
    ChapterNumberer().number_document(doc)
    RefResolver().resolve_document(doc)
    return doc


def test_label_in_document_is_collected():
    """A labeled node (``<fig:results>``) must appear in the IR."""
    text = """
= Intro

Some paragraph.

#figure(image("plot.png"), caption: [Results]) <fig:results>
"""
    doc = TypstExtractorV2(text, "test.typ").extract()

    figures = [b for b in doc.blocks if b.node_type == "figure"]
    assert len(figures) == 1
    assert figures[0].label == "fig:results"


def test_multiple_labels_in_document():
    """Several labeled nodes must each carry their own label."""
    text = """
= Intro

#figure(image("a.png"), caption: [A]) <fig:a>
#figure(image("b.png"), caption: [B]) <fig:b>
"""
    doc = TypstExtractorV2(text, "test.typ").extract()

    figures = [b for b in doc.blocks if b.node_type == "figure"]
    labels = sorted(f.label for f in figures)
    assert labels == ["fig:a", "fig:b"]


def test_unresolved_reference_is_reported():
    """An ``@fig:missing`` reference with no corresponding label must be reported."""
    text = """
= Intro

As shown in @fig:missing, the system works.
"""
    doc = _parse_number_resolve(text)

    warnings = RefResolver().resolve_document(doc)
    assert len(warnings) == 1
    assert "@fig:missing" in warnings[0]


def test_resolved_reference_carries_ref_text():
    """When the target exists, the resolver fills ``ref_text`` with the visible string."""
    text = """
= Intro

#figure(image("plot.png"), caption: [Results]) <fig:results>

As shown in @fig:results.
"""
    doc = _parse_number_resolve(text)

    # Find the inline CrossReference
    for block in doc.blocks:
        if hasattr(block, "runs"):
            for run in block.runs:
                if getattr(run, "target_label", None) == "fig:results":
                    assert run.ref_text == "Рис. 1.1"
                    return
    raise AssertionError("CrossReference to fig:results not found in IR")


def test_figure_with_label():
    text = """
#figure(
  image("plot.png"),
  caption: [Results],
) <fig:results>
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    figures = [b for b in doc.blocks if b.node_type == "figure"]
    assert len(figures) == 1
    assert figures[0].caption is not None


def test_table_with_label():
    text = """
#table(
  columns: 2,
  table.header([A][B]),
  [1][2],
) <table:data>
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1
