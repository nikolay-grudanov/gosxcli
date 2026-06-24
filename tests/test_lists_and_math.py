"""Regression tests for list rendering, inline math parsing, and block
equation stripping.

Each of these was a "looks fine, renders blank or unstyled" bug:

* Lists had no markers because the writer forgot to attach ``numPr``.
* Inline math ``$x$`` was emitted as plain text because the parser did
  not extract it into an ``InlineMathNode``.
* Block math captured leading and trailing newlines into the latex
  source, which then confused latex2mathml.

The tests below guard against silent regressions.
"""

from pathlib import Path

import pytest
import zipfile

from typst_gost_docx.ir.model import (
    Equation,
    InlineMathNode,
    ListBlock,
    ListKind,
    Paragraph,
    TextRun,
)
from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2


# ---------------------------------------------------------------------------
# Lists — unit-level on the parser
# ---------------------------------------------------------------------------


def test_list_block_kind_is_bullet():
    text = "= Title\n\n- One\n- Two\n- Three\n"
    doc = TypstExtractorV2(text, "test.typ").extract()

    lists = [b for b in doc.blocks if isinstance(b, ListBlock)]
    assert len(lists) == 1
    assert lists[0].kind == ListKind.BULLET
    assert [self_text(r) for r in lists[0].items[0].content] == ["One"]


def test_list_block_kind_is_numbered():
    text = "= Title\n\n1. First\n2. Second\n"
    doc = TypstExtractorV2(text, "test.typ").extract()

    lists = [b for b in doc.blocks if isinstance(b, ListBlock)]
    assert len(lists) == 1
    assert lists[0].kind == ListKind.NUMBERED
    assert len(lists[0].items) == 2


# ---------------------------------------------------------------------------
# Inline math — parser must emit InlineMathNode
# ---------------------------------------------------------------------------


def test_inline_math_parsed_into_node():
    text = "= Intro\n\nEnergy: $E = m c^2$ is famous.\n"
    doc = TypstExtractorV2(text, "test.typ").extract()

    math_nodes: list[InlineMathNode] = []
    for b in doc.blocks:
        if isinstance(b, Paragraph):
            for r in b.runs:
                if isinstance(r, InlineMathNode):
                    math_nodes.append(r)
    assert len(math_nodes) == 1
    assert math_nodes[0].latex == "E = m c^2"


def test_inline_math_with_surrounding_text():
    text = "= Intro\n\nLet $x$ be the variable.\n"
    doc = TypstExtractorV2(text, "test.typ").extract()

    paragraph = next(b for b in doc.blocks if isinstance(b, Paragraph))
    text_before = paragraph.runs[0]
    math = paragraph.runs[1]
    text_after = paragraph.runs[2]

    assert isinstance(text_before, TextRun)
    assert text_before.text.startswith("Let ")
    assert isinstance(math, InlineMathNode)
    assert math.latex == "x"
    assert isinstance(text_after, TextRun)
    assert text_after.text.startswith(" be the variable")


# ---------------------------------------------------------------------------
# Block equation — no stray whitespace
# ---------------------------------------------------------------------------


def test_block_equation_latex_is_stripped():
    text = "= Intro\n\n$$\nx = y\n$$\n"
    doc = TypstExtractorV2(text, "test.typ").extract()

    equations = [b for b in doc.blocks if isinstance(b, Equation)]
    assert len(equations) == 1
    assert equations[0].latex == "x = y"
    assert "\n" not in equations[0].latex


# ---------------------------------------------------------------------------
# End-to-end: lists + math render through the full pipeline
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not Path("template/Шаблон_оформления_ВКР_2026_новый.docx").exists(),
    reason="GOST reference template is not bundled with this checkout",
)
def test_e2e_list_renders_with_numbering(tmp_path):
    """The output .docx must contain numPr so Word/LO shows bullet/number marks."""
    from typst_gost_docx.parser.numbering import ChapterNumberer
    from typst_gost_docx.parser.refs import RefResolver
    from typst_gost_docx.writers.docx_writer import DocxWriter

    text = "= Intro\n\n- Alpha\n- Beta\n\n1. One\n2. Two\n"

    doc = TypstExtractorV2(text, "test.typ").extract()
    ChapterNumberer().number_document(doc)
    RefResolver().resolve_document(doc)

    out = tmp_path / "out.docx"
    DocxWriter(
        reference_doc=Path("template/Шаблон_оформления_ВКР_2026_новый.docx"),
        base_dir=tmp_path,
    ).write(doc, out)

    with zipfile.ZipFile(out) as zf:
        body = zf.read("word/document.xml").decode("utf-8")
        numbering = zf.read("word/numbering.xml").decode("utf-8")

    # numPr must appear in document.xml for every list item.
    assert body.count("<w:numPr>") >= 4, (
        f"Expected at least 4 numPr elements (3 bullet items + 2 numbered, "
        f"but at minimum 4), got {body.count('<w:numPr>')}"
    )
    # numbering.xml must declare a bullet and a decimal abstractNum.
    assert 'w:numFmt w:val="bullet"' in numbering, "Bullet numbering definition missing"
    assert 'w:numFmt w:val="decimal"' in numbering, "Decimal numbering definition missing"


@pytest.mark.skipif(
    not Path("template/Шаблон_оформления_ВКР_2026_новый.docx").exists(),
    reason="GOST reference template is not bundled with this checkout",
)
def test_e2e_inline_math_renders_as_omml(tmp_path):
    """$x$ must end up as an <m:oMath> element in word/document.xml."""
    from typst_gost_docx.parser.numbering import ChapterNumberer
    from typst_gost_docx.parser.refs import RefResolver
    from typst_gost_docx.writers.docx_writer import DocxWriter

    text = "= Intro\n\nThe famous $E = m c^2$ equation.\n"

    doc = TypstExtractorV2(text, "test.typ").extract()
    ChapterNumberer().number_document(doc)
    RefResolver().resolve_document(doc)

    out = tmp_path / "out.docx"
    DocxWriter(
        reference_doc=Path("template/Шаблон_оформления_ВКР_2026_новый.docx"),
        base_dir=tmp_path,
    ).write(doc, out)

    with zipfile.ZipFile(out) as zf:
        body = zf.read("word/document.xml").decode("utf-8")

    # OMML namespace + oMath element means the inline math reached the
    # writer and was rendered as a real Office Math expression.
    assert "<m:oMath" in body, "Inline math was not rendered as OMML"
    # The plain ``$E = m c^2$`` text must NOT leak through.
    assert "$E = m c^2$" not in body, "Raw $...$ text leaked into document body"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def self_text(run) -> str:
    """Return the text of a TextRun or empty string for other node types."""
    return getattr(run, "text", "") or ""
