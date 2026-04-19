"""Typst scanner for parsing - finds tokens in order."""

import re
from typing import Generator, List, Tuple

from pydantic import BaseModel


class Token(BaseModel):
    """Token from Typst source scanning."""

    type: str
    value: str
    line: int
    column: int

    # Allow positional args for backward compatibility with dataclass
    def __init__(
        self, type: str = "", value: str = "", line: int = 0, column: int = 0, **kwargs: object
    ) -> None:
        super().__init__(type=type, value=value, line=line, column=column, **kwargs)


class TypstScanner:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self._tokens: List[Token] = []

    def scan(self) -> Generator[Token, None, None]:
        """Scan Typst text and yield tokens in order."""
        # Pattern groups with their token types - more specific first
        patterns = [
            ("FIGURE_START", r"#figure\("),
            ("TABLE_START", r"#table\("),  # standalone
            ("TABLE_START", r"(\n  table\()"),  # nested (normalize)
            ("OUTLINE_START", r"#outline\("),
            ("HEADING", r"={1,6}\s+"),
            ("BULLET", r"-\s"),
            ("NUMBERED", r"\d+\.\s"),
            ("NEWLINE", r"\n"),
            ("LABEL", r"<([\w:-]+)>"),
            ("REF", r"@[a-zA-Z0-9_-]+"),
            ("REF_INLINE", r"@(fig|tbl|eq)-([a-zA-Z0-9_-]+)"),
            ("BLOCK_MATH_DELIM", r"\$\$"),
            ("INLINE_MATH_DELIM", r"\$"),
            ("EMPHASIS", r"\*(.+?)\*"),
            ("STRONG", r"_(.+?)_"),
            ("INLINE_CODE", r"`[^`]+`"),
            ("INCLUDE", r'#include\s+"([^"]+)"'),
            ("IMPORT", r'#import\s+"([^"]+)"'),
        ]

        # Find all matches
        all_matches: List[Tuple[int, int, str, str]] = []

        for token_type, pattern in patterns:
            regex = re.compile(pattern)
            for m in regex.finditer(self.text):
                all_matches.append((m.start(), m.end(), token_type, m.group()))

        # Sort by position, then by priority (important tokens first at same pos)
        priority = {"FIGURE_START": 0, "TABLE_START": 1}
        all_matches.sort(key=lambda x: (x[0], priority.get(x[2], 99)))

        # Remove overlaps but keep same-pos tokens
        pos = 0
        for start, end, ttype, value in all_matches:
            if start < pos:
                continue  # Skip overlap completely inside

            # If there's text between previous token and this one
            if start > pos:
                gap = self.text[pos:start]
                yield Token("TEXT", gap, self.line, self.column)
                # Update line/col for gap
                newline_count = gap.count("\n")
                self.line += newline_count
                if newline_count:
                    # Simple approximation
                    self.column = len(gap) - gap.rfind("\n")
                else:
                    self.column += len(gap)

            # Yield the token
            if ttype == "TABLE_START" and value.startswith("\n"):
                value = "#table("  # normalize nested to standard

            yield Token(ttype, value, self.line, self.column)

            pos = end
            # Update line/col after token
            newline_count = value.count("\n")
            self.line += newline_count
            if newline_count:
                self.column = 1
            else:
                self.column = end - start

        # Final TEXT for any remaining
        if pos < len(self.text):
            yield Token("TEXT", self.text[pos:], self.line, self.column)
