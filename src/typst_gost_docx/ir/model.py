"""Intermediate Representation models for document conversion."""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


class NodeType(str, Enum):
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
    TEXT_RUN = "text_run"
    EMPHASIS = "emphasis"
    STRONG = "strong"
    INLINE_CODE = "inline_code"
    BOOKMARK = "bookmark"
    CROSS_REFERENCE = "cross_reference"


class ListKind(str, Enum):
    BULLET = "bullet"
    NUMBERED = "numbered"


class NumberingKind(str, Enum):
    FIGURE = "figure"
    TABLE = "table"
    EQUATION = "equation"
    SECTION = "section"


@dataclass
class SourceLocation:
    file_path: str
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None


@dataclass
class BaseNode:
    id: str = ""
    node_type: NodeType = NodeType.DOCUMENT
    label: Optional[str] = None
    source_location: Optional[SourceLocation] = None
    style_hints: dict[str, Any] = field(default_factory=dict)


@dataclass
class Document(BaseNode):
    node_type: NodeType = NodeType.DOCUMENT
    metadata: dict[str, Any] = field(default_factory=dict)
    blocks: list[BaseNode] = field(default_factory=list)


@dataclass
class Section(BaseNode):
    node_type: NodeType = NodeType.SECTION
    level: int = 1
    title: list[BaseNode] = field(default_factory=list)
    blocks: list[BaseNode] = field(default_factory=list)
    numbering_kind: Optional[NumberingKind] = NumberingKind.SECTION


@dataclass
class Paragraph(BaseNode):
    node_type: NodeType = NodeType.PARAGRAPH
    content: list[BaseNode] = field(default_factory=list)


@dataclass
class ListBlock(BaseNode):
    node_type: NodeType = NodeType.LIST_BLOCK
    kind: ListKind = ListKind.BULLET
    items: list["ListItem"] = field(default_factory=list)


@dataclass
class ListItem(BaseNode):
    node_type: NodeType = NodeType.LIST_ITEM
    content: list[BaseNode] = field(default_factory=list)


@dataclass
class Table(BaseNode):
    node_type: NodeType = NodeType.TABLE
    rows: list["TableRow"] = field(default_factory=list)
    has_header: bool = False
    caption: Optional["Caption"] = None
    numbering_kind: Optional[NumberingKind] = NumberingKind.TABLE


@dataclass
class TableRow(BaseNode):
    node_type: NodeType = NodeType.TABLE_ROW
    cells: list["TableCell"] = field(default_factory=list)


@dataclass
class TableCell(BaseNode):
    node_type: NodeType = NodeType.TABLE_CELL
    content: list[BaseNode] = field(default_factory=list)
    colspan: int = 1
    rowspan: int = 1


@dataclass
class Figure(BaseNode):
    node_type: NodeType = NodeType.FIGURE
    caption: Optional["Caption"] = None
    image_path: Optional[str] = None
    numbering_kind: Optional[NumberingKind] = NumberingKind.FIGURE


@dataclass
class Caption(BaseNode):
    node_type: NodeType = NodeType.PARAGRAPH
    text: str = ""
    numbering_kind: Optional[NumberingKind] = None


@dataclass
class Equation(BaseNode):
    node_type: NodeType = NodeType.EQUATION
    latex: str = ""
    caption: Optional[Caption] = None
    numbering_kind: Optional[NumberingKind] = NumberingKind.EQUATION


@dataclass
class TextRun(BaseNode):
    node_type: NodeType = NodeType.TEXT_RUN
    text: str = ""


@dataclass
class Emphasis(BaseNode):
    node_type: NodeType = NodeType.EMPHASIS
    content: list[BaseNode] = field(default_factory=list)


@dataclass
class Strong(BaseNode):
    node_type: NodeType = NodeType.STRONG
    content: list[BaseNode] = field(default_factory=list)


@dataclass
class InlineCode(BaseNode):
    node_type: NodeType = NodeType.INLINE_CODE
    code: str = ""


@dataclass
class Bookmark(BaseNode):
    node_type: NodeType = NodeType.BOOKMARK
    name: str = ""


@dataclass
class CrossReference(BaseNode):
    node_type: NodeType = NodeType.CROSS_REFERENCE
    target_label: str = ""
    ref_text: Optional[str] = None


@dataclass
class CrossRefMap:
    labels: dict[str, BaseNode] = field(default_factory=dict)

    def register(self, label: str, node: BaseNode) -> None:
        self.labels[label] = node

    def resolve(self, label: str) -> Optional[BaseNode]:
        return self.labels.get(label)
