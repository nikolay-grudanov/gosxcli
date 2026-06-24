"""Regression tests for cross-reference resolution pipeline.

These tests guard the architecture established in the v0.4.x refactor:
a single canonical ``CrossReference`` IR node, an early resolver pass in
the CLI pipeline, and a thin writer that consumes pre-resolved text.

If someone re-introduces the bug where the writer silently renders the
raw ``@fig:foo`` label instead of "Рис. 1.1", these tests fail.
"""

from pathlib import Path

import pytest

from typst_gost_docx.ir.model import CrossReference
from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2
from typst_gost_docx.parser.numbering import ChapterNumberer
from typst_gost_docx.parser.refs import RefResolver


# ---------------------------------------------------------------------------
# Resolver unit tests
# ---------------------------------------------------------------------------


def _parse_number_resolve(text: str):
    """Run parse → number → resolve so tests don't repeat the boilerplate."""
    doc = TypstExtractorV2(text, "test.typ").extract()
    ChapterNumberer().number_document(doc)
    RefResolver().resolve_document(doc)
    return doc


def test_resolver_fills_ref_text_for_figure():
    """The resolver must produce 'Рис. 1.1' for a figure referenced inline."""
    text = (
        "= Intro\n"
        "\n"
        "#figure(\n"
        "  image(\"plot.png\"),\n"
        "  caption: [Results],\n"
        ") <fig:results>\n"
        "\n"
        "See @fig:results for details.\n"
    )
    doc = _parse_number_resolve(text)

    refs = [n for n in _walk(doc) if isinstance(n, CrossReference)]
    assert len(refs) == 1
    ref = refs[0]
    assert ref.target_label == "fig:results"
    assert ref.ref_kind == "fig"
    assert ref.number == 1
    assert ref.chapter_number == 1
    assert ref.ref_text == "Рис. 1.1"


def test_resolver_handles_unresolved_reference():
    """An unresolved @label must produce a warning and leave ref_text empty."""
    text = "= Intro\n\nReferences @fig:missing but no such figure exists.\n"
    doc = TypstExtractorV2(text, "test.typ").extract()
    ChapterNumberer().number_document(doc)
    warnings = RefResolver().resolve_document(doc)

    assert len(warnings) == 1
    assert "@fig:missing" in warnings[0]


def test_resolver_handles_table_label():
    """A `@tbl:foo` reference must produce 'Табл. X.Y'."""
    text = (
        "= Intro\n"
        "\n"
        "#table(\n"
        "  columns: 2,\n"
        "  [A][B],\n"
        "  [1][2],\n"
        ") <tbl:data>\n"
        "\n"
        "Numbers in @tbl:data.\n"
    )
    doc = _parse_number_resolve(text)

    refs = [n for n in _walk(doc) if isinstance(n, CrossReference)]
    assert refs[0].ref_text == "Табл. 1.1"


def test_resolver_handles_equation_label():
    text = (
        "= Intro\n"
        "\n"
        "$$\n"
        "E = m c^2\n"
        "$$ <eq:energy>\n"
        "\n"
        "Using @eq:energy here.\n"
    )
    doc = _parse_number_resolve(text)

    refs = [n for n in _walk(doc) if isinstance(n, CrossReference)]
    assert refs[0].ref_text == "Формула 1.1"


def test_resolver_increments_chapter_local_counter():
    """Two figures in the same chapter should yield 1.1 and 1.2."""
    text = (
        "= Chapter\n"
        "\n"
        "#figure(image(\"a.png\"), caption: [A]) <fig:a>\n"
        "\n"
        "#figure(image(\"b.png\"), caption: [B]) <fig:b>\n"
        "\n"
        "See @fig:a and @fig:b.\n"
    )
    doc = _parse_number_resolve(text)

    refs = [n for n in _walk(doc) if isinstance(n, CrossReference)]
    ref_texts = sorted(r.ref_text or "" for r in refs)
    assert ref_texts == ["Рис. 1.1", "Рис. 1.2"]


# ---------------------------------------------------------------------------
# End-to-end: parse + number + resolve + writer actually produces "Рис. X.Y"
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not Path("template/Шаблон_оформления_ВКР_2026_новый.docx").exists(),
    reason="GOST reference template is not bundled with this checkout",
)
def test_e2e_writer_renders_figure_label(tmp_path):
    """Full pipeline: parse → number → resolve → write → assert hyperlink text."""
    from typst_gost_docx.writers.docx_writer import DocxWriter

    text = (
        "#show: doc => page(padding: 2cm, doc)\n"
        "\n"
        "= Intro\n"
        "\n"
        "#figure(image(\"assets/ums_panel.jpg\"), caption: [Panel]) <fig:panel>\n"
        "\n"
        "Reference: @fig:panel.\n"
    )

    src_image = Path("examples/assets/ums_panel.jpg")
    if not src_image.exists():
        pytest.skip("examples/assets/ums_panel.jpg not present")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "ums_panel.jpg").write_bytes(src_image.read_bytes())

    typ_file = tmp_path / "doc.typ"
    typ_file.write_text(text, encoding="utf-8")

    doc = TypstExtractorV2(text, str(typ_file)).extract()
    ChapterNumberer().number_document(doc)
    RefResolver().resolve_document(doc)

    out_docx = tmp_path / "out.docx"
    writer = DocxWriter(
        reference_doc=Path("template/Шаблон_оформления_ВКР_2026_новый.docx"),
        base_dir=tmp_path,
    )
    writer.write(doc, out_docx)

    # out.docx is a zip — read word/document.xml out of it.
    import zipfile

    with zipfile.ZipFile(out_docx) as zf:
        body_xml = zf.read("word/document.xml").decode("utf-8")

    # The writer must produce resolved visible text…
    assert "Рис. 1.1" in body_xml, (
        "Writer rendered raw label instead of resolved text. "
        "Check that ChapterNumberer + RefResolver are invoked in cli.py "
        "and that bookmarks are registered on figure captions."
    )
    # …and the raw label must NOT leak through as visible text.
    assert "fig:panel" not in body_xml, (
        "Raw label fig:panel appears in document body — resolver did not run"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _walk(node):
    """Yield every IR node nested under ``node`` (depth-first)."""
    yield node
    if hasattr(node, "blocks") and node.blocks:
        for b in node.blocks:
            yield from _walk(b)
    if hasattr(node, "runs") and node.runs:
        for r in node.runs:
            yield from _walk(r)
    if hasattr(node, "caption") and node.caption:
        yield from _walk(node.caption)
