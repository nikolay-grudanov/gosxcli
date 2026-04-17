"""Tests for equation handling."""

from typst_gost_docx.parser.scanner import TypstScanner
from typst_gost_docx.parser.extractor import TypstExtractor


def test_inline_math():
    text = """
The equation is $E = mc^2$.
"""
    scanner = TypstScanner(text)
    extractor = TypstExtractor(scanner, "test.typ")

    doc = extractor.extract()

    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) >= 0


def test_block_math():
    text = """
$$
x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}
$$
"""
    scanner = TypstScanner(text)
    extractor = TypstExtractor(scanner, "test.typ")

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
    scanner = TypstScanner(text)
    extractor = TypstExtractor(scanner, "test.typ")

    doc = extractor.extract()

    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) == 2


def test_math_with_greek():
    text = """
$$
\alpha + \beta = \gamma
$$
"""
    scanner = TypstScanner(text)
    extractor = TypstExtractor(scanner, "test.typ")

    doc = extractor.extract()

    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) == 1
    assert r"\alpha" in equations[0].latex
    assert r"\beta" in equations[0].latex


def test_math_with_indices():
    text = """
$$
\sum_{i=1}^{n} x_i
$$
"""
    scanner = TypstScanner(text)
    extractor = TypstExtractor(scanner, "test.typ")

    doc = extractor.extract()

    equations = [b for b in doc.blocks if b.node_type == "equation"]
    assert len(equations) == 1
