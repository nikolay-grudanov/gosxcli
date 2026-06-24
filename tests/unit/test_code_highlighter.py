"""Unit tests for code_highlighter module.

Tests for syntax highlighting functions:
- get_lexer() - lexer retrieval
- get_token_color() - token color mapping
- is_supported_language() - language support check
- get_supported_languages() - supported languages list
"""

from docx.shared import RGBColor
from pygments.lexer import Lexer
from pygments.token import Token

from typst_gost_docx.writers.code_highlighter import (
    get_lexer,
    get_supported_languages,
    get_token_color,
    is_supported_language,
)


class TestGetLexer:
    """Tests for get_lexer function."""

    def test_get_lexer_python(self) -> None:
        """Should get lexer for Python."""
        lexer = get_lexer("python")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_rust(self) -> None:
        """Should get lexer for Rust."""
        lexer = get_lexer("rust")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_javascript(self) -> None:
        """Should get lexer for JavaScript."""
        lexer = get_lexer("javascript")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_c(self) -> None:
        """Should get lexer for C."""
        lexer = get_lexer("c")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_cpp(self) -> None:
        """Should get lexer for C++."""
        lexer = get_lexer("cpp")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_go(self) -> None:
        """Should get lexer for Go."""
        lexer = get_lexer("go")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_unknown(self) -> None:
        """Should fallback to text lexer for unknown language."""
        lexer = get_lexer("unknown_language_xyz")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_case_insensitive(self) -> None:
        """Should handle language case insensitively."""
        lexer_upper = get_lexer("PYTHON")
        lexer_lower = get_lexer("python")
        assert lexer_upper is not None
        assert lexer_lower is not None

    def test_get_lexer_alias_py(self) -> None:
        """Should handle Python alias 'py'."""
        lexer = get_lexer("py")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_alias_js(self) -> None:
        """Should handle JavaScript alias 'js'."""
        lexer = get_lexer("js")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_alias_rs(self) -> None:
        """Should handle Rust alias 'rs'."""
        lexer = get_lexer("rs")
        assert lexer is not None
        assert isinstance(lexer, Lexer)

    def test_get_lexer_alias_cpp(self) -> None:
        """Should handle C++ alias 'c++'."""
        lexer = get_lexer("c++")
        assert lexer is not None
        assert isinstance(lexer, Lexer)


class TestGetTokenColor:
    """Tests for get_token_color function."""

    def test_get_token_color_keyword(self) -> None:
        """Should get color for Keyword token."""
        color = get_token_color(Token.Keyword)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_string(self) -> None:
        """Should get color for String token."""
        color = get_token_color(Token.String)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_comment(self) -> None:
        """Should get color for Comment token."""
        color = get_token_color(Token.Comment)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_number(self) -> None:
        """Should get color for Number token."""
        color = get_token_color(Token.Number)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_name_function(self) -> None:
        """Should get color for Name.Function token."""
        color = get_token_color(Token.Name.Function)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_keyword_type(self) -> None:
        """Should get color for Keyword.Type token."""
        color = get_token_color(Token.Keyword.Type)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_operator(self) -> None:
        """Should get color for Operator token."""
        color = get_token_color(Token.Operator)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_comment_single(self) -> None:
        """Should get color for Comment.Single token."""
        color = get_token_color(Token.Comment.Single)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_string_doc(self) -> None:
        """Should get color for String.Doc token."""
        color = get_token_color(Token.String.Doc)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_none(self) -> None:
        """Should return default color for None token type."""
        color = get_token_color(None)
        assert color is not None
        assert isinstance(color, RGBColor)

    def test_get_token_color_unknown(self) -> None:
        """Should return default color for unknown token type."""
        color = get_token_color(Token.Generic.Output)
        assert color is not None
        assert isinstance(color, RGBColor)


class TestIsSupportedLanguage:
    """Tests for is_supported_language function."""

    def test_is_supported_language_python(self) -> None:
        """Should return True for Python."""
        assert is_supported_language("python") is True

    def test_is_supported_language_rust(self) -> None:
        """Should return True for Rust."""
        assert is_supported_language("rust") is True

    def test_is_supported_language_javascript(self) -> None:
        """Should return True for JavaScript."""
        assert is_supported_language("javascript") is True

    def test_is_supported_language_c(self) -> None:
        """Should return True for C."""
        assert is_supported_language("c") is True

    def test_is_supported_language_cpp(self) -> None:
        """Should return True for C++."""
        assert is_supported_language("cpp") is True

    def test_is_supported_language_go(self) -> None:
        """Should return True for Go."""
        assert is_supported_language("go") is True

    def test_is_supported_language_alias_py(self) -> None:
        """Should return True for Python alias 'py'."""
        assert is_supported_language("py") is True

    def test_is_supported_language_alias_js(self) -> None:
        """Should return True for JavaScript alias 'js'."""
        assert is_supported_language("js") is True

    def test_is_supported_language_alias_rs(self) -> None:
        """Should return True for Rust alias 'rs'."""
        assert is_supported_language("rs") is True

    def test_is_supported_language_alias_cpp(self) -> None:
        """Should return True for C++ alias 'c++'."""
        assert is_supported_language("c++") is True

    def test_is_supported_language_plain(self) -> None:
        """Should return True for plain text."""
        assert is_supported_language("plain") is True

    def test_is_supported_language_text(self) -> None:
        """Should return True for text."""
        assert is_supported_language("text") is True

    def test_is_supported_language_case_insensitive(self) -> None:
        """Should handle case insensitively."""
        assert is_supported_language("PYTHON") is True
        assert is_supported_language("Python") is True

    def test_is_supported_language_unknown(self) -> None:
        """Should return False for unknown language."""
        assert is_supported_language("unknown_lang") is False

    def test_is_supported_language_not_valid(self) -> None:
        """Should return False for invalid language."""
        assert is_supported_language("random123") is False


class TestGetSupportedLanguages:
    """Tests for get_supported_languages function."""

    def test_get_supported_languages_returns_list(self) -> None:
        """Should return a list."""
        languages = get_supported_languages()
        assert isinstance(languages, list)

    def test_get_supported_languages_sorted(self) -> None:
        """Should return sorted list."""
        languages = get_supported_languages()
        assert languages == sorted(languages)

    def test_get_supported_languages_contains_python(self) -> None:
        """Should contain Python."""
        languages = get_supported_languages()
        assert "python" in languages

    def test_get_supported_languages_contains_rust(self) -> None:
        """Should contain Rust."""
        languages = get_supported_languages()
        assert "rust" in languages

    def test_get_supported_languages_contains_javascript(self) -> None:
        """Should contain JavaScript."""
        languages = get_supported_languages()
        assert "javascript" in languages

    def test_get_supported_languages_contains_c(self) -> None:
        """Should contain C."""
        languages = get_supported_languages()
        assert "c" in languages

    def test_get_supported_languages_contains_cpp(self) -> None:
        """Should contain C++."""
        languages = get_supported_languages()
        assert "cpp" in languages

    def test_get_supported_languages_contains_go(self) -> None:
        """Should contain Go."""
        languages = get_supported_languages()
        assert "go" in languages

    def test_get_supported_languages_count(self) -> None:
        """Should contain expected number of languages."""
        languages = get_supported_languages()
        # Check that all aliases are included
        assert len(languages) >= 8  # python, py, rust, rs, js, javascript, c, cpp, go, golang, plain, text