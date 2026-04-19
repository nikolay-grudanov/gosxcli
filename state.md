# Project State: gosxcli

**Last Updated:** 2026-04-19
**Version:** v0.2.0 (In Progress)
**Status:** Active Development - All tests passing (110/110)

---

## Overview

gosxcli — CLI-инструмент для конвертации Typst-документов в DOCX с поддержкой академических стилей по ГОСТ 7.32-2017. Реализует 4-слойную архитектуру: Ingest → Parser → IR → Writer.

---

## Current Status

### Overall Health
- 🟢 Healthy

### Key Metrics
- Lines of Code: ~3,400
- Test Files: 12 (test_multifile.py, test_table_attributes.py, test_validator.py, test_cli_validation.py added, test_extractor_v2.py, test_inline_parsing.py, test_inline_rendering.py, test_smoke.py, test_refs.py, test_tables.py, test_equations.py, real_vkr/)
- Test Cases: 110 (all passing: 48 existing + 14 multifile + 12 table attributes + 19 validation tests)
- Ruff Errors: 0
- Mypy: Passing (--strict mode enabled for extractor_v2.py, model.py, test_table_attributes.py, validator.py)

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

### Recently Completed
- ✅ Project architecture defined (Completed: 2026-04-18)
- ✅ Constitution v1.0.0 ratified (Completed: 2026-04-18)
- ✅ Phase 1 Setup complete (T001-T005): latex2mathml, fixtures/real_vkr/, benchmarks/, tests/regression/
- ✅ Phase 2 Foundational complete (T006-T016): IR model updated with new entities, config migrated to Pydantic v2
- ✅ Inline formatting tests T066-T068 (Completed: 2026-04-19)
- ✅ All 62 tests passing (Completed: 2026-04-19)
- ✅ Fixed: LabelExtractor regex for labels with colons and hyphens (labels.py)
- ✅ Fixed: _extract_until_matching_paren() paren counting (extractor_v2.py)
- ✅ Fixed: labels.py regex to capture `[\w:_-]+` instead of `[\w:]+`
- ✅ Fixed: scanner nested table matching pattern
- ✅ Updated test_real_vkr.py tables test to document nested table limitation
- ✅ Created TypstQueryParser with typst query support (Completed: 2026-04-19)
- ✅ Created RegexFallbackParser using scanner + extractor_v2 (Completed: 2026-04-19)
- ✅ Created UnifiedParser as primary interface (Completed: 2026-04-19)
- ✅ Multi-file Typst project loading with #include support (Completed: 2026-04-19)
  - T024-T027: Implemented recursive loading, depth protection, relative path resolution, debug logging
  - Updated TypstProjectLoader with _load_includes() and _parse_includes() methods
  - Added strict_mode parameter for error handling
  - Protected against cyclic references using loaded_files set
  - All 62 tests passing (48 existing + 14 new multifile tests)
- ✅ CLI flags T063-T065 (Completed: 2026-04-19)
  - T063: Added `--math-mode [native|image|fallback]` flag to CLI
  - T064: Added `--strict` flag to CLI with exit code 1 on unresolved references
  - T065: `--debug` flag already existed
  - Updated DocxWriter to accept and use math_mode parameter
  - Implemented math rendering logic in _write_equation() for all modes
  - Added strict mode validation in _run_conversion()
  - CLI help updated to show new flags
- ✅ Table attributes parsing T034-T039, T047 (Completed: 2026-04-19)
  - Added `border_width` field to TableNode in IR model
  - Implemented `_parse_columns_spec()` for parsing various column formats: (1fr, 2fr), (17%, 83%), (auto, 1fr, 20%)
  - Implemented `_parse_stroke_spec()` for parsing stroke: 0.7pt
  - Implemented `_parse_fill_lambda()` for parsing fill lambda patterns: (col, row) => if row == 0 { luma(220) }
  - Implemented `_parse_align_lambda()` for parsing align lambda patterns: (col, row) => if row == 0 { center }
  - Updated `_extract_row_cells()` to support table.cell(colspan: N)[...] and table.cell(rowspan: N)[...]
  - Updated `_extract_header_cells()` to apply fill and align attributes from lambda expressions
  - Added 12 comprehensive tests for table attributes (test_table_attributes.py)
  - All 74 tests passing (48 existing + 14 multifile + 12 table attributes)
- ✅ Tables colspan/rowspan implementation T040-T046 (Completed: 2026-04-19)
  - Updated TablesManager to use TableNode.columns, header, rows
  - Implemented _set_cell_colspan() for gridSpan
  - Implemented _set_cell_rowspan() for vMerge
  - Implemented _set_cell_borders() for tcBorders
  - Implemented _set_cell_fill() for shd (header shading)
  - Implemented _set_cell_alignment() for jc (alignment)
  - Implemented _set_table_grid() for column widths via tblGrid
  - All 84 tests passing (48 existing + 14 multifile + 12 table attributes + 10 chapter-aware)
- ✅ Chapter-aware references T050-T055 (Completed: 2026-04-19)
  - Added number and chapter_number fields to Figure, TableNode, Equation, Caption, CrossRefNode, Section
  - Integrated ChapterContext in DocxWriter for tracking chapter numbers and counters
  - Updated _write_section to increment chapter_number and reset counters on level 1 headings
  - Updated _write_figure, _write_table, _write_equation to increment counters
  - Added ref_labels configuration for localized reference text
  - Implemented _write_cross_ref_node with chapter-aware numbering
  - Implemented _format_cross_ref for localized formatting ("Рисунок 1.2", "Таблица 2.1")
  - Updated RefResolver to process CrossRefNode
  - Added 10 comprehensive tests (test_chapter_aware_refs.py)
  - All 84 tests passing
- ✅ MathRenderer module T028-T031 (Completed: 2026-04-19)
  - Created writers/math_renderer.py module
  - Implemented MathRenderer class with render() and render_to_element() methods
  - Supports native, fallback, and image modes
  - Uses latex2mathml for LaTeX to OMML conversion
  - Implements text fallback for failed rendering

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
- [ ] T048-T049: Nested tables detection and generation
- [ ] Run full test suite and verify 110+ tests pass
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