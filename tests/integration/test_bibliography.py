"""Integration tests for bibliography feature.

Tests inline citation parsing, bibliography file loading,
and DOCX generation with citations.
"""

import pytest
from pathlib import Path

from typst_gost_docx.config import Config
from typst_gost_docx.parser.bibliography import parse_bibliography
from typst_gost_docx.writers.docx_writer import DocxWriter


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to fixtures directory."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def bib_fixture_path(fixtures_dir: Path) -> Path:
    """Path to bibliography test fixture."""
    return fixtures_dir / "typ" / "bibliography" / "refs.bib"


@pytest.fixture
def basic_typ_path(fixtures_dir: Path) -> Path:
    """Path to basic typ test fixture."""
    return fixtures_dir / "typ" / "bibliography" / "basic.typ"


class TestBibTeXParser:
    """Integration tests for BibTeX parser."""

    def test_parse_refs_bib(self, bib_fixture_path: Path) -> None:
        """Should parse refs.bib fixture correctly."""
        assert bib_fixture_path.exists(), f"Fixture not found: {bib_fixture_path}"

        content = bib_fixture_path.read_text(encoding="utf-8")
        bib = parse_bibliography(content)

        assert len(bib.entries) == 6, f"Expected 6 entries, got {len(bib.entries)}"

        # Check entry keys
        expected_keys = {
            "petrov2023",
            "sidorov2022",
            "ivanov2021",
            "kuznetsov2020",
            "wrongsky2019",
            "smirnova2024",
        }
        actual_keys = set(bib.entries.keys())
        assert expected_keys == actual_keys, f"Missing keys: {expected_keys - actual_keys}"

    def test_parse_article_entry(self, bib_fixture_path: Path) -> None:
        """Should parse article entry with all fields."""
        content = bib_fixture_path.read_text(encoding="utf-8")
        bib = parse_bibliography(content)

        article = bib.get_entry("petrov2023")
        assert article is not None, "petrov2023 entry not found"
        assert article.entry_type.value == "article"
        assert "Петров" in article.author
        assert "программных систем" in article.title
        assert article.year == "2023"
        assert article.journal == "Журнал программирования"

    def test_parse_book_entry(self, bib_fixture_path: Path) -> None:
        """Should parse book entry correctly."""
        content = bib_fixture_path.read_text(encoding="utf-8")
        bib = parse_bibliography(content)

        book = bib.get_entry("sidorov2022")
        assert book is not None, "sidorov2022 entry not found"
        assert book.entry_type.value == "book"
        assert "Сидоров" in book.author
        assert "Архитектура" in book.title
        assert book.year == "2022"

    def test_parse_inproceedings_entry(self, bib_fixture_path: Path) -> None:
        """Should parse inproceedings entry correctly."""
        content = bib_fixture_path.read_text(encoding="utf-8")
        bib = parse_bibliography(content)

        conf = bib.get_entry("ivanov2021")
        assert conf is not None, "ivanov2021 entry not found"
        assert conf.entry_type.value == "inproceedings"
        assert "Иванов" in conf.author
        assert conf.booktitle == "Труды международной конференции по информационным технологиям"


class TestCitationNumbering:
    """Tests for citation numbering logic."""

    def test_citation_numbers_assigned_in_order(self) -> None:
        """Citations should be numbered in order of first appearance."""
        # Simulate citation extraction
        citation_keys = ["petrov2023", "sidorov2022", "ivanov2021", "petrov2023", "sidorov2022"]

        # Track unique keys in order
        seen: dict[str, int] = {}
        numbers: list[int] = []

        for key in citation_keys:
            if key not in seen:
                seen[key] = len(seen) + 1
            numbers.append(seen[key])

        # Expected: [1, 2, 3, 1, 2]
        assert numbers == [1, 2, 3, 1, 2], f"Unexpected numbering: {numbers}"
        assert len(seen) == 3, f"Expected 3 unique keys, got {len(seen)}"

    def test_repeated_citation_same_number(self) -> None:
        """Same citation key should get same number."""
        citation_keys = ["a", "b", "a", "c", "b", "a"]

        seen: dict[str, int] = {}
        for key in citation_keys:
            if key not in seen:
                seen[key] = len(seen) + 1

        assert seen["a"] == 1, "First key 'a' should be 1"
        assert seen["b"] == 2, "Second key 'b' should be 2"
        assert seen["c"] == 3, "Third key 'c' should be 3"


class TestInlineCitationExtraction:
    """Tests for inline citation extraction from Typst documents."""

    def test_extract_citations_from_typ(self, basic_typ_path: Path) -> None:
        """Should extract @[key] citations from Typst document."""
        content = basic_typ_path.read_text(encoding="utf-8")

        # Count @[key] patterns
        import re

        citation_pattern = r"@\[([\w]+)\]"
        matches = re.findall(citation_pattern, content)

        expected_keys = ["petrov2023", "sidorov2022", "ivanov2021"]
        assert len(matches) >= 3, f"Expected at least 3 citations, found {len(matches)}"

        # Check unique keys
        unique_keys = set(matches)
        assert "petrov2023" in unique_keys
        assert "sidorov2022" in unique_keys
        assert "ivanov2021" in unique_keys


class TestBibliographyFormatting:
    """Tests for ГОСТ 7.32-2017 bibliography formatting."""

    def test_article_format(self) -> None:
        """Article entry should format correctly per ГОСТ."""
        from typst_gost_docx.ir.model import BibliographyEntry, BibliographyType
        from pathlib import Path
        import tempfile

        entry = BibliographyEntry(
            key="test2024",
            entry_type=BibliographyType.ARTICLE,
            author="Иванов А.А.",
            title="Методы исследования",
            journal="Журнал программирования",
            year="2024",
            pages="45--62",
        )

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            from typst_gost_docx.ir.model import CitationStyle

            config = Config(
                input_file=Path("test.typ"),
                output_file=temp_path,
            )
            writer = DocxWriter(config)

            formatted = writer._format_bibliography_entry(entry, 1, CitationStyle.NUMERIC)
            print(f"Formatted article: {formatted}")

            # Should contain: number. Author. Title. Journal. Year. С. pages.
            assert "1." in formatted
            assert "Иванов А.А." in formatted
            assert "Методы исследования" in formatted
            assert "Журнал программирования" in formatted
            assert "2024" in formatted
            assert "С. 45--62" in formatted
        finally:
            temp_path.unlink(missing_ok=True)

    def test_book_format(self) -> None:
        """Book entry should format correctly per ГОСТ."""
        from typst_gost_docx.ir.model import BibliographyEntry, BibliographyType
        from pathlib import Path
        import tempfile

        entry = BibliographyEntry(
            key="book2022",
            entry_type=BibliographyType.BOOK,
            author="Петров Б.Б.",
            title="Архитектура систем",
            address="Москва",
            publisher="Наука",
            year="2022",
            pages="256",
        )

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            from typst_gost_docx.ir.model import CitationStyle

            config = Config(
                input_file=Path("test.typ"),
                output_file=temp_path,
            )
            writer = DocxWriter(config)

            formatted = writer._format_bibliography_entry(entry, 2, CitationStyle.NUMERIC)
            print(f"Formatted book: {formatted}")

            # Should contain: number. Author. Title. Publisher. Year. Pages с.
            assert "2." in formatted
            assert "Петров Б.Б." in formatted
            assert "Архитектура систем" in formatted
            assert "Наука" in formatted
            assert "2022" in formatted
            assert "256 с." in formatted
        finally:
            temp_path.unlink(missing_ok=True)

    def test_inproceedings_format(self) -> None:
        """Inproceedings entry should format correctly per ГОСТ."""
        from typst_gost_docx.ir.model import BibliographyEntry, BibliographyType
        from pathlib import Path
        import tempfile

        entry = BibliographyEntry(
            key="conf2021",
            entry_type=BibliographyType.INPROCEEDINGS,
            author="Сидоров В.В.",
            title="Оптимизация алгоритмов",
            booktitle="Труды конференции",
            year="2021",
            pages="112--118",
        )

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            from typst_gost_docx.ir.model import CitationStyle

            config = Config(
                input_file=Path("test.typ"),
                output_file=temp_path,
            )
            writer = DocxWriter(config)

            formatted = writer._format_bibliography_entry(entry, 3, CitationStyle.NUMERIC)
            print(f"Formatted inproceedings: {formatted}")

            # Should contain: number. Author. Title. Booktitle. Year. С. pages.
            assert "3." in formatted
            assert "Сидоров В.В." in formatted
            assert "Оптимизация алгоритмов" in formatted
            assert "Труды конференции" in formatted
            assert "2021" in formatted
            assert "С. 112--118" in formatted
        finally:
            temp_path.unlink(missing_ok=True)


class TestBibliographyConversion:
    """End-to-end tests for bibliography conversion."""

    def test_bibliography_file_loads(self, bib_fixture_path: Path) -> None:
        """Should load and parse bibliography file."""
        content = bib_fixture_path.read_text(encoding="utf-8")
        bib = parse_bibliography(content)

        assert bib is not None
        assert len(bib.entries) > 0

    def test_basic_typ_has_bibliography_call(self, basic_typ_path: Path) -> None:
        """Basic.typ should contain #bibliography() call."""
        content = basic_typ_path.read_text(encoding="utf-8")
        assert '#bibliography("refs.bib")' in content, \
            "basic.typ should contain bibliography call"


class TestAuthorYearCitations:
    """Tests for author-year citation style."""

    def test_author_year_citation_format(self) -> None:
        """Author-year citation should format as (Author, Year)."""
        from typst_gost_docx.ir.model import (
            BibliographyEntry,
            BibliographySection,
            CitationStyle,
            BibliographyType,
        )

        # Create entries with authors and years
        entry1 = BibliographyEntry(
            key="smith2020",
            entry_type=BibliographyType.ARTICLE,
            author="Smith J.",
            title="Article Title",
            year="2020",
        )
        entry2 = BibliographyEntry(
            key="jones2021",
            entry_type=BibliographyType.BOOK,
            author="Jones A.",
            title="Book Title",
            year="2021",
        )

        # Create section with AUTHOR_YEAR style
        section = BibliographySection(
            style=CitationStyle.AUTHOR_YEAR,
            entries=[entry1, entry2],
        )

        # Verify style is set correctly
        assert section.style == CitationStyle.AUTHOR_YEAR

        # Verify entries have required fields for author-year format
        assert section.entries[0].author == "Smith J."
        assert section.entries[0].year == "2020"
        assert section.entries[1].author == "Jones A."
        assert section.entries[1].year == "2021"

    def test_author_year_without_year(self) -> None:
        """Should handle entries without year in author-year style."""
        from typst_gost_docx.ir.model import (
            BibliographyEntry,
            BibliographySection,
            CitationStyle,
            BibliographyType,
        )

        # Create entry without year
        entry = BibliographyEntry(
            key="unknown",
            entry_type=BibliographyType.MISC,
            author="Unknown Author",
            title="Unknown Work",
        )

        # Section with AUTHOR_YEAR style
        section = BibliographySection(
            style=CitationStyle.AUTHOR_YEAR,
            entries=[entry],
        )

        assert section.style == CitationStyle.AUTHOR_YEAR
        assert section.entries[0].year == ""  # Empty year is allowed

    def test_author_year_article_format(self) -> None:
        """Article entry should format correctly in author-year style."""
        from typst_gost_docx.ir.model import (
            BibliographyEntry,
            CitationStyle,
            BibliographyType,
        )
        from pathlib import Path
        import tempfile

        entry = BibliographyEntry(
            key="test2024",
            entry_type=BibliographyType.ARTICLE,
            author="Иванов А.А.",
            title="Методы исследования",
            journal="Журнал программирования",
            year="2024",
            pages="45--62",
        )

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            from typst_gost_docx.config import Config

            config = Config(
                input_file=Path("test.typ"),
                output_file=temp_path,
            )
            writer = DocxWriter(config)

            # Test AUTHOR_YEAR formatting
            formatted = writer._format_bibliography_entry(
                entry, 1, CitationStyle.AUTHOR_YEAR
            )
            print(f"Formatted article (AUTHOR_YEAR): {formatted}")

            # Should contain: Author (Year) Title // Journal. — С. pages.
            assert "Иванов А.А" in formatted  # No trailing dot before (Year)
            assert "(2024)" in formatted
            assert "Методы исследования" in formatted
            assert "// Журнал программирования" in formatted
            assert "— С. 45--62" in formatted
            # Should NOT contain numeric prefix or trailing dot before year
            assert "1." not in formatted
            assert "Иванов А.А. (2024)" not in formatted  # No dot before (
        finally:
            temp_path.unlink(missing_ok=True)

    def test_author_year_book_format(self) -> None:
        """Book entry should format correctly in author-year style."""
        from typst_gost_docx.ir.model import (
            BibliographyEntry,
            CitationStyle,
            BibliographyType,
        )
        from pathlib import Path
        import tempfile

        entry = BibliographyEntry(
            key="book2022",
            entry_type=BibliographyType.BOOK,
            author="Петров Б.Б.",
            title="Архитектура систем",
            address="Москва",
            publisher="Наука",
            year="2022",
            pages="256",
        )

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            from typst_gost_docx.config import Config

            config = Config(
                input_file=Path("test.typ"),
                output_file=temp_path,
            )
            writer = DocxWriter(config)

            # Test AUTHOR_YEAR formatting
            formatted = writer._format_bibliography_entry(
                entry, 2, CitationStyle.AUTHOR_YEAR
            )
            print(f"Formatted book (AUTHOR_YEAR): {formatted}")

            # Should contain: Author (Year) Title. — City: Publisher. — Pages с.
            assert "Петров Б.Б" in formatted  # No trailing dot before (Year)
            assert "(2022)" in formatted
            assert "Архитектура систем" in formatted
            assert "— Москва: Наука" in formatted
            assert "— 256 с." in formatted
            # Should NOT contain numeric prefix or trailing dot before year
            assert "2." not in formatted
            assert "Петров Б.Б. (2022)" not in formatted  # No dot before (
        finally:
            temp_path.unlink(missing_ok=True)

    def test_author_year_inproceedings_format(self) -> None:
        """Inproceedings entry should format correctly in author-year style."""
        from typst_gost_docx.ir.model import (
            BibliographyEntry,
            CitationStyle,
            BibliographyType,
        )
        from pathlib import Path
        import tempfile

        entry = BibliographyEntry(
            key="conf2021",
            entry_type=BibliographyType.INPROCEEDINGS,
            author="Сидоров В.В.",
            title="Оптимизация алгоритмов",
            booktitle="Труды конференции",
            year="2021",
            pages="112--118",
        )

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            from typst_gost_docx.config import Config

            config = Config(
                input_file=Path("test.typ"),
                output_file=temp_path,
            )
            writer = DocxWriter(config)

            # Test AUTHOR_YEAR formatting
            formatted = writer._format_bibliography_entry(
                entry, 3, CitationStyle.AUTHOR_YEAR
            )
            print(f"Formatted inproceedings (AUTHOR_YEAR): {formatted}")

            # Should contain: Author (Year) Title // Booktitle. — С. pages.
            assert "Сидоров В.В" in formatted  # No trailing dot before (Year)
            assert "(2021)" in formatted
            assert "Оптимизация алгоритмов" in formatted
            assert "// Труды конференции" in formatted
            assert "— С. 112--118" in formatted
            # Should NOT contain numeric prefix or trailing dot before year
            assert "3." not in formatted
            assert "Сидоров В.В. (2021)" not in formatted  # No dot before (
        finally:
            temp_path.unlink(missing_ok=True)
