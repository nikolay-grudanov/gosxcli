# Project State: gosxcli

**Last Updated:** 2026-04-19
**Version:** v0.1.0 (MVP)
**Status:** Active Development

---

## Overview

gosxcli — CLI-инструмент для конвертации Typst-документов в DOCX с поддержкой академических стилей по ГОСТ 7.32-2017. Реализует 4-слойную архитектуру: Ingest → Parser → IR → Writer.

---

## Current Status

### Overall Health
- 🟡 Needs Attention

### Key Metrics
- Lines of Code: ~2,666
- Test Files: 5
- Test Cases: 32
- Ruff Errors: 3
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

### v0.2 (Planned)
| Feature | Status | Notes |
|---------|--------|-------|
| Enhanced math | 🔲 Not Started | latex2mathml integration |
| colspan/rowspan | 🔲 Not Started | Table cell merging |
| Better refs | 🔲 Not Started | Improved resolution |
| Chapter numbering | 🔲 Not Started | Section-aware |
| Inline formatting | 🔲 Not Started | *emphasis*, **strong** |

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
1. **Tests failing** — pytest collection shows 6 errors
   - Impact: Cannot verify code quality
   - Status: 🔴 Open
   - Owner: TBD

2. **Duplicate parsers** — extractor.py vs extractor_v2.py
   - Impact: Code duplication, confusion
   - Status: 🔴 Open
   - Owner: TBD

3. **Dataclass vs Pydantic** — Config and IR use dataclass, should use Pydantic v2
   - Impact: Violates constitution
   - Status: 🔴 Open
   - Owner: TBD

### High (P1)
4. **Pydantic unused** — In dependencies but not used
   - Impact: Unnecessary dependency
   - Status: 🟡 Open
   - Owner: TBD

5. **Python 3.14 untested** — Project requires >=3.12 but not tested on 3.14
   - Impact: Potential compatibility issues
   - Status: 🟡 Open
   - Owner: TBD

### Medium (P2)
6. **Missing tests** — No tests for ImagesManager, BookmarksManager, StylesManager
   - Impact: Low test coverage
   - Status: 🟡 Open
   - Owner: TBD

### Low (P3)
7. **Ruff errors** — 3 linting errors (F401, F841)
   - Impact: Code quality
   - Status: 🟢 Trivial
   - Owner: TBD

8. **No mypy** — Static type checking not configured
   - Impact: No type safety guarantees
   - Status: 🟡 Open
   - Owner: TBD

---

## Current Work

### Active Tasks
- [ ] Fix pytest collection errors (Assignee: TBD)
- [ ] Determine and remove duplicate parser (Assignee: TBD)
- [ ] Migrate from dataclass to Pydantic v2 (Assignee: TBD)

### Recently Completed
- ✅ Project architecture defined (Completed: 2026-04-18)
- ✅ Constitution v1.0.0 ratified (Completed: 2026-04-18)

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Ratify constitution v1.0.0 | Establish project governance principles |
| 2026-04-19 | Add state.md | Track project status and progress |

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

**Last Updated by:** @gosxcli-developer