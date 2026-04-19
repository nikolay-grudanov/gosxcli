"""Smoke tests for v0.1 backward compatibility.

Ensures that basic conversion functionality from v0.1 still works in v0.2.
"""

from pathlib import Path

from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2
from typst_gost_docx.writers.docx_writer import DocxWriter


def test_v01_basic_conversion(tmp_path: Path) -> None:
    """Test basic v0.1 features: headings, paragraphs, lists.

    Ensures that minimal document with basic features converts correctly.
    """
    # Create a simple v0.1-style document
    typst_content = """= Main Heading
This is a paragraph.

== Subheading
This is another paragraph.

- Item 1
- Item 2
"""

    output_file = tmp_path / "output.docx"

    # Extract structure (v0.1 style: direct text input)
    extractor = TypstExtractorV2(typst_content, "test.typ")
    ir_doc = extractor.extract()

    # Write DOCX
    writer = DocxWriter()
    writer.write(ir_doc, output_file)

    # Verify output file exists
    assert output_file.exists(), "Output DOCX file was not created"

    # Verify file size is reasonable (not empty)
    file_size = output_file.stat().st_size
    assert file_size > 1000, f"Output file too small: {file_size} bytes"


def test_v01_headings_conversion(tmp_path: Path) -> None:
    """Test that heading levels 1-3 from v0.1 convert correctly."""
    typst_content = """= Level 1 Heading
Content under L1.

== Level 2 Heading
Content under L2.

=== Level 3 Heading
Content under L3.
"""

    output_file = tmp_path / "headings.docx"

    # Extract structure
    extractor = TypstExtractorV2(typst_content, "headings.typ")
    ir_doc = extractor.extract()

    # Write DOCX
    writer = DocxWriter()
    writer.write(ir_doc, output_file)

    # Verify output
    assert output_file.exists()
    assert output_file.stat().st_size > 1000


def test_v01_basic_table_conversion(tmp_path: Path) -> None:
    """Test that basic table from v0.1 converts correctly."""
    typst_content = """= Table Test

#table(
  columns: 2,
  [Cell 1][Cell 2],
  [Cell 3][Cell 4],
)
"""

    output_file = tmp_path / "table.docx"

    # Extract structure
    extractor = TypstExtractorV2(typst_content, "table.typ")
    ir_doc = extractor.extract()

    # Write DOCX
    writer = DocxWriter()
    writer.write(ir_doc, output_file)

    # Verify output
    assert output_file.exists()
    assert output_file.stat().st_size > 1000


def test_v01_labels_and_references(tmp_path: Path) -> None:
    """Test that labels and references from v0.1 work."""
    typst_content = """= Reference Test

Here is a figure <fig:test>.

= Another Section

See @fig:test for details.
"""

    output_file = tmp_path / "refs.docx"

    # Extract structure
    extractor = TypstExtractorV2(typst_content, "refs.typ")
    ir_doc = extractor.extract()

    # Write DOCX
    writer = DocxWriter()
    writer.write(ir_doc, output_file)

    # Verify output
    assert output_file.exists()
    assert output_file.stat().st_size > 1000


def test_v01_inline_math(tmp_path: Path) -> None:
    """Test that inline math from v0.1 converts (with fallback)."""
    typst_content = """= Math Test

The formula is $E = mc^2$.
"""

    output_file = tmp_path / "math.docx"

    # Extract structure
    extractor = TypstExtractorV2(typst_content, "math.typ")
    ir_doc = extractor.extract()

    # Write DOCX
    writer = DocxWriter()
    writer.write(ir_doc, output_file)

    # Verify output
    assert output_file.exists()
    assert output_file.stat().st_size > 1000
