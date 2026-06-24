"""XML utilities for low-level OpenXML manipulation."""

from typing import Any

from lxml import etree


def format_xml(element: etree._Element) -> str:
    # ``tostring(..., encoding="unicode")`` returns ``str`` per lxml stubs.
    result: str = etree.tostring(element, pretty_print=True, encoding="unicode")
    return result


def create_element(tag: str, **attrs: Any) -> etree._Element:
    elem = etree.Element(tag)
    for key, value in attrs.items():
        elem.set(key, str(value))
    return elem
