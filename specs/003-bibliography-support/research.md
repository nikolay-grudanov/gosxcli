# Research: Bibliography Support

**Feature**: Bibliography Support (bibtex-style)
**Date**: 2026-04-19
**Spec**: specs/003-bibliography-support/spec.md

## Research Summary

Based on analysis of the feature specification and project architecture, the following technical decisions were made:

---

## Decision 1: BibTeX Parsing Approach

**Choice**: Custom parser with regex-based extraction

**Rationale**: 
- No reliable pure-Python BibTeX parsing libraries with proper Cyrillic support
- Custom implementation gives full control over field extraction and error handling
- BibTeX format is relatively simple (entry type, key, fields)
-符合项目架构（4-layer中的Parser层）

**Alternatives Considered**:
- `bibtexparser` library - adds dependency, may have Cyrillic issues
- `python-bibtex` - unmaintained, no Python 3.12+ support
- External tool call - violates CLI simplicity principle

---

## Decision 2: Bibliography Architecture Integration

**Choice**: New module in `parser/` layer + new IR node type

**Rationale**:
- Bibliography loading happens in Parser layer (after Ingest)
- New `BibliographyNode` added to IR to represent bibliography section
- Citation markers `@[key]` parsed as `CitationNode` in IR
- Writer generates DOCX bibliography section from `BibliographyNode`

**Architecture**:
```
Ingest: Load .bib file as raw string
Parser: 
  - Parse .bib file → BibliographyFile object
  - Parse @[key] citations → CitationNode in IR
  - Collect all citations for bibliography section
IR: BibliographyNode, CitationNode
Writer: Generate bibliography section and inline citation markers
```

---

## Decision 3: Citation Rendering

**Choice**: Inline numbered citations [1], [2] with numeric style default

**Rationale**:
- Numeric style is most common for Russian academic ГОСТ documents
- Author-year style available as configuration option
- DOCX hyperlinks not used (citations are static numbers, not clickable)
- All citations collected before rendering (need global numbering)

---

## Decision 4: Bibliography Entry Storage

**Choice**: Pydantic model for BibliographyEntry in `ir/model.py`

**Rationale**:
- Constitution requires Pydantic v2 for all data models
- Entry fields: key, entry_type, author, title, year, journal, booktitle, publisher, pages, url, doi
- Validation: required fields (key, entry_type), optional fields with defaults
- Error handling: warn on missing required fields, use placeholder

---

## Decision 5: CLI Configuration

**Choice**: Add `--bibliography-style` flag (numeric | author-year)

**Rationale**:
- SC-013 requires style selection via CLI or config
- Consistent with existing `--math-mode` and `--strict` flags
- Default: numeric (most common for ГОСТ)

---

## Key Technical Details

### BibTeX Entry Types to Support

| Type | Format | Example |
|------|--------|---------|
| article | author. Title. // Journal, Year. — P. pages | Journal article |
| book | author. Title. — City: Publisher, Year | Book |
| inproceedings | author. Title // Proceedings... — Year. — P. pages | Conference |
| techreport | author. Title. — City, Year. — N. number | Technical report |
| misc | author. Title. — Year. — URL | Web resource |

### ГОСТ 7.32-2017 Bibliography Format

Entry format: `[number]. Author. Title. — City: Publisher, Year. — Pages`

Example:
```
1. Петров И.И. Заголовок статьи // Журнал. — 2023. — Т. 1. — С. 12-25.
2. Сидоров А.А. Название книги. — Москва: Издательство, 2023. — 256 с.
```

---

## Unknowns Resolved

1. **BibTeX library**: Custom regex parser (no external dependency)
2. **Cyrillic support**: UTF-8 encoding assumed in .bib files, custom parser handles correctly
3. **Integration**: BibliographyNode added to IR, parsed in Parser, written in Writer
4. **Style selection**: CLI flag `--bibliography-style` with numeric default
5. **Error handling**: Warnings on missing keys/fields, placeholder for missing entries

---

## Testing Approach

Per Constitution Testing Mandate:
- Fixture: `tests/fixtures/typ/bibliography/basic.typ` with @[key] citations
- Fixture: `tests/fixtures/docx/bibliography/basic.docx` with expected output
- Integration test: Convert .typ with bibliography to DOCX, verify structure

---

## Files to Create/Modify

### New Files
- `src/typst_gost_docx/parser/bibliography.py` - BibTeX parser
- `tests/fixtures/typ/bibliography/` - Typst test fixtures
- `tests/fixtures/docx/bibliography/` - Expected DOCX output

### Modify
- `src/typst_gost_docx/ir/model.py` - Add BibliographyNode, CitationNode, BibliographyEntry
- `src/typst_gost_docx/parser/extractor.py` - Parse #bibliography() and @[key]
- `src/typst_gost_docx/writers/docx_writer.py` - Generate bibliography section
- `src/typst_gost_docx/cli.py` - Add --bibliography-style flag
- `src/typst_gost_docx/config.py` - Add bibliography_style to Config