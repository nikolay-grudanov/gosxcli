"""XML utilities for low-level OpenXML manipulation."""

from typing import Any, cast
from lxml import etree  # type: ignore[import-untyped]


def format_xml(element: etree.Element) -> str:
    result = etree.tostring(element, pretty_print=True, encoding="unicode")
    return cast(str, result)


def create_element(tag: str, **attrs: Any) -> etree.Element:
    elem = etree.Element(tag)
    for key, value in attrs.items():
        elem.set(key, str(value))
    return elem
