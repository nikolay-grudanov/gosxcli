"""XML utilities for low-level OpenXML manipulation."""

from lxml import etree


def format_xml(element: etree.Element) -> str:
    return etree.tostring(element, pretty_print=True, encoding="unicode")


def create_element(tag: str, **attrs) -> etree.Element:
    elem = etree.Element(tag)
    for key, value in attrs.items():
        elem.set(key, str(value))
    return elem
