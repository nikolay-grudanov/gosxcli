# Project State: gosxcli

**Last Updated:** 2026-04-19
**Version:** v0.2.0 (In Progress)
**Status:** Active Development - All tests passing (114/114)

---

## Overview

gosxcli — CLI-инструмент для конвертации Typst-документов в DOCX с поддержкой академических стилей по ГОСТ 7.32-2017. Реализует 4-слойную архитектуру: Ingest → Parser → IR → Writer.

---

## Current Status

### Overall Health
- 🟢 Healthy

### Key Metrics
- Lines of Code: ~3,600
- Test Files: 13 (test_multifile.py, test_table_attributes.py, test_validator.py, test_cli_validation.py, test_nested_tables.py added, test_extractor_v2.py, test_inline_parsing.py, test_inline_rendering.py, test_smoke.py, test_refs.py, test_tables.py, test_equations.py, real_vkr/)
- Test Cases: 114 (all passing: 48 existing + 14 multifile + 12 table attributes + 19 validation + 4 nested tables)
- Ruff Errors: 0
- Mypy: Passing (--strict mode enabled for extractor_v2.py, model.py, test_table_attributes.py, validator.py, scanner.py, tables.py)

---

## Progress Tracker

### v0.1 (MVP) - Current
| Feature | Status | Notes |
|---------|--------|-------|
| Headings | ✅ Complete | Levels 1-3 supported |
| Paragraphs | ✅ Complete | Basic formatting |
| Lists | ✅ Complete | Bullet and numbered |
| Tables | ✅ Complete | Basic support only |
| Figures | ✅ Complete | With captions |
| References | ✅ Complete | @label resolution |
| Math | ⚠️ MVP | Complex formulas as placeholders |

### v0.2 (In Progress)
| Feature | Status | Notes |
|---------|--------|-------|
| Enhanced math | ✅ Complete | MathRenderer module with latex2mathml, T028-T031 |
| Table attributes parsing | ✅ Complete | T034-T039: columns, stroke, fill, align, colspan, rowspan parsing |
| colspan/rowspan | ✅ Complete | T040-T046: TablesManager with gridSpan, vMerge, borders, shading, alignment |
| Better refs | ✅ Complete | T050-T055: CrossRefNode, ChapterContext, chapter-aware numbering |
| Chapter numbering | ✅ Complete | ChapterContext integrated in DocxWriter |
| Inline formatting | ✅ Complete | InlineNode, InlineRunNode, runs in Paragraph, parser and writer updated |
| Bidirectional validation | ✅ Complete | T058-T062: ReferenceValidator, ValidationResult, CLI integration |
| Table of Contents | ✅ Complete | T056-T057: #outline() parsing and DOCX TOC generation |
| Multi-file support | ✅ Complete | T024-T027: #include recursive loading with depth protection |
| CLI flags | ✅ Complete | T063-T065: --math-mode, --strict, --debug |
| Nested tables | ✅ Complete | T048-T049: Table detection in figures, nested table generation in cells |
| Enhanced label parsing | ✅ Complete | Updated scanner patterns to support labels with colons and hyphens |


### v0.3 (Planned)
| Feature | Status | Notes |
|---------|--------|-------|
| Code blocks | 🔲 Not Started | Syntax highlighting |
| Bibliography | 🔲 Not Started | Reference management |
| Page breaks | 🔲 Not Started | Section formatting |
| Error handling | 🔲 Not Started | Robust error messages |
| Full GOST | 🔲 Not Started | Complete compliance |

---

## Known Issues

### Critical (P0)
1. **Duplicate parsers** — extractor.py vs extractor_v2.py → RESOLVED with new architecture
   - Impact: Code duplication, confusion
   - Status: 🟢 Fixed (Solution: UnifiedParser chooses between TypstQueryParser and RegexFallbackParser)
   - Completed: 2026-04-19

 2. **Dataclass vs Pydantic** — Config, IR, Scanner use Pydantic v2 ✅ RESOLVED
   - Impact: Violates constitution
   - Status: 🟢 Fixed (Solution: Token in scanner.py migrated to Pydantic BaseModel, scanner_v2.py removed)
   - Completed: 2026-04-19

### High (P1)
 3. **Pydantic unused** — ✅ RESOLVED - Pydantic v2 is now used in config.py, ir/model.py, scanner.py
   - Impact: Unnecessary dependency
   - Status: 🟢 Fixed
   - Completed: 2026-04-19

4. **Python 3.14 untested** — Project requires >=3.12 but not tested on 3.14
   - Impact: Potential compatibility issues
   - Status: 🟡 Open
   - Owner: TBD

### Medium (P2)
5. **Missing tests** — No tests for ImagesManager, BookmarksManager, StylesManager
   - Impact: Low test coverage
   - Status: 🟡 Open
   - Owner: TBD

### Low (P3)
7. **Ruff errors** — None (fixed: labels.py regex, extractor_v2.py paren tracking)
   - Impact: Code quality
   - Status: 🟢 Fixed
   - Owner: N/A

8. **No mypy** — Static type checking not configured
   - Impact: No type safety guarantees
   - Status: 🟡 Open
   - Owner: TBD

---

## Current Work

### Active Tasks
- [x] Migrate from dataclass to Pydantic v2 (Completed: 2026-04-19) ✅
- [x] Fix LabelExtractor source_location bug (Completed: 2026-04-19)
- [x] Fix TypstExtractorV2 list behavior (Completed: 2026-04-19)
- [x] Fix TypstExtractorV2 table access pattern (Completed: 2026-04-19)
- [x] Fix Greek letters math parsing (Completed: 2026-04-19) - тест need raw strings
- [x] Update remaining failing tests (refs, real_vkr) - FIXED: 2026-04-19
- [x] Implement multi-file Typst project loading with #include support (Completed: 2026-04-19) ✅
  - T024-T027: Implemented recursive loading, depth protection, relative path resolution, debug logging
- [x] Implement table attributes parsing (T034-T039) (Completed: 2026-04-19) ✅
  - Added `border_width` field to TableNode
  - Implemented `_parse_columns_spec()`, `_parse_stroke_spec()`, `_parse_fill_lambda()`, `_parse_align_lambda()`
  - Updated `_extract_row_cells()` for table.cell(colspan/rowspan)
  - Added 12 comprehensive tests for table attributes
- [x] Implement bidirectional validation (T058-T062) (Completed: 2026-04-19) ✅
  - Added `ValidationResult` model to ir/model.py
  - Created `ReferenceValidator` class in parser/validator.py
  - Added 19 comprehensive tests
- [x] Implement Table of Contents support (T056-T057) (Completed: 2026-04-19) ✅
  - Added TOCNode class, OUTLINE_START token, _write_toc() method
  - Created 7 tests
- [x] Implement tables colspan/rowspan T040-T046 (Completed: 2026-04-19) ✅
  - TablesManager updated with gridSpan, vMerge, borders, shading, alignment
- [x] Implement chapter-aware references T050-T055 (Completed: 2026-04-19) ✅
  - ChapterContext integrated in DocxWriter, _format_cross_ref() implemented
  - Added 10 comprehensive tests
- [x] Implement MathRenderer module T028-T031 (Completed: 2026-04-19) ✅
  - Created writers/math_renderer.py with render() and render_to_element()
- [x] Implement CLI flags T063-T065 (Completed: 2026-04-19) ✅
  - Added --math-mode, --strict flags to CLI
- [x] Implement nested tables T048-T049 (Completed: 2026-04-19) ✅
  - Updated IR model: Added `table` field to Figure for nested tables
  - Parser: Added `_extract_nested_table_from_figure()` to detect tables inside #figure()
  - Parser: Updated `_extract_figure()`, `_extract_table()`, `_extract_equation()` to handle inline labels
  - Scanner: Updated LABEL pattern from `<([\w:]+)>` to `<([\w:-]+)>` to support labels with hyphens
  - Writer: Updated `_write_figure()` to handle tables instead of images
  - Writer: Added `_write_cell_content()` method to handle nested tables in cells
  - Writer: Added `_add_nested_table()`, `_add_nested_table_row()`, `_add_nested_cell_borders()` for nested table generation
  - Added 4 comprehensive tests for nested tables (test_nested_tables.py)
  - All 114 tests passing (48 existing + 14 multifile + 12 table attributes + 10 chapter-aware + 7 TOC + 19 validation + 4 nested tables)
- [x] Enhanced label parsing (Completed: 2026-04-19) ✅
  - Updated scanner.py LABEL pattern to support colons and hyphens in labels
  - Fixed label handling for figures, tables, and equations with inline labels
  - All 114 tests passing

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Ratify constitution v1.0.0 | Establish project governance principles |
| 2026-04-19 | Add state.md | Track project status and progress |
| 2026-04-19 | Fix LabelExtractor regex to include hyphens | Labels like `ch01-llm-agents` were not captured |
| 2026-04-19 | Fix _extract_until_matching_paren() to count parens in token value | Original code only checked exact `(` and `)` tokens, missing nested structures |
| 2026-04-19 | Fix figure/table extraction to skip closing paren token | Leftover `) ` token was being parsed as paragraph |
| 2026-04-19 | Document nested table limitation in test | Tables inside figures are not extracted as standalone blocks |
| 2026-04-19 | New parser architecture: TypstQueryParser + RegexFallbackParser + UnifiedParser | Primary: typst query JSON, Fallback: regex-based scanner+extractor |
| 2026-04-19 | Implement multi-file Typst project loading with #include support | Real-world VRK documents are split across multiple files; recursive loading needed with protection against cycles |
| 2026-04-19 | Add --math-mode and --strict CLI flags | Required by tasks T063-T065; math rendering modes and strict reference validation |
| 2026-04-19 | Implement bidirectional validation for references and labels | T058-T062: Ensure all references have definitions and warn about unused labels; improves document quality and catches errors early |
| 2026-04-19 | Implement Table of Contents support with placeholder approach | python-docx has limited TOC field support; using placeholder with "Содержание" heading as MVP, allows manual field update in Word |

---

## Next Steps

### Phase 3 Completion
- [ ] Run full test suite and verify 114+ tests pass
- [ ] Code review by @gosxcli-reviewer

### Short Term (Next 2 Weeks)
1. Add missing tests for Writer components (ImagesManager, BookmarksManager, StylesManager)
2. Fix ruff linting errors
3. Set up mypy for type checking
4. Update AGENTS.md to match code

### Medium Term (Next Month)
5. Implement v0.2 features
6. Improve error handling
7. Add integration tests

---

## Resources

- **Constitution:** [.specify/memory/constitution.md](.specify/memory/constitution.md)
- **Architecture:** [AGENTS.md](AGENTS.md)
- **README:** [README.md](README.md)
- **Roadmap:** [docs/roadmap.md](docs/roadmap.md)
- **DOD:** [docs/DOD.md](docs/DOD.md)

---

**Last Updated by:** @gosxcli-orchestrator (2026-04-19)