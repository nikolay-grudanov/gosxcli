# Data Model: Bibliography Support

**Feature**: Bibliography Support
**Date**: 2026-04-19
**Spec**: specs/003-bibliography-support/spec.md

## Entity Overview

This feature introduces the following new entities:

1. **BibliographyFile** - Container for loaded .bib file
2. **BibliographyEntry** - Single bibliographic record
3. **Citation** - Inline reference to BibliographyEntry
4. **BibliographySection** - DOCX output section

---

## Entity Definitions

### BibliographyFile

**Purpose**: Represents a loaded BibTeX file with all entries

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| path | str | Yes | Path to .bib file |
| entries | Dict[str, BibliographyEntry] | Yes | Map of key → entry |
| parse_errors | List[str] | No | Warnings for malformed entries |

**Validation Rules**:
- Duplicate keys: warn and use first occurrence
- Missing required fields: warn and mark entry as incomplete

---

### BibliographyEntry

**Purpose**: Single bibliographic entry from BibTeX

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| key | str | Yes | Citation key (e.g., "smith2020") |
| entry_type | BibliographyType | Yes | article, book, inproceedings, etc. |
| author | str | Yes | Author name(s) |
| title | str | Yes | Title of work |
| year | str | No | Publication year |
| journal | str | No | Journal name (for articles) |
| booktitle | str | No | Book title (for inproceedings) |
| publisher | str | No | Publisher name |
| address | str | No | City/location |
| pages | str | No | Page range (e.g., "12-25") |
| volume | str | No | Volume number |
| number | str | No | Issue number |
| doi | str | No | Digital Object Identifier |
| url | str | No | Web URL |

**Validation Rules**:
- key: non-empty string
- entry_type: must be valid BibliographyType enum
- author, title: non-empty if entry is used
- Optional fields: empty string if not present

---

### BibliographyType (Enum)

**Values**:
- `ARTICLE` - Journal article
- `BOOK` - Book
- `INPROCEEDINGS` - Conference proceeding
- `TECHREPORT` - Technical report
- `MISC` - Miscellaneous/unknown
- `PHDTHESIS` - PhD thesis
- `MASTERSTHESIS` - Master's thesis

---

### Citation

**Purpose**: Inline citation marker in document

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| key | str | Yes | Reference to BibliographyEntry key |
| number | int | Yes | Assigned citation number (1, 2, 3...) |
| position | SourceLocation | Yes | Position in source document |

**Validation Rules**:
- key: must exist in loaded bibliography or warning issued
- number: positive integer, assigned sequentially

---

### BibliographySection (IR Node)

**Purpose**: Section in DOCX containing formatted bibliography

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| heading | str | Yes | Section heading (default: "Список литературы") |
| entries | List[BibliographyEntry] | Yes | All cited entries in order |
| style | CitationStyle | Yes | Citation style (numeric or author-year) |
| position | SourceLocation | Yes | Position in document |

**Validation Rules**:
- entries: ordered by first citation appearance
- style: must be valid CitationStyle enum

---

### CitationStyle (Enum)

**Values**:
- `NUMERIC` - [1], [2], [3] format (default)
- `AUTHOR_YEAR` - (Smith, 2020) format

---

## State Transitions

### Citation Numbering

```
Document with @[key] citations
         ↓
Parser extracts all @[key] in order
         ↓
Assign sequential numbers (1, 2, 3...)
         ↓
Create Citation nodes with numbers
         ↓
Create BibliographySection with entries
         ↓
Writer renders [1] and bibliography
```

---

## Relationship Diagram

```
BibliographyFile
    │
    ├── entries: Dict[key → BibliographyEntry]
    │
    └── Citation instances reference entries by key
              │
              ↓
         CitationNode (in IR)
              │
              ↓
    BibliographySectionNode (in IR)
              │
              ↓
         DOCX Writer
              │
              ↓
    [1] inline markers + Bibliography section
```

---

## Edge Cases

1. **Missing key**: Citation references non-existent entry → warning + placeholder "[unknown]"
2. **Duplicate entry type**: Multiple entries with same key → warn, use first
3. **Incomplete entry**: Missing author/title → warn, include with available data
4. **LaTeX commands in fields**: `\textit{}`, `\textbf{}` → strip commands, keep text
5. **Long titles**: No truncation, wrap in DOCX

---

## Integration with Existing IR

New nodes added to `ir/model.py`:
- `BibliographyEntry` - Pydantic BaseModel (embedded in BibliographySection)
- `CitationNode` - Pydantic BaseModel (like CrossReferenceNode)
- `BibliographySection` - Pydantic BaseModel (like TOCNode)

No breaking changes to existing nodes. Minor version bump: IR_1_1