"""Typst scanner for parsing."""

import re
from dataclasses import dataclass
from typing import Generator


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


class TypstScanner:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def scan(self) -> Generator[Token, None, None]:
        patterns = [
            (r"^={1,6}\s+", "HEADING"),
            (r"^-", "BULLET"),
            (r"^\d+\.", "NUMBERED"),
            (r"^\s*\n", "NEWLINE"),
            (r"#figure\(", "FIGURE_START"),
            (r"#table\(", "TABLE_START"),
            (r"\$\$", "BLOCK_MATH_DELIM"),
            (r"\$", "INLINE_MATH_DELIM"),
            (r"<(\w+)>", "LABEL"),
            (r"@(\w+)", "REF"),
            (r"\*(.+?)\*", "EMPHASIS"),
            (r"_(.+?)_", "STRONG"),
            (r"`[^`]+`", "INLINE_CODE"),
            (r'#include\s+"([^"]+)"', "INCLUDE"),
            (r'#import\s+"([^"]+)"', "IMPORT"),
        ]

        while self.pos < len(self.text):
            matched = False

            for pattern, token_type in patterns:
                if token_type.startswith("INLINE"):
                    regex = re.compile(pattern)
                    match = regex.search(self.text[self.pos :])
                    if match:
                        yield Token(token_type, match.group(), self.line, self.column)
                        self.pos += match.end()
                        self.column += match.end()
                        matched = True
                        break
                else:
                    regex = re.compile(pattern, re.MULTILINE)
                    match = regex.match(self.text[self.pos :])
                    if match:
                        yield Token(token_type, match.group(), self.line, self.column)
                        lines = match.group().count("\n")
                        self.line += lines
                        self.pos += match.end()
                        self.column = 1
                        matched = True
                        break

            if not matched:
                if self.text[self.pos] == "\n":
                    self.line += 1
                    self.pos += 1
                    self.column = 1
                else:
                    self.pos += 1
                    self.column += 1
