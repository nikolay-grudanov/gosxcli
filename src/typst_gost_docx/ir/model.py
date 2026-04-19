"""Intermediate Representation models for document conversion.

This module defines the IR (Intermediate Representation) data structures
for converting Typst documents to DOCX format.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Types of nodes in the IR tree."""

    DOCUMENT = "document"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    LIST_BLOCK = "list_block"
    LIST_ITEM = "list_item"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    FIGURE = "figure"
    EQUATION = "equation"
    MATH = "math"
    TEXT_RUN = "text_run"
    INLINE_RUN = "inline_run"
    INLINE_CODE = "inline_code"
    INLINE_MATH = "inline_math"
    BOOKMARK = "bookmark"
    CROSS_REFERENCE = "cross_reference"
    CROSS_REF = "cross_ref"
    TABLE_HEADER = "table_header"
    TOC = "toc"
    CITATION = "citation"
    BIBLIOGRAPHY_SECTION = "bibliography_section"


class ListKind(str, Enum):
    """Kind of list (bullet or numbered)."""

    BULLET = "bullet"
    NUMBERED = "numbered"


class NumberingKind(str, Enum):
    """Numbering kind for figures, tables, equations, sections."""

    FIGURE = "figure"
    TABLE = "table"
    EQUATION = "equation"
    SECTION = "section"


class MathRenderMode(str, Enum):
    """Rendering mode for mathematical expressions."""

    NATIVE = "native"
    IMAGE = "image"
    FALLBACK = "fallback"


class BibliographyType(str, Enum):
    """Types of bibliographic entries (BibTeX entry types)."""

    ARTICLE = "article"
    BOOK = "book"
    INPROCEEDINGS = "inproceedings"
    TECHREPORT = "techreport"
    MISC = "misc"
    PHDTHESIS = "phdthesis"
    MASTERSTHESIS = "mastersthesis"


class CitationStyle(str, Enum):
    """Citation style for inline references."""

    NUMERIC = "numeric"
    AUTHOR_YEAR = "author_year"


class SourceLocation(BaseModel):
    """Source location information for debugging."""

    file_path: str
    line: int
    column: int = 0
    end_line: Optional[int] = None
    end_column: Optional[int] = None


class BaseNode(BaseModel):
    """Base class for all IR nodes."""

    id: str = ""
    node_type: NodeType = NodeType.DOCUMENT
    label: Optional[str] = None
    source_location: Optional[SourceLocation] = None
    style_hints: dict[str, Any] = Field(default_factory=dict)


class Document(BaseNode):
    """Root document node."""

    node_type: NodeType = NodeType.DOCUMENT
    metadata: dict[str, Any] = Field(default_factory=dict)
    blocks: list["IRNode"] = Field(default_factory=list)


class Section(BaseNode):
    """Section or heading node."""

    node_type: NodeType = NodeType.SECTION
    level: int = 1
    title: list["IRNode"] = Field(default_factory=list)
    blocks: list["IRNode"] = Field(default_factory=list)
    numbering_kind: Optional[NumberingKind] = NumberingKind.SECTION
    number: int = 0
    chapter_number: int = 0


class Paragraph(BaseNode):
    """Paragraph node with inline runs.

    Uses a list of InlineNode runs instead of plain text content
    to support inline formatting (bold, italic, underline, code, math).

    Provides backward compatibility for code that accesses `content` field
    by reconstructing text from runs when explicit content is not set.

    Attributes:
        node_type: Node type (paragraph).
        runs: List of inline nodes for rich text formatting.
    """

    node_type: NodeType = NodeType.PARAGRAPH
    runs: list["InlineNode"] = Field(default_factory=list)
    _content: str = ""

    @property
    def content(self) -> str:
        """Get paragraph text content.

        Returns explicit content if set, otherwise reconstructs from runs.

        Returns:
            The text content of the paragraph.
        """
        if self._content:
            return self._content
        if self.runs:
            return "".join(self._extract_text_from_run(run) for run in self.runs)
        return ""

    @content.setter
    def content(self, value: str) -> None:
        """Set paragraph text content.

        Args:
            value: The text content to set.
        """
        self._content = value

    @staticmethod
    def _extract_text_from_run(node: "InlineNode") -> str:
        """Extract text from an inline node.

        Args:
            node: An inline node (TextRun, InlineRunNode, InlineCodeNode, etc).

        Returns:
            The text content of the node.
        """
        if hasattr(node, "text"):
            return node.text
        if hasattr(node, "code"):
            return node.code
        if hasattr(node, "latex"):
            return node.latex
        if hasattr(node, "name"):
            return node.name
        if hasattr(node, "target_label"):
            return node.target_label or ""
        return ""


class ListBlock(BaseNode):
    """List block node."""

    node_type: NodeType = NodeType.LIST_BLOCK
    kind: ListKind = ListKind.BULLET
    items: list["ListItem"] = Field(default_factory=list)


class ListItem(BaseNode):
    """List item node."""

    node_type: NodeType = NodeType.LIST_ITEM
    content: list["IRNode"] = Field(default_factory=list)


class ColSpec(BaseModel):
    """Column specification for tables."""

    width: Optional[float] = None
    width_percent: Optional[float] = None
    align: Optional[str] = None


class TableHeaderNode(BaseNode):
    """Table header row node."""

    node_type: NodeType = NodeType.TABLE_HEADER
    cells: list["TableCellNode"] = Field(default_factory=list)


class TableCellNode(BaseNode):
    """Table cell node with colspan/rowspan support."""

    node_type: NodeType = NodeType.TABLE_CELL
    content: list["IRNode"] = Field(default_factory=list)
    colspan: int = 1
    rowspan: int = 1
    align: Optional[str] = None
    fill: Optional[str] = None


class TableNode(BaseNode):
    """Table node with column specifications."""

    node_type: NodeType = NodeType.TABLE
    columns: list[ColSpec] = Field(default_factory=list)
    header: Optional[TableHeaderNode] = None
    rows: list[list["TableCellNode"]] = Field(default_factory=list)
    has_header: bool = False
    caption: Optional["Caption"] = None
    numbering_kind: Optional[NumberingKind] = NumberingKind.TABLE
    number: int = 0
    chapter_number: int = 0
    border_width: float = 0.0  # Stroke width in points


class Figure(BaseNode):
    """Figure node.

    Can contain either an image or a table (but not both).
    """

    node_type: NodeType = NodeType.FIGURE
    caption: Optional["Caption"] = None
    image_path: Optional[str] = None
    table: Optional["TableNode"] = None  # Nested table inside figure
    numbering_kind: Optional[NumberingKind] = NumberingKind.FIGURE
    number: int = 0
    chapter_number: int = 0


class Caption(BaseNode):
    """Caption for figures, tables, equations."""

    node_type: NodeType = NodeType.PARAGRAPH
    text: str = ""
    numbering_kind: Optional[NumberingKind] = None
    number: int = 0
    chapter_number: int = 0


class Equation(BaseNode):
    """Block equation node."""

    node_type: NodeType = NodeType.EQUATION
    latex: str = ""
    caption: Optional[Caption] = None
    numbering_kind: Optional[NumberingKind] = NumberingKind.EQUATION
    number: int = 0
    chapter_number: int = 0


class MathNode(BaseNode):
    """Math expression node with rendering mode.

    Represents a mathematical expression (inline or block) in the document.
    Supports different rendering modes and tracks rendering errors.

    Attributes:
        content: The LaTeX content of the mathematical expression.
        render_mode: Rendering mode - "native" for OMML, "image" for image fallback,
            "fallback" for text fallback when rendering fails.
        render_error: Error message if rendering failed, None otherwise.
        display_mode: Whether this is a block equation (display math) vs inline.
    """

    node_type: NodeType = NodeType.MATH
    content: str = ""
    display_mode: bool = False
    render_mode: MathRenderMode = MathRenderMode.NATIVE
    render_error: Optional[str] = None


class TextRun(BaseNode):
    """Plain text run node."""

    node_type: NodeType = NodeType.TEXT_RUN
    text: str = ""


class InlineRunNode(BaseNode):
    """Inline text run with formatting."""

    node_type: NodeType = NodeType.INLINE_RUN
    text: str = ""
    bold: bool = False
    italic: bool = False
    underline: bool = False


class InlineCodeNode(BaseNode):
    """Inline code node."""

    node_type: NodeType = NodeType.INLINE_CODE
    code: str = ""


class InlineMathNode(BaseNode):
    """Inline math expression."""

    node_type: NodeType = NodeType.INLINE_MATH
    latex: str = ""
    render_mode: MathRenderMode = MathRenderMode.NATIVE


class Bookmark(BaseNode):
    """Bookmark node for DOCX references."""

    node_type: NodeType = NodeType.BOOKMARK
    name: str = ""


class CrossReference(BaseNode):
    """Legacy cross-reference node."""

    node_type: NodeType = NodeType.CROSS_REFERENCE
    target_label: str = ""
    ref_text: Optional[str] = None


class CrossRefNode(BaseNode):
    """Cross-reference node with chapter-aware numbering."""

    node_type: NodeType = NodeType.CROSS_REF
    target_label: str = ""
    ref_kind: Optional[str] = None
    ref_text: Optional[str] = None
    number: int = 0
    chapter_number: int = 0


class TOCNode(BaseNode):
    """Table of Contents node.

    Represents a #outline() call in Typst that generates a table of contents.

    Attributes:
        node_type: Node type (toc).
        title: Title for the TOC (default: "Содержание").
    """

    node_type: NodeType = NodeType.TOC
    title: str = "Содержание"


class BibliographyEntry(BaseNode):
    """Single bibliographic entry from BibTeX file.

    Represents a single bibliographic reference with all its metadata.

    Attributes:
        key: Unique citation key (e.g., "smith2020").
        entry_type: Type of bibliographic entry (article, book, etc.).
        author: Author name(s).
        title: Title of the work.
        year: Publication year.
        journal: Journal name (for articles).
        booktitle: Book title (for inproceedings).
        publisher: Publisher name.
        address: City/location of publication.
        pages: Page range (e.g., "12-25").
        volume: Volume number.
        number: Issue number.
        doi: Digital Object Identifier.
        url: Web URL.
    """

    key: str = ""
    entry_type: BibliographyType = BibliographyType.MISC
    author: str = ""
    title: str = ""
    year: str = ""
    journal: str = ""
    booktitle: str = ""
    publisher: str = ""
    address: str = ""
    pages: str = ""
    volume: str = ""
    number: str = ""
    doi: str = ""
    url: str = ""


class CitationNode(BaseNode):
    """Inline citation marker in document.

    Represents a @[key] citation in the document that references
    a BibliographyEntry.

    Attributes:
        key: Reference to BibliographyEntry key.
        number: Assigned citation number (1, 2, 3...).
    """

    node_type: NodeType = NodeType.CITATION
    key: str = ""
    number: int = 0


class BibliographySection(BaseNode):
    """Bibliography section in DOCX.

    Represents the "Список литературы" section containing all
    cited references in order.

    Attributes:
        heading: Section heading (default: "Список литературы").
        entries: All cited entries in order of first citation.
        style: Citation style (numeric or author-year).
    """

    node_type: NodeType = NodeType.BIBLIOGRAPHY_SECTION
    heading: str = "Список литературы"
    entries: list[BibliographyEntry] = Field(default_factory=list)
    style: CitationStyle = CitationStyle.NUMERIC


class ChapterContext(BaseModel):
    """Context for chapter-aware numbering.

    Used during document traversal to track current chapter state
    for proper section numbering and reference formatting.

    Attributes:
        chapter_number: Current chapter number (1-based).
        chapter_title: Title of the current chapter.
        section_counter: Counter for sections within the current chapter.
    """

    chapter_number: int = 1
    chapter_title: str = ""
    section_counter: int = 0
    figure_counter: int = 0
    table_counter: int = 0
    equation_counter: int = 0


# Type alias for inline nodes (used in Paragraph.runs)
InlineNode = (
    TextRun
    | InlineRunNode
    | InlineCodeNode
    | InlineMathNode
    | Bookmark
    | CrossRefNode
    | CrossReference
    | CitationNode
)


# Type alias for all IR nodes
IRNode = (
    Document
    | Section
    | Paragraph
    | ListBlock
    | ListItem
    | TableNode
    | Figure
    | Equation
    | MathNode
    | TextRun
    | InlineRunNode
    | InlineCodeNode
    | InlineMathNode
    | Bookmark
    | CrossReference
    | CrossRefNode
    | Caption
    | TOCNode
    | CitationNode
    | BibliographySection
)


class CrossRefMap(BaseModel):
    """Map for cross-reference resolution."""

    labels: dict[str, BaseNode] = Field(default_factory=dict)

    def register(self, label: str, node: BaseNode) -> None:
        """Register a label with its node."""
        self.labels[label] = node

    def resolve(self, label: str) -> Optional[BaseNode]:
        """Resolve a label to its node."""
        return self.labels.get(label)


class ValidationResult(BaseModel):
    """Результат валидации ссылок и меток.

    Содержит информацию о неопределённых ссылках и неиспользуемых метках.

    Attributes:
        undefined_refs: Ссылки (@label), которые не имеют определения.
        unreferenced_labels: Метки (<label>), на которые нет ссылок.
        file_path: Путь к файлу для отчёта (опционально).
        line_number: Номер строки для отчёта (опционально).
    """

    undefined_refs: set[str] = Field(default_factory=set)
    unreferenced_labels: set[str] = Field(default_factory=set)
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    @property
    def has_errors(self) -> bool:
        """Проверяет наличие ошибок (неопределённых ссылок)."""
        return bool(self.undefined_refs)

    @property
    def has_warnings(self) -> bool:
        """Проверяет наличие предупреждений (неиспользуемых меток)."""
        return bool(self.unreferenced_labels)

    def format_report(self) -> str:
        """Форматирует отчёт о валидации в читаемый текст.

        Returns:
            Строка с форматированным отчётом о проблемах.
        """
        lines: list[str] = []

        # Добавляем информацию о файле, если доступна
        if self.file_path:
            location = f"{self.file_path}"
            if self.line_number is not None:
                location += f":{self.line_number}"
            lines.append(f"Validation report for {location}")
            lines.append("")

        # Выводим неопределённые ссылки (ошибки)
        if self.undefined_refs:
            lines.append("Undefined references (errors):")
            for ref in sorted(self.undefined_refs):
                lines.append(f"  WARNING: @{ref}")
            lines.append("")

        # Выводим неиспользуемые метки (предупреждения)
        if self.unreferenced_labels:
            lines.append("Unreferenced labels (info):")
            for label in sorted(self.unreferenced_labels):
                lines.append(f"  INFO: <{label}>")
            lines.append("")

        # Если нет проблем
        if not self.undefined_refs and not self.unreferenced_labels:
            lines.append("No validation issues found.")

        return "\n".join(lines)
