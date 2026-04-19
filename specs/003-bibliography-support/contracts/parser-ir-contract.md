# Contracts: Bibliography Support

**Feature**: Bibliography Support
**Date**: 2026-04-19

This directory contains interface contracts for the Bibliography feature.

---

## Contract 1: Parser → IR Contract

### Bibliography Parsing Contract

**Input**: 
- Typst document with `#bibliography("file.bib")` command
- `.bib` file content

**Output**:
- IRDocument with `BibliographyNode` and `CitationNode` elements

### Parser Behavior

1. **When `#bibliography("file.bib")` found**:
   - Load and parse `file.bib`
   - Store parsed entries in `BibliographyFile` object
   - Add `BibliographyNode` to IR at document end

2. **When `@[key]` found in text**:
   - Create `CitationNode` with key reference
   - Track citation order for numbering
   - Emit warning if key not in bibliography

3. **Citation Numbering**:
   - First unique citation → 1
   - Second unique citation → 2
   - Repeat of existing citation → same number

### Error Handling

| Condition | Behavior |
|-----------|----------|
| .bib file not found | Warning + continue without bibliography |
| Key not in bibliography | Warning + placeholder "[unknown]" |
| Malformed BibTeX entry | Warning + skip entry |
| Duplicate key | Warning + use first occurrence |

---

## Contract 2: IR → Writer Contract

### Bibliography Node Contract

**Node Type**: `BibliographyNode`

**Fields**:
```python
heading: str = "Список литературы"
entries: List[BibliographyEntry]  # Ordered by first citation
style: CitationStyle = CitationStyle.NUMERIC
```

**Entry Format (ГОСТ 7.32-2017)**:

Numeric style:
```
1. Автор А.А. Название статьи // Журнал. — Год. — Т. X. — С. XX-XX.
2. Автор Б.Б. Название книги. — Город: Издательство, Год. — 256 с.
```

Author-year style:
```
Автор, А.А. (Год). Название статьи // Журнал. Т. X. С. XX-XX.
Автор, Б.Б. (Год). Название книги. — Город: Издательство.
```

---

## Contract 3: CLI Configuration Contract

### Bibliography Style Flag

**Flag**: `--bibliography-style`

**Values**:
- `numeric` (default) - [1], [2], [3] inline
- `author-year` - (Author, Year) inline

**Config Integration**:
- Adds `bibliography_style` field to `Config` model
- Default: `CitationStyle.NUMERIC`

---

## Contract 4: Typst Syntax Contract

### Supported Typst Commands

| Command | Description | Example |
|---------|-------------|---------|
| `#bibliography("file.bib")` | Load bibliography file | `#bibliography("refs.bib")` |
| `@[key]` | Inline citation | `@[smith2020]` |
| `@[key, p. 42]` | Citation with page | `@[smith2020, p. 42]` (future) |

### Unsupported

- `#set bibliography(style: ...)` - Not implemented in MVP
- Multiple bibliography files - Not supported in MVP

---

## Contract 5: Integration Test Contract

### Test Scenario: Basic Bibliography

**Input**:
- `basic.typ` with `#bibliography("refs.bib")` and `@[a]` `@[b]` `@[a]`
- `refs.bib` with entries for `a` and `b`

**Expected Output**:
- DOCX with inline [1], [2], [1] markers
- Bibliography section with 2 entries (a=1, b=2)
- Entry format follows ГОСТ 7.32-2017

---

## Verification

All contracts verified by:
1. Unit tests in `tests/unit/test_bibliography.py`
2. Integration tests in `tests/integration/test_bibliography.py`
3. E2E test fixtures in `tests/fixtures/typ/bibliography/`