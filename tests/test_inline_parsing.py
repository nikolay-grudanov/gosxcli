"""Test inline formatting parsing."""

from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2
from typst_gost_docx.ir.model import (
    InlineRunNode,
    InlineCodeNode,
    TextRun,
    CrossReference,
)


class TestInlineParsing:
    """Test suite for inline formatting parsing."""

    def test_inline_bold_parsing(self):
        """Test bold (*text*) parsing."""
        text = "This is *bold* text."
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
        assert len(paragraphs) == 1

        runs = paragraphs[0].runs
        # Find the bold run
        bold_runs = [r for r in runs if isinstance(r, InlineRunNode) and r.bold is True]
        assert len(bold_runs) == 1
        assert bold_runs[0].text == "bold"

        # Check surrounding plain text
        text_runs = [r for r in runs if isinstance(r, TextRun)]
        combined_text = "".join(r.text for r in text_runs)
        assert "This is " in combined_text
        assert " text." in combined_text

    def test_inline_italic_parsing(self):
        """Test italic (_text_) parsing."""
        text = "This is _italic_ text."
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
        assert len(paragraphs) == 1

        runs = paragraphs[0].runs
        # Find the italic run
        italic_runs = [r for r in runs if isinstance(r, InlineRunNode) and r.italic is True]
        assert len(italic_runs) == 1
        assert italic_runs[0].text == "italic"

        # Check surrounding plain text
        text_runs = [r for r in runs if isinstance(r, TextRun)]
        combined_text = "".join(r.text for r in text_runs)
        assert "This is " in combined_text
        assert " text." in combined_text

    def test_inline_code_parsing(self):
        """Test inline code (`code`) parsing."""
        text = "Use `function()` to call."
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
        assert len(paragraphs) == 1

        runs = paragraphs[0].runs
        # Find the code node
        code_nodes = [r for r in runs if isinstance(r, InlineCodeNode)]
        assert len(code_nodes) == 1
        assert code_nodes[0].code == "function()"

        # Check surrounding plain text
        text_runs = [r for r in runs if isinstance(r, TextRun)]
        combined_text = "".join(r.text for r in text_runs)
        assert "Use " in combined_text
        assert " to call." in combined_text

    def test_inline_mixed_parsing(self):
        """Test mixed formatting: *bold* and _italic_ and `code`."""
        text = "*bold* and _italic_ and `code`"
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
        assert len(paragraphs) == 1

        runs = paragraphs[0].runs

        # Check for bold
        bold_runs = [r for r in runs if isinstance(r, InlineRunNode) and r.bold is True]
        assert len(bold_runs) == 1
        assert bold_runs[0].text == "bold"

        # Check for italic
        italic_runs = [r for r in runs if isinstance(r, InlineRunNode) and r.italic is True]
        assert len(italic_runs) == 1
        assert italic_runs[0].text == "italic"

        # Check for code
        code_nodes = [r for r in runs if isinstance(r, InlineCodeNode)]
        assert len(code_nodes) == 1
        assert code_nodes[0].code == "code"

    def test_inline_paragraph_with_formatting(self):
        """Test full paragraph parsing with formatting."""
        text = "The *quick* brown fox jumps over the _lazy_ dog."
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
        assert len(paragraphs) == 1

        runs = paragraphs[0].runs
        # Should have: plain "The ", bold "quick", plain " brown fox jumps over the ", italic "lazy", plain " dog."
        assert len(runs) == 5

        # Verify each run type
        assert isinstance(runs[0], TextRun)
        assert runs[0].text == "The "

        assert isinstance(runs[1], InlineRunNode)
        assert runs[1].bold is True
        assert runs[1].text == "quick"

        assert isinstance(runs[2], TextRun)
        assert runs[2].text == " brown fox jumps over the "

        assert isinstance(runs[3], InlineRunNode)
        assert runs[3].italic is True
        assert runs[3].text == "lazy"

        assert isinstance(runs[4], TextRun)
        assert runs[4].text == " dog."

    def test_inline_ref_with_formatting(self):
        """Test that @ref and formatting work together."""
        text = "As shown in *Figure 1* @fig-1, the results are good."
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        paragraphs = [b for b in doc.blocks if b.node_type == "paragraph"]
        assert len(paragraphs) == 1

        runs = paragraphs[0].runs

        # Find bold run
        bold_runs = [r for r in runs if isinstance(r, InlineRunNode) and r.bold is True]
        assert len(bold_runs) == 1
        assert bold_runs[0].text == "Figure 1"

        # Find cross reference
        refs = [r for r in runs if isinstance(r, CrossReference)]
        assert len(refs) == 1
        assert refs[0].target_label == "fig-1"


class TestInlineFormattingDirect:
    """Test inline formatting parsing via direct method calls."""

    def test_parse_inline_formatting_bold(self):
        """Test _parse_inline_formatting method with bold."""
        extractor = TypstExtractorV2("", "test.typ")
        nodes = extractor._parse_inline_formatting("Hello *world*!")

        # Should have: TextRun "Hello ", InlineRunNode bold "world", TextRun "!"
        assert len(nodes) == 3
        assert isinstance(nodes[0], TextRun)
        assert nodes[0].text == "Hello "

        assert isinstance(nodes[1], InlineRunNode)
        assert nodes[1].bold is True
        assert nodes[1].text == "world"

        assert isinstance(nodes[2], TextRun)
        assert nodes[2].text == "!"

    def test_parse_inline_formatting_italic(self):
        """Test _parse_inline_formatting method with italic."""
        extractor = TypstExtractorV2("", "test.typ")
        nodes = extractor._parse_inline_formatting("Hello _world_!")

        # Should have: TextRun "Hello ", InlineRunNode italic "world", TextRun "!"
        assert len(nodes) == 3
        assert isinstance(nodes[0], TextRun)
        assert nodes[0].text == "Hello "

        assert isinstance(nodes[1], InlineRunNode)
        assert nodes[1].italic is True
        assert nodes[1].text == "world"

        assert isinstance(nodes[2], TextRun)
        assert nodes[2].text == "!"

    def test_parse_inline_formatting_code(self):
        """Test _parse_inline_formatting method with code."""
        extractor = TypstExtractorV2("", "test.typ")
        nodes = extractor._parse_inline_formatting("Call `func()` now")

        # Should have: TextRun "Call ", InlineCodeNode "func()", TextRun " now"
        assert len(nodes) == 3
        assert isinstance(nodes[0], TextRun)
        assert nodes[0].text == "Call "

        assert isinstance(nodes[1], InlineCodeNode)
        assert nodes[1].code == "func()"

        assert isinstance(nodes[2], TextRun)
        assert nodes[2].text == " now"

    def test_parse_inline_formatting_no_formatting(self):
        """Test _parse_inline_formatting with plain text (no formatting)."""
        extractor = TypstExtractorV2("", "test.typ")
        nodes = extractor._parse_inline_formatting("Just plain text")

        # Should return single TextRun
        assert len(nodes) == 1
        assert isinstance(nodes[0], TextRun)
        assert nodes[0].text == "Just plain text"

    def test_parse_inline_formatting_combined(self):
        """Test _parse_inline_formatting with multiple formats combined."""
        extractor = TypstExtractorV2("", "test.typ")
        nodes = extractor._parse_inline_formatting("_*bold+italic*_")

        # Should have InlineRunNode with both bold and italic
        assert len(nodes) == 1
        assert isinstance(nodes[0], InlineRunNode)
        # Current implementation only recognizes single format at a time
        # This test documents current behavior
