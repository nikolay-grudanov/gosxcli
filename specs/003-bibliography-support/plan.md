# Implementation Plan: Bibliography Support

**Branch**: `002-bugfix-v0.1-labels-refs-math` | **Date**: 2026-04-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-bibliography-support/spec.md`

## Summary

Add Bibliography support for BibTeX-style citations. Users can:
- Load `.bib` files via `#bibliography("file.bib")`
- Insert inline citations with `@[key]`
- Generate "Список литературы" section in DOCX
- Format entries according to ГОСТ 7.32-2017

**Technical Approach**: Custom BibTeX parser (no external deps), new IR nodes, integrated into existing 4-layer pipeline.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: None (custom BibTeX parser), existing: typer, pydantic v2, python-docx
**Storage**: N/A (file-based input)
**Testing**: pytest (existing framework)
**Target Platform**: Linux/macOS/Windows CLI
**Project Type**: CLI tool for document conversion
**Performance Goals**: < 5s for 50 citations (SC-006)
**Constraints**: Must follow 4-layer architecture, Pydantic v2 for models
**Scale/Scope**: ~100-500 entries per bibliography, single .bib file per document

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| 4-layer architecture | ✅ PASS | New module in parser layer, new IR nodes |
| Pydantic v2 for models | ✅ PASS | BibliographyEntry, CitationNode use BaseModel |
| IR Contract preserved | ✅ PASS | New node types, no breaking changes |
| GOST compliance | ✅ PASS | ГОСТ 7.32-2017 formatting for bibliography |
| Testing Mandate | ✅ PASS | Fixtures will be created in tests/fixtures/ |
| Strict/Soft modes | ✅ PASS | Warnings for missing keys (soft), can add strict |

**Violations**: None

## Project Structure

### Documentation (this feature)

```text
specs/003-bibliography-support/
├── plan.md              # This file
├── research.md          # Phase 0: Technical decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Integration scenarios
├── contracts/           # Phase 1: Interface contracts
│   └── parser-ir-contract.md
└── tasks.md             # Phase 2 (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/typst_gost_docx/
├── cli.py                  # Add --bibliography-style flag
├── config.py               # Add bibliography_style to Config
├── ir/
│   └── model.py            # Add: BibliographyEntry, CitationNode, BibliographySection
├── parser/
│   ├── bibliography.py     # NEW: BibTeX parser
│   ├── extractor.py       # Parse #bibliography() and @[key]
│   └── ...
└── writers/
    └── docx_writer.py     # Generate bibliography section
```

**Structure Decision**: 
- `parser/bibliography.py` - BibTeX parsing module
- New IR nodes in `ir/model.py`
- Writer modified to handle `BibliographySection`

## Complexity Tracking

> N/A - No constitution violations to justify

---

## Phase 0: Research ✅

Completed in `research.md`:
- BibTeX parsing: Custom regex parser
- Architecture: New module + IR nodes
- Style: CLI flag with numeric default
- Error handling: Warnings + placeholders

## Phase 1: Design & Contracts ✅

Completed:
- `data-model.md` - Entity definitions
- `contracts/parser-ir-contract.md` - Interface contracts  
- `quickstart.md` - Integration scenarios

### Files to Create

| File | Purpose |
|------|---------|
| `src/typst_gost_docx/parser/bibliography.py` | BibTeX parser |
| `tests/fixtures/typ/bibliography/basic.typ` | Test fixture |
| `tests/fixtures/docx/bibliography/basic.docx` | Expected output |
| `tests/unit/test_bibliography.py` | Unit tests |

### Files to Modify

| File | Changes |
|------|---------|
| `src/typst_gost_docx/ir/model.py` | Add BibliographyEntry, CitationNode, BibliographySection |
| `src/typst_gost_docx/parser/extractor.py` | Parse #bibliography(), @[key] |
| `src/typst_gost_docx/writers/docx_writer.py` | Write bibliography section |
| `src/typst_gost_docx/cli.py` | Add --bibliography-style |
| `src/typst_gost_docx/config.py` | Add bibliography_style |

---

## Next Step

Run `/speckit.tasks` to generate task list from this plan.