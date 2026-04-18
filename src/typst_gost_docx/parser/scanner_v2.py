"""Simplified Typst scanner for robust parsing."""

import re
from dataclasses import dataclass
from typing import Generator, Optional


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


class TypstScannerV2:
    """Simplified scanner for reliable tokenization."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def scan(self) -> Generator[Token, None, None]:
        """Scan text and generate tokens.

        Yields:
            Tokens for structured elements and text
        """
        while self.pos < len(self.text):
            # Try to match patterns at current position
            matched = False
            token = None

            # Check for special patterns first
            token = self._match_heading()
            if token:
                yield token
                matched = True
            else:
                token = self._match_list_item()
                if token:
                    yield token
                    matched = True
                else:
                    token = self._match_figure_start()
                    if token:
                        yield token
                        matched = True
                    else:
                        token = self._match_table_start()
                        if token:
                            yield token
                            matched = True
                        else:
                            token = self._match_block_math()
                            if token:
                                yield token
                                matched = True
                            else:
                                token = self._match_label()
                                if token:
                                    yield token
                                    matched = True
                                else:
                                    token = self._match_inline_ref()
                                    if token:
                                        yield token
                                        matched = True

            if not matched:
                # Yield as TEXT character(s)
                if self.text[self.pos] == "\n":
                    self.line += 1
                    self.pos += 1
                    self.column = 1
                else:
                    # Collect text until next pattern or newline
                    text_start = self.pos
                    while self.pos < len(self.text) and self.text[self.pos] != "\n":
                        if self._peek_special():
                            break
                        self.pos += 1
                        self.column += 1

                    if self.pos > text_start:
                        yield Token(
                            "TEXT",
                            self.text[text_start : self.pos],
                            self.line,
                            self.column - (self.pos - text_start),
                        )

    def _peek_special(self) -> bool:
        """Check if next character starts a special pattern."""
        if self.pos >= len(self.text):
            return False

        current_char = self.text[self.pos]
        return current_char in ["=", "-", "@", "#", "$", "<", "*", "_", "`"]

    def _match_heading(self) -> Optional[Token]:
        """Match heading pattern (=, ==, ===)."""
        if self.text.startswith("=", self.pos):
            level = 0
            while self.pos + level < len(self.text) and self.text[self.pos + level] == "=":
                level += 1
                if level > 6:
                    break

            if (
                level >= 1
                and self.pos + level < len(self.text)
                and self.text[self.pos + level].isspace()
            ):
                token = Token("HEADING", "=" * level, self.line, self.column)
                self.pos += level + 1
                self.column += level + 1
                return token

        return None

    def _match_list_item(self) -> Optional[Token]:
        """Match list item (- or 1.)."""
        if self.text.startswith("- ", self.pos):
            token = Token("BULLET", "- ", self.line, self.column)
            self.pos += 2
            self.column += 2
            return token

        # Match numbered list (1. 2. etc.)
        num_match = re.match(r"^(\d+)\.\s+", self.text[self.pos :])
        if num_match:
            token = Token("NUMBERED", num_match.group(), self.line, self.column)
            self.pos += len(num_match.group())
            self.column += len(num_match.group())
            return token

        return None

    def _match_figure_start(self) -> Optional[Token]:
        """Match figure start (#figure()."""
        if self.text.startswith("#figure(", self.pos):
            token = Token("FIGURE_START", "#figure(", self.line, self.column)
            self.pos += len("#figure(")
            self.column += len("#figure(")
            return token

        return None

    def _match_table_start(self) -> Optional[Token]:
        """Match table start (#table()."""
        if self.text.startswith("#table(", self.pos):
            token = Token("TABLE_START", "#table(", self.line, self.column)
            self.pos += len("#table(")
            self.column += len("#table(")
            return token

        return None

    def _match_block_math(self) -> Optional[Token]:
        """Match block math delimiters ($$)."""
        if self.text.startswith("$$", self.pos):
            token = Token("BLOCK_MATH_DELIM", "$$", self.line, self.column)
            self.pos += 2
            self.column += 2
            return token

        return None

    def _match_label(self) -> Optional[Token]:
        """Match label (<label>)."""
        if self.text.startswith("<", self.pos):
            end_pos = self.text.find(">", self.pos)
            if end_pos != -1 and end_pos - self.pos < 50:  # Reasonable label length
                label = self.text[self.pos : end_pos + 1]
                token = Token("LABEL", label, self.line, self.column)
                self.pos = end_pos + 1
                self.column = end_pos - self.pos + 1
                return token

        return None

    def _match_inline_ref(self) -> Optional[Token]:
        """Match inline reference (@fig-test, @tbl-test, @eq-test)."""
        if self.text.startswith("@", self.pos):
            # Try to match @fig-, @tbl-, @eq- followed by identifier
            ref_match = re.match(r"^@(fig|tbl|eq)-([a-zA-Z0-9_-]+)", self.text[self.pos :])
            if ref_match:
                token = Token("REF_INLINE", ref_match.group(), self.line, self.column)
                self.pos += len(ref_match.group())
                self.column += len(ref_match.group())
                return token

        return None

        current_char = self.text[self.pos]
        return current_char in ("=", "-", "@", "#", "$", "<", "*", "_", "`")

    def _match_heading(self) -> bool:
        """Match heading pattern (=, ==, ===)."""
        if self.text.startswith("=", self.pos):
            level = 0
            while self.pos + level < len(self.text) and self.text[self.pos + level] == "=":
                level += 1
                if level > 6:
                    break

            if (
                level >= 1
                and self.pos + level < len(self.text)
                and self.text[self.pos + level].isspace()
            ):
                yield Token("HEADING", "=" * level, self.line, self.column)
                self.pos += level + 1
                self.column += level + 1
                return True

        return False

    def _match_list_item(self) -> bool:
        """Match list item (- or 1.)."""
        if self.text.startswith("- ", self.pos):
            yield Token("BULLET", "- ", self.line, self.column)
            self.pos += 2
            self.column += 2
            return True

        # Match numbered list (1. 2. etc.)
        num_match = re.match(r"^(\d+)\.\s+", self.text[self.pos :])
        if num_match:
            yield Token("NUMBERED", num_match.group(), self.line, self.column)
            self.pos += len(num_match.group())
            self.column += len(num_match.group())
            return True

        return False

    def _match_figure_start(self) -> bool:
        """Match figure start (#figure()."""
        if self.text.startswith("#figure(", self.pos):
            yield Token("FIGURE_START", "#figure(", self.line, self.column)
            self.pos += len("#figure(")
            self.column += len("#figure(")
            return True

        return False

    def _match_table_start(self) -> bool:
        """Match table start (#table()."""
        if self.text.startswith("#table(", self.pos):
            yield Token("TABLE_START", "#table(", self.line, self.column)
            self.pos += len("#table(")
            self.column += len("#table(")
            return True

        return False

    def _match_block_math(self) -> bool:
        """Match block math delimiters ($$)."""
        if self.text.startswith("$$", self.pos):
            yield Token("BLOCK_MATH_DELIM", "$$", self.line, self.column)
            self.pos += 2
            self.column += 2
            return True

        return False

    def _match_label(self) -> bool:
        """Match label (<label>)."""
        if self.text.startswith("<", self.pos):
            end_pos = self.text.find(">", self.pos)
            if end_pos != -1 and end_pos - self.pos < 50:  # Reasonable label length
                label = self.text[self.pos : end_pos + 1]
                yield Token("LABEL", label, self.line, self.column)
                self.pos = end_pos + 1
                self.column = end_pos - self.pos + 1
                return True

        return False

    def _match_inline_ref(self) -> bool:
        """Match inline reference (@fig-test, @tbl-test, @eq-test)."""
        if self.text.startswith("@", self.pos):
            # Try to match @fig-, @tbl-, @eq- followed by identifier
            ref_match = re.match(r"^@(fig|tbl|eq)-([a-zA-Z0-9_-]+)", self.text[self.pos :])
            if ref_match:
                yield Token("REF_INLINE", ref_match.group(), self.line, self.column)
                self.pos += len(ref_match.group())
                self.column += len(ref_match.group())
                return True

        return False
