---

description: "Task list for Bibliography Support feature implementation"
---

# Tasks: Bibliography Support

**Input**: Design documents from `/specs/003-bibliography-support/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per Constitution Testing Mandate (fixtures required for each supported Typst construct)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project**: `src/typst_gost_docx/`, `tests/` at repository root
- Paths shown below follow the existing project structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [P] Create test fixtures directory `tests/fixtures/typ/bibliography/`
- [ ] T002 [P] Create test fixtures directory `tests/fixtures/docx/bibliography/`
- [ ] T003 Create BibTeX test fixture `tests/fixtures/typ/bibliography/refs.bib` with article, book, inproceedings entries

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

⚠️ **CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Add `BibliographyType` enum to `src/typst_gost_docx/ir/model.py`
- [ ] T005 [P] Add `CitationStyle` enum to `src/typst_gost_docx/ir/model.py`
- [ ] T006 [P] Add `BibliographyEntry` Pydantic model to `src/typst_gost_docx/ir/model.py`
- [ ] T007 Add `CitationNode` Pydantic model to `src/typst_gost_docx/ir/model.py`
- [ ] T008 Add `BibliographySection` Pydantic model to `src/typst_gost_docx/ir/model.py`
- [ ] T009 Add `BibliographyFile` class in `src/typst_gost_docx/parser/bibliography.py`
- [ ] T010 Implement BibTeX parser in `src/typst_gost_docx/parser/bibliography.py`
  - Parse entry types: article, book, inproceedings, techreport, misc
  - Extract fields: author, title, year, journal, booktitle, publisher, pages, url, doi
  - Handle Cyrillic characters
  - Handle LaTeX commands stripping
- [ ] T011 Add `bibliography_style` field to `src/typst_gost_docx/config.py`
- [ ] T012 Add `--bibliography-style` CLI flag in `src/typst_gost_docx/cli.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Inline Citations in Text (Priority: P1) 🎯 MVP

**Goal**: Users can add @[key] citations in text and get numbered [1], [2], [3] markers

**Independent Test**: Create Typst document with @[key] citations, convert to DOCX, verify inline [1], [2] markers appear

### Tests for User Story 1

> **NOTE**: Tests MUST be written and FAIL before implementation

- [ ] T013 [P] [US1] Create test fixture `tests/fixtures/typ/bibliography/basic.typ` with @[key] citations
- [ ] T014 [P] [US1] Create expected DOCX output `tests/fixtures/docx/bibliography/basic.docx` with numbered citations
- [ ] T015 [P] [US1] Write unit tests for CitationNode in `tests/unit/test_bibliography.py`
- [ ] T016 [US1] Write integration test for inline citations in `tests/integration/test_bibliography.py`

### Implementation for User Story 1

- [ ] T017 [US1] Update scanner to recognize `@[key]` pattern in `src/typst_gost_docx/parser/scanner.py`
- [ ] T018 [US1] Update extractor to parse `@[key]` citations in `src/typst_gost_docx/parser/extractor.py`
- [ ] T019 [US1] Implement citation numbering logic in `src/typst_gost_docx/parser/extractor.py`
  - Track unique keys in order of appearance
  - Assign sequential numbers
  - Handle repeated citations
- [ ] T020 [US1] Write inline citation markers in `src/typst_gost_docx/writers/docx_writer.py`
  - Render [1], [2], [3] in text for NUMERIC style

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Bibliography File Parsing (Priority: P1) 🎯 MVP

**Goal**: System can load and parse BibTeX .bib files with all entry types

**Independent Test**: Load BibTeX file, verify all entry types parse correctly with required fields

### Tests for User Story 2

> **NOTE**: Tests MUST be written and FAIL before implementation

- [ ] T021 [P] [US2] Write unit tests for BibTeX parser in `tests/unit/test_bibliography.py`
- [ ] T022 [P] [US2] Write tests for all BibTeX entry types in `tests/unit/test_bibliography.py`

### Implementation for User Story 2

- [ ] T023 [US2] Implement `#bibliography("file.bib")` parsing in `src/typst_gost_docx/parser/extractor.py`
- [ ] T024 [US2] Implement BibliographyFile loading in `src/typst_gost_docx/ingest/project_loader.py`
- [ ] T025 [US2] Handle missing .bib file with warning (FR-010)
- [ ] T026 [US2] Handle malformed BibTeX entries with warnings
- [ ] T027 [US2] Handle duplicate keys (use first occurrence)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - bibliography can be loaded and citations rendered

---

## Phase 5: User Story 3 - Formatted Bibliography Output (Priority: P2)

**Goal**: Bibliography section in DOCX formatted according to ГОСТ 7.32-2017

**Independent Test**: Convert document with bibliography, verify "Список литературы" section with proper formatting

### Tests for User Story 3

> **NOTE**: Tests MUST be written and FAIL before implementation

- [ ] T028 [P] [US3] Write integration test for bibliography formatting in `tests/integration/test_bibliography.py`
- [ ] T029 [P] [US3] Create test fixture with multiple entry types for formatting tests

### Implementation for User Story 3

- [ ] T030 [US3] Implement bibliography section generation in `src/typst_gost_docx/writers/docx_writer.py`
- [ ] T031 [US3] Format entries according to ГОСТ 7.32-2017:
  - Article: `1. Автор А.А. Название // Журнал. — Год. — С. XX-XX.`
  - Book: `2. Автор Б.Б. Название. — Город: Издательство, Год. — 256 с.`
  - Inproceedings: `3. Автор В.В. Название // Труды конференции. — Год. — С. XX-XX.`
- [ ] T032 [US3] Apply hanging indent (1.25cm) for bibliography entries
- [ ] T033 [US3] Handle long titles with proper line wrapping

**Checkpoint**: At this point, bibliography output should be properly formatted per ГОСТ

---

## Phase 6: User Story 4 - Citation Style Options (Priority: P3)

**Goal**: Users can choose between numeric and author-year citation styles

**Independent Test**: Convert with --bibliography-style author-year, verify (Author, Year) format in text

### Tests for User Story 4

> **NOTE**: Tests MUST be written and FAIL before implementation

- [ ] T034 [P] [US4] Write tests for author-year style in `tests/unit/test_bibliography.py`

### Implementation for User Story 4

- [ ] T035 [US4] Implement author-year inline format in `src/typst_gost_docx/writers/docx_writer.py`
  - Format: `(Smith, 2020)` instead of `[1]`
- [ ] T036 [US4] Sort bibliography alphabetically for author-year style
- [ ] T037 [US4] Implement AUTHOR_YEAR bibliography formatting per ГОСТ

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T038 [P] Update README.md with bibliography documentation
- [ ] T039 [P] Update state.md with completed bibliography feature
- [ ] T040 Add warning for missing keys (FR-011) in `src/typst_gost_docx/parser/validator.py`
- [ ] T041 Handle incomplete entries with placeholder text
- [ ] T042 [P] Add inline comments to BibTeX parser in `src/typst_gost_docx/parser/bibliography.py`
- [ ] T043 [P] Add inline comments to bibliography formatting in `src/typst_gost_docx/writers/docx_writer.py`
- [ ] T044 Run full test suite and verify all tests pass
- [ ] T045 Run ruff check and mypy --strict
- [ ] T046 Update CHANGELOG.md with bibliography feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 and US2
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Depends on US1, US2, US3

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Foundation models before parser implementation
- Core implementation before formatting
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001, T002)
- All Foundational tasks marked [P] can run in parallel (T004, T005, T006)
- Once Foundational phase completes, US1 and US2 can start in parallel
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel

---

## Parallel Example: User Story 1 + User Story 2

```bash
# Launch all tests for US1 + US2 together:
Task: "Create test fixture tests/fixtures/typ/bibliography/basic.typ"
Task: "Write unit tests for CitationNode"
Task: "Write unit tests for BibTeX parser"

# Launch all foundational models in parallel:
Task: "Add BibliographyType enum to ir/model.py"
Task: "Add CitationStyle enum to ir/model.py"
Task: "Add BibliographyEntry model to ir/model.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Inline Citations)
4. Complete Phase 4: User Story 2 (Bibliography Parsing)
5. **STOP and VALIDATE**: Test bibliography works - citations render [1], [2], bibliography section generates
6. Deploy/demo if ready (basic MVP)

### Full Feature Delivery

1. Complete Phase 5: User Story 3 (ГОСТ Formatting)
2. Complete Phase 6: User Story 4 (Citation Styles)
3. Complete Phase 7: Polish
4. Final release with full bibliography support

---

## Success Criteria Coverage

Each success criterion from spec.md is covered by tasks:

- **SC-001**: T013, T016, T017, T018, T019, T020 - Inline citations [1], [2], [3]
- **SC-002**: T030, T031 - Bibliography section with correct entry count
- **SC-003**: T010, T021, T022 - All BibTeX entry types parse correctly
- **SC-004**: T019 - Repeated citations use same number
- **SC-005**: T030, T031, T032, T033 - ГОСТ 7.32-2017 formatting
- **SC-006**: T044 - Performance test for 50 citations

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence