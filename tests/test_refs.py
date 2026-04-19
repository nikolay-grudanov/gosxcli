"""Tests for labels and references."""

from typst_gost_docx.parser.labels import LabelExtractor
from typst_gost_docx.parser.refs import RefResolver
from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2


def test_label_extraction():
    text = """
This is a paragraph with a label <fig:results>.

Another label <table:data>.
"""
    extractor = LabelExtractor("test.typ")
    nodes = extractor.extract_labels_and_refs(text)

    labels = [n for n in nodes if n.node_type == "bookmark"]
    assert len(labels) == 2
    assert labels[0].name == "fig:results"
    assert labels[1].name == "table:data"


def test_ref_extraction():
    text = """
As shown in @fig:results and @table:data, the system works.

See also @equation:energy.
"""
    extractor = LabelExtractor("test.typ")
    nodes = extractor.extract_labels_and_refs(text)

    refs = [n for n in nodes if n.node_type == "cross_reference"]
    assert len(refs) == 3
    assert refs[0].target_label == "fig:results"
    assert refs[1].target_label == "table:data"
    assert refs[2].target_label == "equation:energy"


def test_ref_resolution():
    text = """Some text @fig:results here."""

    label_extractor = LabelExtractor("test.typ")
    label_extractor.extract_labels_and_refs(text)

    ref_resolver = RefResolver(label_extractor.get_cross_ref_map())

    test_nodes = [
        n for n in label_extractor.extract_labels_and_refs(text) if n.node_type == "cross_reference"
    ]

    warnings = ref_resolver.resolve_refs(test_nodes)

    assert len(warnings) == 1
    assert "Unresolved reference" in warnings[0]


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
