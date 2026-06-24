"""Syntax highlighting module using Pygments.

This module provides syntax highlighting for code blocks in DOCX documents
using the Pygments library. It uses VS Code Dark+ color scheme.

Typical usage:
    from typst_gost_docx.writers.code_highlighter import highlight_code

    highlight_code("def hello():", "python", paragraph)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from docx.shared import Pt, RGBColor
from pygments.lexers import get_lexer_by_name  # type: ignore[import-untyped]
from pygments.token import Token  # type: ignore[import-untyped]
from pygments.lexer import Lexer  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from docx.text.paragraph import Paragraph
    from pygments.lexer import Lexer

# VS Code Dark+ color scheme
TOKEN_COLORS = {
    Token.Keyword: RGBColor(0x00, 0x9B, 0xD8),  # Cyan
    Token.Keyword.Constant: RGBColor(0x00, 0x9B, 0xD8),
    Token.Keyword.Declaration: RGBColor(0x00, 0x9B, 0xD8),
    Token.Keyword.Type: RGBColor(0x4E, 0xC4, 0xD8),
    Token.Name: RGBColor(0x9E, 0xE6, 0xFF),
    Token.Name.Function: RGBColor(0xDC, 0xDD, 0xCC),
    Token.Name.Class: RGBColor(0x4E, 0xC4, 0xD8),
    Token.String: RGBColor(0xCE, 0x91, 0x78),
    Token.String.Doc: RGBColor(0x6A, 0x99, 0x55),
    Token.Number: RGBColor(0xB5, 0xCE, 0xA8),
    Token.Comment: RGBColor(0x6A, 0x99, 0x55),
    Token.Comment.Single: RGBColor(0x6A, 0x99, 0x55),
    Token.Comment.Multiline: RGBColor(0x6A, 0x99, 0x55),
    Token.Operator: RGBColor(0xD4, 0xD4, 0xD4),
    Token.Punctuation: RGBColor(0xD4, 0xD4, 0xD4),
    Token.Generic: RGBColor(0xD4, 0xD4, 0xD4),
    Token.Other: RGBColor(0xD4, 0xD4, 0xD4),
}

# Default color for unrecognized tokens
DEFAULT_COLOR = RGBColor(0xD4, 0xD4, 0xD4)  # Light gray

# Language aliases mapping
LANG_ALIASES = {
    "python": "python",
    "py": "python",
    "rust": "rust",
    "rs": "rust",
    "javascript": "javascript",
    "js": "javascript",
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "go": "go",
    "golang": "go",
    "plain": "text",
    "text": "text",
}

# Supported languages
SUPPORTED_LANGUAGES = frozenset(LANG_ALIASES.keys())


def get_lexer(language: str) -> Lexer:
    """Get Pygments lexer by language name.

    Args:
        language: Language identifier (python, rust, js, etc.)

    Returns:
        Pygments lexer instance for the specified language.
    """
    lang = LANG_ALIASES.get(language.lower(), language.lower())
    try:
        return get_lexer_by_name(lang)
    except Exception:  # noqa: BLE001
        logger = logging.getLogger("typst_gost_docx")
        logger.debug(f"Failed to get lexer for '{lang}', falling back to text")
        return get_lexer_by_name("text")


def get_token_color(token_type: Any) -> RGBColor:
    """Get color for a Pygments token type.

    Handles token subtypes by checking the exact match or parent types.

    Args:
        token_type: Pygments token type (can be Token or tuple of tokens).

    Returns:
        RGBColor for the token type.
    """
    # Handle None token type
    if token_type is None:
        return DEFAULT_COLOR

    # Convert token type to string and check parent types
    # Pygments tokens are like: Token.Keyword, Token.Name.Function, etc.
    token_str = str(token_type)
    token_parts = token_str.split(".")

    # Check from most specific (longest) to most general (shortest)
    for i in range(len(token_parts), 0, -1):
        check_str = ".".join(token_parts[:i])
        if check_str in TOKEN_COLORS:
            return TOKEN_COLORS[check_str]

    return DEFAULT_COLOR


def highlight_code(
    code: str,
    language: str,
    paragraph: Paragraph,
    shading_color: RGBColor | None = None,
) -> None:
    """Add syntax highlighted code to a paragraph.

    Applies Pygments-based syntax highlighting to code text, using VS Code Dark+
    color scheme and monospace font.

    Args:
        code: Source code string.
        language: Language identifier (python, rust, js, c, cpp, go, etc.)
        paragraph: python-docx Paragraph object.
        shading_color: Optional background color (RGBColor). If None, no shading applied.
    """
    from pygments import lex  # type: ignore[import-untyped]

    lexer = get_lexer(language)
    tokens = list(lex(code, lexer))

    # Clear existing runs and create first run
    if paragraph.runs:
        paragraph.runs[0]._element.text = ""  # noqa: SLF001
        first_run = paragraph.runs[0]
    else:
        first_run = paragraph.add_run()

    # Set base font properties
    first_run.font.name = "Courier New"
    first_run.font.size = Pt(9)

    # Handle empty code
    if not code:
        return

    # Process tokens and create runs with appropriate colors
    for i, (token_type, token_string) in enumerate(tokens):
        if i == 0:
            # Reuse first run
            run = first_run
            run.text = token_string
        else:
            run = paragraph.add_run(token_string)

        run.font.name = "Courier New"
        run.font.size = Pt(9)

        # Apply color
        color = get_token_color(token_type)
        run.font.color.rgb = color

    # Apply shading if provided
    if shading_color:
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement

        shading_elm = OxmlElement("w:shd")
        # Convert RGBColor to hex string using str() method
        color_hex = str(shading_color)
        shading_elm.set(qn("w:fill"), color_hex)
        paragraph._element.get_or_add_pPr().insert_element_before(shading_elm, "w:spacing")


def is_supported_language(language: str) -> bool:
    """Check if a language is supported for syntax highlighting.

    Args:
        language: Language identifier to check.

    Returns:
        True if the language is supported, False otherwise.
    """
    return language.lower() in SUPPORTED_LANGUAGES


def get_supported_languages() -> list[str]:
    """Get list of supported language identifiers.

    Returns:
        List of supported language names.
    """
    return sorted(SUPPORTED_LANGUAGES)
