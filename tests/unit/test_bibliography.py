"""Unit tests for Bibliography IR models.

Tests for BibliographyEntry, CitationNode, BibliographySection,
and CitationStyle/BibliographyType enums.
"""


from typst_gost_docx.ir.model import (
    BibliographyEntry,
    BibliographySection,
    BibliographyType,
    CitationNode,
    CitationStyle,
)


class TestBibliographyType:
    """Tests for BibliographyType enum."""

    def test_article_value(self) -> None:
        """Article type should have correct value."""
        assert BibliographyType.ARTICLE.value == "article"

    def test_book_value(self) -> None:
        """Book type should have correct value."""
        assert BibliographyType.BOOK.value == "book"

    def test_inproceedings_value(self) -> None:
        """Inproceedings type should have correct value."""
        assert BibliographyType.INPROCEEDINGS.value == "inproceedings"

    def test_techreport_value(self) -> None:
        """Techreport type should have correct value."""
        assert BibliographyType.TECHREPORT.value == "techreport"

    def test_misc_value(self) -> None:
        """Misc type should have correct value."""
        assert BibliographyType.MISC.value == "misc"

    def test_all_types_defined(self) -> None:
        """All expected BibTeX entry types should be defined."""
        expected_types = {
            "article",
            "book",
            "inproceedings",
            "techreport",
            "misc",
            "phdthesis",
            "mastersthesis",
        }
        actual_values = {bt.value for bt in BibliographyType}
        assert expected_types == actual_values


class TestCitationStyle:
    """Tests for CitationStyle enum."""

    def test_numeric_value(self) -> None:
        """Numeric style should have correct value."""
        assert CitationStyle.NUMERIC.value == "numeric"

    def test_author_year_value(self) -> None:
        """Author-year style should have correct value."""
        assert CitationStyle.AUTHOR_YEAR.value == "author_year"


class TestBibliographyEntry:
    """Tests for BibliographyEntry model."""

    def test_create_minimal_entry(self) -> None:
        """Should create entry with minimal required fields."""
        entry = BibliographyEntry(
            key="test2024",
            entry_type=BibliographyType.ARTICLE,
            author="Иванов А.А.",
            title="Тестовая статья",
        )
        assert entry.key == "test2024"
        assert entry.entry_type == BibliographyType.ARTICLE
        assert entry.author == "Иванов А.А."
        assert entry.title == "Тестовая статья"

    def test_create_full_entry(self) -> None:
        """Should create entry with all fields."""
        entry = BibliographyEntry(
            key="full2024",
            entry_type=BibliographyType.BOOK,
            author="Петров Б.Б.",
            title="Полное руководство",
            year="2024",
            journal="",
            booktitle="",
            publisher="Наука",
            address="Москва",
            pages="256",
            volume="1",
            number="",
            doi="10.1234/test",
            url="https://example.com",
        )
        assert entry.year == "2024"
        assert entry.publisher == "Наука"
        assert entry.pages == "256"
        assert entry.doi == "10.1234/test"

    def test_default_entry_type(self) -> None:
        """Default entry type should be MISC."""
        entry = BibliographyEntry(key="test", title="Test")
        assert entry.entry_type == BibliographyType.MISC

    def test_empty_fields_defaults(self) -> None:
        """Empty optional fields should default to empty string."""
        entry = BibliographyEntry(key="test", title="Test")
        assert entry.year == ""
        assert entry.journal == ""
        assert entry.pages == ""


class TestCitationNode:
    """Tests for CitationNode model."""

    def test_create_citation(self) -> None:
        """Should create citation with key and number."""
        citation = CitationNode(key="petrov2023", number=1)
        assert citation.key == "petrov2023"
        assert citation.number == 1
        assert citation.node_type.value == "citation"

    def test_citation_with_zero_number(self) -> None:
        """Citation number should be int, can be 0 (unassigned)."""
        citation = CitationNode(key="unknown")
        assert citation.number == 0

    def test_citation_default_values(self) -> None:
        """Citation should have sensible defaults."""
        citation = CitationNode()
        assert citation.key == ""
        assert citation.number == 0


class TestBibliographySection:
    """Tests for BibliographySection model."""

    def test_create_bibliography_section(self) -> None:
        """Should create bibliography section with entries."""
        entry1 = BibliographyEntry(
            key="a1",
            entry_type=BibliographyType.ARTICLE,
            author="Автор А.",
            title="Статья 1",
        )
        entry2 = BibliographyEntry(
            key="b2",
            entry_type=BibliographyType.BOOK,
            author="Автор Б.",
            title="Книга 2",
        )
        section = BibliographySection(
            heading="Список литературы",
            entries=[entry1, entry2],
            style=CitationStyle.NUMERIC,
        )
        assert len(section.entries) == 2
        assert section.heading == "Список литературы"
        assert section.style == CitationStyle.NUMERIC
        assert section.node_type.value == "bibliography_section"

    def test_default_heading(self) -> None:
        """Default heading should be Russian 'Список литературы'."""
        section = BibliographySection()
        assert section.heading == "Список литературы"

    def test_default_style(self) -> None:
        """Default style should be NUMERIC."""
        section = BibliographySection()
        assert section.style == CitationStyle.NUMERIC

    def test_empty_entries_default(self) -> None:
        """Entries should default to empty list."""
        section = BibliographySection()
        assert section.entries == []


class TestAuthorYearStyle:
    """Tests for AUTHOR_YEAR citation style."""

    def test_citation_style_enum_has_author_year(self) -> None:
        """AUTHOR_YEAR style should exist in CitationStyle enum."""
        assert CitationStyle.AUTHOR_YEAR.value == "author_year"

    def test_bibliography_section_with_author_year_style(self) -> None:
        """Should create bibliography section with AUTHOR_YEAR style."""
        section = BibliographySection(style=CitationStyle.AUTHOR_YEAR)
        assert section.style == CitationStyle.AUTHOR_YEAR
        assert section.node_type.value == "bibliography_section"

    def test_citation_node_with_author_year_style(self) -> None:
        """CitationNode should work with author-year style."""
        citation = CitationNode(key="smith2020", number=1)
        assert citation.key == "smith2020"
        assert citation.number == 1
        assert citation.node_type.value == "citation"

    def test_bibliography_section_with_entries_author_year(self) -> None:
        """Should create bibliography section with entries and AUTHOR_YEAR style."""
        entry1 = BibliographyEntry(
            key="ivanov2024",
            entry_type=BibliographyType.ARTICLE,
            author="Иванов А.А.",
            title="Новая статья",
            year="2024",
        )
        entry2 = BibliographyEntry(
            key="petrov2023",
            entry_type=BibliographyType.BOOK,
            author="Петров Б.Б.",
            title="Новая книга",
            year="2023",
        )
        section = BibliographySection(
            heading="Список литературы",
            entries=[entry1, entry2],
            style=CitationStyle.AUTHOR_YEAR,
        )
        assert len(section.entries) == 2
        assert section.style == CitationStyle.AUTHOR_YEAR
        assert section.entries[0].year == "2024"
        assert section.entries[1].year == "2023"
