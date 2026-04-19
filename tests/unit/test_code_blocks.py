"""Unit tests for CodeBlock IR model and parsing.

Tests for CodeBlockNode model and code block extraction.
"""

from typst_gost_docx.ir.model import CodeBlockNode, Document, NodeType


def _get_code_blocks(doc: Document) -> list[CodeBlockNode]:
    """Extract CodeBlockNode instances from document blocks.

    Type narrowing helper for mypy strict mode.
    """
    return [b for b in doc.blocks if isinstance(b, CodeBlockNode)]


class TestCodeBlockNode:
    """Tests for CodeBlockNode model."""

    def test_create_minimal_code_block(self) -> None:
        """Should create code block with minimal fields."""
        code_block = CodeBlockNode(
            id="test-id",
            content="print('hello')",
        )
        assert code_block.node_type == NodeType.CODE_BLOCK
        assert code_block.content == "print('hello')"
        assert code_block.language is None

    def test_create_code_block_with_language(self) -> None:
        """Should create code block with language identifier."""
        code_block = CodeBlockNode(
            id="test-id",
            content="def foo(): pass",
            language="python",
        )
        assert code_block.node_type == NodeType.CODE_BLOCK
        assert code_block.content == "def foo(): pass"
        assert code_block.language == "python"

    def test_create_code_block_with_multiline_content(self) -> None:
        """Should handle multi-line code content."""
        code_block = CodeBlockNode(
            id="test-id",
            content="def foo():\n    pass\n\nbar = 1",
            language="python",
        )
        assert code_block.node_type == NodeType.CODE_BLOCK
        assert "\n" in code_block.content
        assert code_block.content == "def foo():\n    pass\n\nbar = 1"

    def test_create_code_block_empty_language(self) -> None:
        """Should handle empty language string."""
        code_block = CodeBlockNode(
            id="test-id",
            content="some code",
            language="",
        )
        assert code_block.node_type == NodeType.CODE_BLOCK
        assert code_block.language == ""

    def test_code_block_label_support(self) -> None:
        """Should support label for code blocks."""
        code_block = CodeBlockNode(
            id="test-id",
            content="code here",
            label="code:example",
        )
        assert code_block.label == "code:example"

    def test_code_block_source_location(self) -> None:
        """Should support source location for code blocks."""
        from typst_gost_docx.ir.model import SourceLocation

        source_loc = SourceLocation(
            file_path="test.typ",
            line=10,
            column=5,
        )
        code_block = CodeBlockNode(
            id="test-id",
            content="code here",
            source_location=source_loc,
        )
        assert code_block.source_location is not None
        assert code_block.source_location.file_path == "test.typ"
        assert code_block.source_location.line == 10

    def test_code_block_style_hints(self) -> None:
        """Should support style hints for code blocks."""
        code_block = CodeBlockNode(
            id="test-id",
            content="code here",
            style_hints={"background": "#f0f0f0"},
        )
        assert code_block.style_hints == {"background": "#f0f0f0"}


class TestCodeBlockExtraction:
    """Tests for code block extraction from Typst source."""

    def test_extract_python_code_block(self) -> None:
        """Should extract Python code block."""
        from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2

        text = """```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```
"""
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        code_blocks = _get_code_blocks(doc)
        assert len(code_blocks) == 1

        code_block = code_blocks[0]
        assert code_block.language == "python"
        assert "def fibonacci(n):" in code_block.content
        assert "return fibonacci(n-1) + fibonacci(n-2)" in code_block.content

    def test_extract_plain_code_block(self) -> None:
        """Should extract plain code block without language."""
        from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2

        text = """```
This is plain text code.
No language specified.
```
"""
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        code_blocks = _get_code_blocks(doc)
        assert len(code_blocks) == 1

        code_block = code_blocks[0]
        assert code_block.language is None or code_block.language == ""
        assert "This is plain text code." in code_block.content

    def test_extract_rust_code_block(self) -> None:
        """Should extract Rust code block."""
        from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2

        text = """```rust
fn main() {
    println!("Hello, world!");
}
```
"""
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        code_blocks = _get_code_blocks(doc)
        assert len(code_blocks) == 1

        code_block = code_blocks[0]
        assert code_block.language == "rust"
        assert "fn main()" in code_block.content

    def test_extract_multiple_code_blocks(self) -> None:
        """Should extract multiple code blocks from document."""
        from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2

        text = """= Introduction

```python
print("Hello")
```

Some text here.

```bash
echo "World"
```

= Conclusion
"""
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        code_blocks = _get_code_blocks(doc)
        assert len(code_blocks) == 2

        assert code_blocks[0].language == "python"
        assert code_blocks[1].language == "bash"

    def test_extract_code_block_with_special_chars(self) -> None:
        """Should handle special characters in code blocks."""
        from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2

        text = """```python
# Special chars: <, >, &, ", '
if x < 5 and y > 3:
    print("Hello & goodbye")
```
"""
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        code_blocks = _get_code_blocks(doc)
        assert len(code_blocks) == 1

        code_block = code_blocks[0]
        assert "<" in code_block.content
        assert ">" in code_block.content
        assert "&" in code_block.content
        assert '"' in code_block.content

    def test_extract_code_block_preserves_indentation(self) -> None:
        """Should preserve indentation in code blocks."""
        from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2

        text = """```python
def hello():
    print("    indented")
        print("more indented")
```
"""
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        code_blocks = _get_code_blocks(doc)
        assert len(code_blocks) == 1

        code_block = code_blocks[0]
        assert "    print(" in code_block.content  # 4 spaces
        assert "        print(" in code_block.content  # 8 spaces

    def test_extract_code_block_preserves_empty_lines(self) -> None:
        """Should preserve empty lines in code blocks."""
        from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2

        text = """```python
def foo():
    pass


def bar():
    pass
```
"""
        extractor = TypstExtractorV2(text, "test.typ")
        doc = extractor.extract()

        code_blocks = _get_code_blocks(doc)
        assert len(code_blocks) == 1

        code_block = code_blocks[0]
        assert "\n\n" in code_block.content  # Double newline for empty line
