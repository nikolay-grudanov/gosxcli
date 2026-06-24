"""MathML to OMML converter for equation rendering.

Converts MathML elements to Office Math Markup Language (OMML) elements
that can be embedded in Word documents via python-docx.

OMML namespace: http://schemas.openxmlformats.org/officeDocument/2006/math
MathML namespace: http://www.w3.org/1998/Math/MathML
"""

from __future__ import annotations

from typing import Optional

from lxml import etree

from docx.oxml.ns import qn


def convert_mathml_to_omml(mathml_str: str) -> Optional[etree._Element]:
    """Convert MathML string to OMML element.

    Args:
        mathml_str: MathML XML string from latex2mathml.

    Returns:
        OMML oMath element or None if conversion fails.
    """
    try:
        # Parse MathML string to lxml element
        mathml_elem = etree.fromstring(mathml_str.encode())

        # Create root oMath element
        omath = etree.Element(qn("m:oMath"))

        # Convert children
        _convert_math_children(mathml_elem, omath)

        return omath
    except Exception:
        return None


def _convert_math_children(source: etree._Element, target: etree._Element) -> None:
    """Recursively convert MathML children to OMML.

    Args:
        source: Source MathML element.
        target: Target OMML element.
    """
    for child in source:
        tag = etree.QName(child.tag).localname

        if tag in ("mi", "mo", "mn", "mtext"):
            # Identifier, operator, number, text -> text run
            text = child.text or ""
            if text:
                r = etree.SubElement(target, qn("m:r"))
                t = etree.SubElement(r, qn("m:t"))
                t.text = text
        elif tag == "mfrac":
            # Fraction
            _convert_fraction(child, target)
        elif tag in ("msqrt", "mroot"):
            # Square root or root
            _convert_radical(child, target)
        elif tag == "msup":
            # Superscript
            _convert_superscript(child, target)
        elif tag == "msub":
            # Subscript
            _convert_subscript(child, target)
        elif tag in ("msubsup", "munderover"):
            # Subscript-superscript
            _convert_sub_sup(child, target)
        elif tag == "munder":
            # Underscore - simplified pass-through
            _convert_math_children(child, target)
        elif tag == "mtable":
            # Matrix/table
            _convert_table(child, target)
        elif tag == "mspace":
            # Space - add blank text run
            r = etree.SubElement(target, qn("m:r"))
            t = etree.SubElement(r, qn("m:t"))
            t.text = " "
        elif tag == "mrow":
            # Grouped expressions — pass through children
            _convert_math_children(child, target)
        else:
            # Unknown element - try to get text content
            if child.text:
                r = etree.SubElement(target, qn("m:r"))
                t = etree.SubElement(r, qn("m:t"))
                t.text = child.text


def _convert_fraction(source: etree._Element, target: etree._Element) -> None:
    """Convert MathML fraction to OMML fraction.

    Args:
        source: Source mfrac element.
        target: Target OMML element to append to.
    """
    f = etree.SubElement(target, qn("m:f"))

    # Fraction properties
    fPr = etree.SubElement(f, qn("m:fPr"))
    type_elem = etree.SubElement(fPr, qn("m:type"))
    type_elem.set(qn("m:val"), "bar")

    # Numerator (first child) and Denominator (second child)
    children = list(source)
    num = etree.SubElement(f, qn("m:num"))
    if len(children) >= 1:
        _convert_math_children(children[0], num)
    den = etree.SubElement(f, qn("m:den"))
    if len(children) >= 2:
        _convert_math_children(children[1], den)


def _convert_radical(source: etree._Element, target: etree._Element) -> None:
    """Convert MathML radical to OMML radical.

    Args:
        source: Source msqrt/mroot element.
        target: Target OMML element to append to.
    """
    rad = etree.SubElement(target, qn("m:rad"))

    # Radical properties
    radPr = etree.SubElement(rad, qn("m:radPr"))
    degHide = etree.SubElement(radPr, qn("m:degHide"))
    degHide.set(qn("m:val"), "on")  # Hide degree for square root

    # Degree (for mroot)
    deg = etree.SubElement(rad, qn("m:deg"))
    tag = etree.QName(source.tag).localname
    if tag == "mroot":
        # mroot has degree as first child
        children = list(source)
        if children:
            _convert_math_children(children[0], deg)

    # radicand (the base)
    e = etree.SubElement(rad, qn("m:e"))
    for child in source:
        tag = etree.QName(child.tag).localname
        if tag == "mrow":
            _convert_math_children(child, e)


def _convert_superscript(source: etree._Element, target: etree._Element) -> None:
    """Convert MathML superscript to OMML superscript.

    Args:
        source: Source msup element.
        target: Target OMML element to append to.
    """
    sup = etree.SubElement(target, qn("m:sSup"))

    # Base
    e = etree.SubElement(sup, qn("m:e"))
    # Superscript
    sup2 = etree.SubElement(sup, qn("m:sup"))

    children = list(source)
    if len(children) >= 1:
        _convert_math_children(children[0], e)
    if len(children) >= 2:
        _convert_math_children(children[1], sup2)


def _convert_subscript(source: etree._Element, target: etree._Element) -> None:
    """Convert MathML subscript to OMML subscript.

    Args:
        source: Source msub element.
        target: Target OMML element to append to.
    """
    sub = etree.SubElement(target, qn("m:sSub"))

    # Base
    e = etree.SubElement(sub, qn("m:e"))
    # Subscript
    sub2 = etree.SubElement(sub, qn("m:sub"))

    children = list(source)
    if len(children) >= 1:
        _convert_math_children(children[0], e)
    if len(children) >= 2:
        _convert_math_children(children[1], sub2)


def _convert_sub_sup(source: etree._Element, target: etree._Element) -> None:
    """Convert MathML subscript-superscript to OMML.

    Args:
        source: Source msubsup/munderover element.
        target: Target OMML element to append to.
    """
    subSup = etree.SubElement(target, qn("m:sSubSup"))

    # Base
    e = etree.SubElement(subSup, qn("m:e"))
    # Subscript
    sub = etree.SubElement(subSup, qn("m:sub"))
    # Superscript
    sup = etree.SubElement(subSup, qn("m:sup"))

    children = list(source)
    if len(children) >= 1:
        _convert_math_children(children[0], e)
    if len(children) >= 2:
        _convert_math_children(children[1], sub)
    if len(children) >= 3:
        _convert_math_children(children[2], sup)


def _convert_table(source: etree._Element, target: etree._Element) -> None:
    """Convert MathML table/matrix to OMML.

    Args:
        source: Source mtable element.
        target: Target OMML element to append to.
    """
    m = etree.SubElement(target, qn("m:m"))

    # Matrix properties
    mPr = etree.SubElement(m, qn("m:mPr"))
    cCols = etree.SubElement(mPr, qn("m:cCols"))
    cCols.set(qn("m:val"), "1")

    # Process rows
    for row in source:
        if etree.QName(row.tag).localname == "mtr":
            mr = etree.SubElement(m, qn("m:mr"))
            # Create row structure
            for cell in row:
                if etree.QName(cell.tag).localname == "mtd":
                    e = etree.SubElement(mr, qn("m:e"))
                    _convert_math_children(cell, e)
