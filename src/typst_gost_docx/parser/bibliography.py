"""BibTeX parser for bibliography support.

This module provides functionality for parsing BibTeX (.bib) files
and extracting bibliographic entries.

BibTeX format overview:
- Entries start with @TYPE{key, where TYPE is article, book, etc.
- Fields are specified as field_name = {value} or field_name = "value"
- Entries end with }
- Comments may appear as %% or % at start of line
"""

import re
from typing import Optional

from ..ir.model import BibliographyEntry, BibliographyType


class BibliographyFile:
    """Container for loaded BibTeX file with all entries.

    Attributes:
        path: Path to the .bib file.
        entries: Dictionary mapping citation keys to BibliographyEntry objects.
        parse_errors: List of warning messages for malformed entries.
    """

    def __init__(self, path: str) -> None:
        """Initialize BibliographyFile.

        Args:
            path: Path to the .bib file.
        """
        self.path: str = path
        self.entries: dict[str, BibliographyEntry] = {}
        self.parse_errors: list[str] = []

    def get_entry(self, key: str) -> Optional[BibliographyEntry]:
        """Get a bibliography entry by key.

        Args:
            key: Citation key.

        Returns:
            BibliographyEntry if found, None otherwise.
        """
        return self.entries.get(key)

    def add_entry(self, entry: BibliographyEntry) -> None:
        """Add an entry to the bibliography.

        Args:
            entry: BibliographyEntry to add.
        """
        if entry.key in self.entries:
            self.parse_errors.append(
                f"Duplicate key '{entry.key}' - using first occurrence"
            )
            return  # Keep first occurrence, skip duplicates
        self.entries[entry.key] = entry


def _parse_entry_type(entry_type_str: str) -> BibliographyType:
    """Parse BibTeX entry type string to BibliographyType enum.

    Поддерживаемые типы записей BibTeX:
    - article: Статья в журнале
    - book: Книга (монография)
    - inproceedings: Материалы конференции
    - conference: Синоним для inproceedings
    - techreport: Технический отчёт
    - misc: Разное (для записей без специфического типа)
    - phdthesis: PhD диссертация
    - mastersthesis: Магистерская диссертация

    Args:
        entry_type_str: Lowercase entry type string (e.g., "article").

    Returns:
        Corresponding BibliographyType enum value.
    """
    # Mapping of BibTeX entry types to BibliographyType enum values
    # Includes common aliases (e.g., "conference" → "inproceedings")
    type_mapping: dict[str, BibliographyType] = {
        "article": BibliographyType.ARTICLE,
        "book": BibliographyType.BOOK,
        "inproceedings": BibliographyType.INPROCEEDINGS,
        "conference": BibliographyType.INPROCEEDINGS,  # Alias for inproceedings
        "techreport": BibliographyType.TECHREPORT,
        "misc": BibliographyType.MISC,
        "phdthesis": BibliographyType.PHDTHESIS,
        "mastersthesis": BibliographyType.MASTERSTHESIS,
    }
    # Convert to lowercase for case-insensitive matching
    # Default to MISC if type is not recognized
    return type_mapping.get(entry_type_str.lower(), BibliographyType.MISC)


def _strip_latex_commands(text: str) -> str:
    """Strip LaTeX commands from text, keeping the content.

    Удаляет команды форматирования LaTeX, сохраняя только текстовое содержимое.
    Это позволяет корректно отображать библиографические записи в DOCX без LaTeX-синтаксиса.

    Обрабатываемые команды:
    - \textbf{...} - жирный шрифт
    - \textit{...} - курсив
    - \emph{...} - акцент
    - \textsc{...} - капитель
    - Общие команды вида \command{content}

    Args:
        text: Text potentially containing LaTeX commands.

    Returns:
        Text with LaTeX commands removed.
    """
    # Remove specific text formatting commands (preserve content inside braces)
    # Pattern: \\text*{content} → content
    text = re.sub(r'\\text\w+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]*)\}', r'\1', text)

    # Remove general LaTeX commands with braces
    # Pattern: \\command{content} → content
    text = re.sub(r'\\\w+\{([^}]*)\}', r'\1', text)

    # Remove LaTeX commands without braces (e.g., \& \% etc.)
    # Pattern: \\command → empty string
    text = re.sub(r'\\[a-zA-Z]+', '', text)

    # Clean up extra whitespace (multiple spaces → single space)
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    return text.strip()


def _parse_bibtex_value(value: str) -> str:
    """Parse and clean a BibTeX field value.

    Выполняет очистку значения поля BibTeX:
    1. Удаляет кавычки или фигурные скобки
    2. Разэкранирует специальные символы BibTeX
    3. Преобразует специальные символы (например, ~ → пробел, -- → –)
    4. Удаляет команды LaTeX

    Args:
        value: Raw BibTeX field value.

    Returns:
        Cleaned string value suitable for display in DOCX.
    """
    # Remove surrounding braces {...} or quotes "..."
    value = value.strip()
    if (value.startswith('{') and value.endswith('}')) or \
       (value.startswith('"') and value.endswith('"')):
        value = value[1:-1]

    # Unescape common BibTeX special characters
    # In BibTeX, these characters are escaped with backslash
    value = value.replace('\\&', '&')
    value = value.replace('\\#', '#')
    value = value.replace('\\%', '%')
    value = value.replace('\\$', '$')
    value = value.replace('\\{', '{')
    value = value.replace('\\}', '}')
    # Tilde is non-breaking space in LaTeX, replace with regular space
    value = value.replace('~', ' ')
    # Double dash in LaTeX is en dash (–) for page ranges
    value = value.replace('--', '–')

    # Remove LaTeX accent commands (e.g., \`a → a, \"o → o, ^e → e)
    # Pattern: \\[accent]letter → letter
    value = re.sub(r'\\["\'`^~=.uvHtcdb](\w)', r'\1', value)

    # Strip LaTeX formatting commands (e.g., \textbf, \textit)
    value = _strip_latex_commands(value)

    # Final strip to remove any remaining whitespace
    return value.strip()


class BibTeXParser:
    """Parser for BibTeX format files.

    Parses .bib files and extracts bibliographic entries with their fields.
    Supports article, book, inproceedings, techreport, misc entry types.
    Handles Cyrillic characters and basic LaTeX command stripping.
    """

    # Regex patterns for parsing BibTeX
    ENTRY_PATTERN = re.compile(
        r'@(\w+)\s*\{\s*([^,\s]+)\s*,',
        re.IGNORECASE | re.MULTILINE
    )
    FIELD_PATTERN = re.compile(
        r'(\w+)\s*=\s*'
        r'(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|"([^"]*)"|([^\s,]+))',
        re.MULTILINE | re.DOTALL
    )

    def __init__(self) -> None:
        """Initialize BibTeXParser."""
        self.entries: list[BibliographyEntry] = []
        self.errors: list[str] = []

    def parse(self, content: str) -> BibliographyFile:
        """Parse BibTeX content from a string.

        Основной метод парсинга BibTeX-файла:
        1. Удаляет комментарии (% и %% в начале строк)
        2. Находит все записи с помощью ENTRY_PATTERN regex
        3. Для каждой записи извлекает поля с помощью FIELD_PATTERN regex
        4. Создаёт BibliographyEntry для каждой записи
        5. Добавляет записи в BibliographyFile

        Args:
            content: Raw BibTeX file content.

        Returns:
            BibliographyFile containing all parsed entries.
        """
        # Step 1: Remove comments (lines starting with % or %%)
        # BibTeX comments start with % (single or double percent sign)
        lines: list[str] = []
        for line in content.split('\n'):
            # Remove inline comments (comment after text on same line)
            if '%' in line:
                comment_pos = line.index('%')
                # Check if it's a LaTeX comment (not a percent in a string)
                # In BibTeX, % inside braces is not a comment
                if comment_pos == 0 or line[:comment_pos].count('{') == line[:comment_pos].count('}'):
                    line = line[:comment_pos]
            line = line.rstrip()
            if line and not line.startswith('%%'):
                lines.append(line)
        content = '\n'.join(lines)

        # Initialize result object
        bibliography = BibliographyFile("")
        self.entries = []
        self.errors = []

        # Step 2: Find all entries using ENTRY_PATTERN regex
        # Pattern: @TYPE{key, ...fields... }
        for match in self.ENTRY_PATTERN.finditer(content):
            entry_type_str = match.group(1)
            key = match.group(2).strip()

            # Step 3: Find the entry body (everything between the key and closing brace)
            # Use brace counting to handle nested braces in field values
            start = match.end()
            brace_count = 1
            end = start
            for i, char in enumerate(content[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i
                        break

            entry_body = content[start:end]

            # Step 4: Parse fields using FIELD_PATTERN regex
            # Pattern: field_name = {value} or field_name = "value"
            fields: dict[str, str] = {}
            for field_match in self.FIELD_PATTERN.finditer(entry_body):
                field_name = field_match.group(1).lower()
                # Get value from whichever group matched (braces, quotes, or plain text)
                field_value = field_match.group(2) or field_match.group(3) or field_match.group(4) or ""
                fields[field_name] = _parse_bibtex_value(field_value)

            # Step 5: Create BibliographyEntry
            entry = BibliographyEntry(
                key=key,
                entry_type=_parse_entry_type(entry_type_str),
                author=fields.get('author', ''),
                title=fields.get('title', ''),
                year=fields.get('year', ''),
                journal=fields.get('journal', ''),
                booktitle=fields.get('booktitle', ''),
                publisher=fields.get('publisher', ''),
                address=fields.get('address', ''),
                pages=fields.get('pages', ''),
                volume=fields.get('volume', ''),
                number=fields.get('number', ''),
                doi=fields.get('doi', ''),
                url=fields.get('url', ''),
            )

            # Validate required fields (at least author or title should be present)
            if not entry.author and not entry.title:
                self.errors.append(
                    f"Entry '{key}' is missing both author and title"
                )

            # Add entry to results
            self.entries.append(entry)
            bibliography.add_entry(entry)

        # Copy errors to bibliography file
        bibliography.parse_errors = self.errors
        return bibliography


def parse_bibliography(content: str) -> BibliographyFile:
    """Parse BibTeX content and return BibliographyFile.

    Args:
        content: Raw BibTeX file content.

    Returns:
        BibliographyFile containing all parsed entries.
    """
    parser = BibTeXParser()
    return parser.parse(content)
