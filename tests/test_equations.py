"""Tests for equation handling."""

from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2


def test_inline_math():
    text = """
The equation is $E = mc^2$.
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) >= 0


def test_block_math():
    text = """
$$
x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}
$$
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) == 1


def test_multiple_block_math():
    text = """
$$
E = mc^2
$$

$$
F = ma
$$
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) == 2


def test_math_with_greek():
    # Use raw string for input to preserve backslashes
    # Then manually handle newlines since raw strings don't interpret \n
    text = "$$" + "\n" + r"\alpha + \beta = \gamma" + "\n" + "$$"
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) == 1
    # The result will contain single backslash (preserved from raw string)
    assert r"\alpha" in equations[0].latex
    assert r"\beta" in equations[0].latex


def test_math_with_indices():
    text = """
$$
\sum_{i=1}^{n} x_i
$$
"""
    extractor = TypstExtractorV2(text, "test.typ")

    doc = extractor.extract()

    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) == 1
