"""Test state-machine based extractor."""

from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2


def test_extractor_v2_basic():
    """Test basic extraction with state-machine parser."""
    text = """= Heading 1

This is a paragraph with a @fig-test reference.

- Item 1
- Item 2

#figure(
  image("test.png"),
  caption: [Test caption],
) <fig-test>

$$
x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}
$$ <eq-test>
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    assert doc.node_type == "document"
    assert len(doc.blocks) > 0

    # Check heading
    sections = [b for b in doc.blocks if b.node_type == "section"]
    assert len(sections) == 1
    assert sections[0].level == 1

    # Check paragraph with reference
    paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
    assert len(paragraphs) == 1

    # Check if paragraph contains CrossReference
    para_content = paragraphs[0].content
    has_ref = any(
        hasattr(node, "node_type") and node.node_type == "cross_reference" for node in para_content
    )
    assert has_ref, "Paragraph should contain CrossReference"

    # Check list
    lists = [b for b in doc.blocks if b.node_type == "list_block"]
    assert len(lists) == 1
    assert len(lists[0].items) == 2

    # Check figure
    figures = [b for b in doc.blocks if b.node_type == "figure"]
    assert len(figures) == 1
    assert figures[0].label == "fig-test"
    assert figures[0].caption is not None

    # Check equation
    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) == 1
    assert equations[0].label == "eq-test"


def test_extractor_v2_table():
    """Test table extraction."""
    text = """#table(
  columns: 2,
  table.header([Header 1][Header 2]),
  [Cell 1][Cell 2],
  [Cell 3][Cell 4],
) <tbl-test>
"""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    assert doc.node_type == "document"

    tables = [b for b in doc.blocks if b.node_type == "table"]
    assert len(tables) == 1

    table = tables[0]
    assert table.label == "tbl-test"
    assert table.has_header
    assert len(table.rows) == 2

    # Check header row
    header_row = table.rows[0]
    assert len(header_row.cells) == 2

    # Check data row
    data_row = table.rows[1]
    assert len(data_row.cells) == 2


def test_extractor_v2_multiple_references():
    """Test multiple inline references in paragraph."""
    text = """See @fig-1, @tbl-2, and @eq-3 for details."""
    extractor = TypstExtractorV2(text, "test.typ")
    doc = extractor.extract()

    paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
    assert len(paragraphs) == 1

    para = paragraphs[0]
    refs = [
        node
        for node in para.content
        if hasattr(node, "node_type") and node.node_type == "cross_reference"
    ]
    assert len(refs) == 3

    assert refs[0].target_label == "@fig-1"
    assert refs[1].target_label == "@tbl-2"
    assert refs[2].target_label == "@eq-3"


if __name__ == "__main__":
    test_extractor_v2_basic()
    test_extractor_v2_table()
    test_extractor_v2_multiple_references()
    print("All tests passed!")
