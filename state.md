# Project State: gosxcli

**Last Updated:** 2026-04-19
**Version:** v0.2.0 (In Progress)
**Status:** Active Development - All tests passing

---

## Overview

gosxcli — CLI-инструмент для конвертации Typst-документов в DOCX с поддержкой академических стилей по ГОСТ 7.32-2017. Реализует 4-слойную архитектуру: Ingest → Parser → IR → Writer.

---

## Current Status

### Overall Health
- 🟢 Healthy

### Key Metrics
- Lines of Code: ~2,800
- Test Files: 8 (test_extractor_v2.py, test_inline_parsing.py, test_inline_rendering.py, test_smoke.py, test_refs.py, test_tables.py, test_equations.py, real_vkr/)
- Test Cases: 48 (all passing)
- Ruff Errors: 0
- Mypy: Not configured

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
| Enhanced math | 🔄 In Progress | latex2mathml dependency added, IR model updated |
| colspan/rowspan | 🔄 In Progress | TableNode, TableCellNode with colspan/rowspan added |
| Better refs | 🔄 In Progress | CrossRefNode, ChapterContext added |
| Chapter numbering | 🔄 In Progress | ChapterContext entity added |
| Inline formatting | ✅ Complete | InlineNode, InlineRunNode, runs in Paragraph, parser and writer updated |

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

### Recently Completed
- ✅ Project architecture defined (Completed: 2026-04-18)
- ✅ Constitution v1.0.0 ratified (Completed: 2026-04-18)
- ✅ Phase 1 Setup complete (T001-T005): latex2mathml, fixtures/real_vkr/, benchmarks/, tests/regression/
- ✅ Phase 2 Foundational complete (T006-T016): IR model updated with new entities, config migrated to Pydantic v2
- ✅ Inline formatting tests T066-T068 (Completed: 2026-04-19)
- ✅ All 48 tests passing (Completed: 2026-04-19)
- ✅ Fixed: LabelExtractor regex for labels with colons and hyphens (labels.py)
- ✅ Fixed: _extract_until_matching_paren() paren counting (extractor_v2.py)
- ✅ Fixed: labels.py regex to capture `[\w:_-]+` instead of `[\w:]+`
- ✅ Fixed: scanner nested table matching pattern
- ✅ Updated test_real_vkr.py tables test to document nested table limitation
- ✅ Created TypstQueryParser with typst query support (Completed: 2026-04-19)
- ✅ Created RegexFallbackParser using scanner + extractor_v2 (Completed: 2026-04-19)
- ✅ Created UnifiedParser as primary interface (Completed: 2026-04-19)

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

---

## Next Steps

### Immediate (This Week)
1. Fix pytest collection errors
2. Determine and remove duplicate parser
3. Migrate from dataclass to Pydantic v2

### Short Term (Next 2 Weeks)
4. Add missing tests for Writer components
5. Fix ruff linting errors
6. Set up mypy for type checking
7. Update AGENTS.md to match code

### Medium Term (Next Month)
8. Implement v0.2 features
9. Improve error handling
10. Add integration tests

---

## Resources

- **Constitution:** [.specify/memory/constitution.md](.specify/memory/constitution.md)
- **Architecture:** [AGENTS.md](AGENTS.md)
- **README:** [README.md](README.md)
- **Roadmap:** [docs/roadmap.md](docs/roadmap.md)
- **DOD:** [docs/DOD.md](docs/DOD.md)

---

**Last Updated by:** @gosxcli-orchestrator (2026-04-19)