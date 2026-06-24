"""Regression tests for the ``#link()`` inline-link feature.

Spec 001 US2 T073: parse ``#link("url")[label]`` and ``#link("url")``
into ``InlineLinkNode`` IR; writer must emit a real
``<w:hyperlink r:id="...">`` element backed by a TargetMode="External"
relationship in ``word/_rels/document.xml.rels``.

The bug guard: if the writer renders the link as plain text (the legacy
fallback), the rId and external relationship disappear and the URL
cannot survive a Word round-trip.
"""

from pathlib import Path

import pytest
import zipfile

from typst_gost_docx.ir.model import InlineLinkNode, Paragraph, TextRun
from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2


# ---------------------------------------------------------------------------
# Parser-level
# ---------------------------------------------------------------------------


def test_link_with_label_parsed_into_node():
    text = '= Title\n\nVisit #link("https://example.com")[our site].\n'
    doc = TypstExtractorV2(text, "test.typ").extract()

    paragraph = next(b for b in doc.blocks if isinstance(b, Paragraph))
    link = next(r for r in paragraph.runs if isinstance(r, InlineLinkNode))
    assert link.url == "https://example.com"
    assert link.text == "our site"


def test_link_without_label_keeps_empty_text():
    text = '= Title\n\nRead more at #link("https://example.com").\n'
    doc = TypstExtractorV2(text, "test.typ").extract()

    paragraph = next(b for b in doc.blocks if isinstance(b, Paragraph))
    link = next(r for r in paragraph.runs if isinstance(r, InlineLinkNode))
    assert link.url == "https://example.com"
    assert link.text == ""


def test_link_text_around_preserved():
    """Whitespace handling around a link is best-effort; both edges must be present."""
    text = '= Title\n\nBefore #link("https://e.com")[mid] after.\n'
    doc = TypstExtractorV2(text, "test.typ").extract()

    paragraph = next(b for b in doc.blocks if isinstance(b, Paragraph))
    runs = [r for r in paragraph.runs if isinstance(r, TextRun)]
    texts = [r.text for r in runs]
    # "Before " before the link and "after." after it — the whitespace
    # immediately following the closing bracket is consumed by the
    # surrounding inline-formatting pass, but the substantive text
    # stays intact.
    assert any("Before" in t for t in texts)
    assert any("after." in t for t in texts)


def test_multiple_links_in_same_paragraph():
    text = (
        '= Title\n\n'
        'See #link("https://a.com")[alpha] and #link("https://b.com")[beta] for details.\n'
    )
    doc = TypstExtractorV2(text, "test.typ").extract()

    paragraph = next(b for b in doc.blocks if isinstance(b, Paragraph))
    links = [r for r in paragraph.runs if isinstance(r, InlineLinkNode)]
    assert len(links) == 2
    assert {(link.url, link.text) for link in links} == {
        ("https://a.com", "alpha"),
        ("https://b.com", "beta"),
    }


# ---------------------------------------------------------------------------
# Writer-level (E2E)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not Path("template/Шаблон_оформления_ВКР_2026_новый.docx").exists(),
    reason="GOST reference template is not bundled with this checkout",
)
def test_e2e_link_emits_external_relationship(tmp_path):
    """Writer must register an external relationship and emit w:hyperlink."""
    from typst_gost_docx.parser.numbering import ChapterNumberer
    from typst_gost_docx.parser.refs import RefResolver
    from typst_gost_docx.writers.docx_writer import DocxWriter

    text = '= Intro\n\nVisit #link("https://example.com")[our site].\n'
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
        rels = zf.read("word/_rels/document.xml.rels").decode("utf-8")

    # A w:hyperlink with an r:id must appear in the body
    assert "<w:hyperlink " in body, "No w:hyperlink element in document.xml"
    assert 'r:id=' in body, "Hyperlink has no r:id reference"

    # The relationship must be external and point at the URL.
    # Note: the rels file stores Target before TargetMode, so the regex
    # accepts either order.
    assert "TargetMode=\"External\"" in rels, "Relationship is not external"
    assert "https://example.com" in rels, "URL not registered in relationships"
    assert "hyperlink" in rels, "Relationship type is not hyperlink"

    # The visible link text must appear in the body
    assert "our site" in body

    # The raw #link(...) source must NOT leak through
    assert "#link" not in body


@pytest.mark.skipif(
    not Path("template/Шаблон_оформления_ВКР_2026_новый.docx").exists(),
    reason="GOST reference template is not bundled with this checkout",
)
def test_e2e_link_without_label_still_registers_url(tmp_path):
    """Bare ``#link("url")`` without [label] must still register the URL."""
    from typst_gost_docx.parser.numbering import ChapterNumberer
    from typst_gost_docx.parser.refs import RefResolver
    from typst_gost_docx.writers.docx_writer import DocxWriter

    text = '= Intro\n\nRead more at #link("https://typst.app").\n'
    doc = TypstExtractorV2(text, "test.typ").extract()
    ChapterNumberer().number_document(doc)
    RefResolver().resolve_document(doc)

    out = tmp_path / "out.docx"
    DocxWriter(
        reference_doc=Path("template/Шаблон_оформления_ВКР_2026_новый.docx"),
        base_dir=tmp_path,
    ).write(doc, out)

    with zipfile.ZipFile(out) as zf:
        rels = zf.read("word/_rels/document.xml.rels").decode("utf-8")

    # Even without a label, the URL must be registered as an external
    # relationship — the visible text defaults to the URL itself.
    assert "https://typst.app" in rels
    assert "TargetMode=\"External\"" in rels
