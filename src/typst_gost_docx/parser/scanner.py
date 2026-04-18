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
            ("HEADING", r"={1,6}\s+"),
            ("BULLET", r"-\s"),
            ("NUMBERED", r"\d+\.\s"),
            ("NEWLINE", r"\s*\n"),
            ("FIGURE_START", r"#figure\("),
            ("TABLE_START", r"#table\("),
            ("BLOCK_MATH_DELIM", r"\$\$"),
            ("INLINE_MATH_DELIM", r"\$"),
            ("LABEL", r"<([a-zA-Z0-9_-]+)>"),
            ("REF_INLINE", r"@(fig|tbl|eq)-([a-zA-Z0-9_-]+)"),
            ("EMPHASIS", r"\*(.+?)\*"),
            ("STRONG", r"_(.+?)_"),
            ("INLINE_CODE", r"`[^`]+`"),
            ("INCLUDE", r'#include\s+"([^"]+)"'),
            ("IMPORT", r'#import\s+"([^"]+)"'),
        ]

        while self.pos < len(self.text):
            matched = False

            # First, check if we're at the start of a line and can match line-start patterns
            if self.column == 1:
                for token_type, pattern in patterns:
                    if token_type in ("HEADING", "BULLET", "NUMBERED"):
                        regex = re.compile(pattern)
                        match = regex.match(self.text[self.pos :])
                        if match:
                            yield Token(token_type, match.group(), self.line, self.column)
                            lines = match.group().count("\n")
                            self.line += lines
                            self.pos += match.end()
                            self.column = 1
                            matched = True
                            break
                    elif token_type == "NEWLINE":
                        regex = re.compile(pattern, re.MULTILINE)
                        match = regex.match(self.text[self.pos :])
                        if match and match.group() != "":
                            yield Token(token_type, match.group(), self.line, self.column)
                            lines = match.group().count("\n")
                            self.line += lines
                            self.pos += match.end()
                            self.column = 1
                            matched = True
                            break

                if matched:
                    continue

            # Now try to match other patterns (FIGURE, TABLE, MATH, etc.)
            for token_type, pattern in patterns:
                if token_type in ("HEADING", "BULLET", "NUMBERED"):
                    continue  # Already handled above

                regex = re.compile(pattern)
                match = regex.match(self.text[self.pos :])
                if match:
                    yield Token(token_type, match.group(), self.line, self.column)
                    if token_type == "NEWLINE":
                        lines = match.group().count("\n")
                        self.line += lines
                        self.pos += match.end()
                        self.column = 1
                    else:
                        self.pos += match.end()
                        self.column += match.end()
                    matched = True
                    break

            if not matched:
                # Collect consecutive text characters (until pattern or newline)
                text_start = self.pos
                while self.pos < len(self.text) and self.text[self.pos] != "\n":
                    # Check if current position starts any pattern (except line-start patterns)
                    starts_pattern = False
                    for token_type, pattern in patterns:
                        if token_type in ("HEADING", "BULLET", "NUMBERED", "NEWLINE"):
                            continue
                        regex = re.compile(pattern)
                        if regex.match(self.text[self.pos :]):
                            starts_pattern = True
                            break

                    if starts_pattern:
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
                else:
                    # Single character couldn't be matched - yield as TEXT and advance
                    yield Token("TEXT", self.text[self.pos : self.pos + 1], self.line, self.column)
                    self.pos += 1
                    self.column += 1
