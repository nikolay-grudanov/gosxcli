---

description: "Task list for Enhanced Academic Document Support feature implementation"
---

# Tasks: Enhanced Academic Document Support

**Input**: Design documents from `/specs/001-enhanced-academic-support/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included in this task list as specified in the feature specification (E2E testing, regression testing, benchmarking)

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

- [X] T001 Add `latex2mathml` dependency to pyproject.toml as core dependency
- [X] T002 Install `latex2mathml` dependency and verify installation
- [X] T003 [P] Create `fixtures/real_vkr/` directory structure for E2E testing documents
- [X] T004 [P] Create `benchmarks/` directory for performance benchmarking results
- [X] T005 [P] Create regression test directory structure `tests/regression/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

⚠️ **CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Update IR model with new entity types in `src/typst_gost_docx/ir/model.py`
- [X] T007 [P] Add `MathNode` to IR model with `render_mode`, `render_error` fields
- [X] T008 [P] Add `InlineNode`, `InlineRunNode`, `InlineCodeNode`, `CrossRefNode` to IR model
- [X] T009 [P] Add `ChapterContext` entity to IR model
- [X] T010 [P] Add `ColSpec`, `TableHeaderNode`, `TableCellNode`, `TableNode` to IR model
- [X] T011 Update `ParagraphNode` in IR model to use `runs: List[InlineNode]` instead of `content: str`
- [X] T012 Add backward compatibility fallback for `ParagraphNode.content` field
- [X] T013 Update configuration in `src/typst_gost_docx/config.py` with new settings
- [X] T014 [P] Add `ref_labels` configuration for localization
- [X] T015 [P] Add `math_mode` configuration option
- [X] T016 Add `strict_mode` configuration option

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Academic Thesis Conversion (Priority: P1) 🎯 MVP

**Goal**: Enable conversion of multi-file Typst academic documents with complex math, tables, references, and include support

**Independent Test**: Test on anonymous documents `00-vvedenie.typ` and `01-literature-review.typ`. Converter generates DOCX without exceptions, file opens in Word/LibreOffice without errors, structure (headings, tables, formulas) preserved.

### Tests for User Story 1

- [ ] T017 [P] [US1] Create E2E test fixture `fixtures/real_vkr/00-vvedenie.typ` with multi-file structure
- [ ] T018 [P] [US1] Create E2E test fixture `fixtures/real_vkr/01-literature-review.typ` with references
- [ ] T019 [P] [US1] Write E2E test for multi-file include support in `tests/e2e/test_multifile.py`
- [ ] T020 [P] [US1] Write E2E test for math rendering in `tests/e2e/test_math.py`
- [ ] T021 [P] [US1] Write E2E test for complex tables in `tests/e2e/test_tables.py`
- [ ] T022 [P] [US1] Write unit tests for `MathNode` in `tests/unit/test_ir_math.py`
- [ ] T023 [P] [US1] Write unit tests for table parsing in `tests/unit/test_parser_tables.py`

### Implementation for User Story 1

**Multi-file Support (FR-001, FR-002, FR-003)**
- [ ] T024 [US1] Implement recursive file loading in `src/typst_gost_docx/ingest/project_loader.py`
- [ ] T025 [US1] Add depth limit check (max 10 levels) to prevent circular includes
- [ ] T026 [US1] Implement relative path resolution for includes
- [ ] T027 [US1] Add debug logging for loaded file tree

**Math Rendering (FR-004, FR-005, FR-006, FR-007, FR-008, FR-009)**
- [ ] T028 [P] [US1] Create math rendering module `src/typst_gost_docx/writers/math_renderer.py`
- [ ] T029 [US1] Implement LaTeX to MathML/OMML conversion using `latex2mathml`
- [ ] T030 [US1] Implement image fallback for failed math rendering
- [ ] T031 [US1] Add error logging for each math expression that falls back to image
- [ ] T032 [US1] Update parser to extract math expressions in `src/typst_gost_docx/parser/extractor.py`
- [ ] T033 [US1] Update DOCX writer to render math in `src/typst_gost_docx/writers/docx_writer.py`

**Complex Table Support (FR-010, FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017)**
- [ ] T034 [P] [US1] Update parser to extract table attributes in `src/typst_gost_docx/parser/extractor.py`
- [ ] T035 [P] [US1] Parse `columns` attribute with percentage widths and alignment
- [ ] T036 [P] [US1] Parse `stroke` attribute and convert to border width
- [ ] T037 [P] [US1] Parse `fill` lambda patterns for header shading detection
- [ ] T038 [P] [US1] Parse `align` lambda patterns for header/body alignment
- [ ] T039 [P] [US1] Parse `colspan` and `rowspan` attributes in cells
- [ ] T040 [P] [US1] Update table writer in `src/typst_gost_docx/writers/tables.py`
- [ ] T041 [US1] Implement grid span (`<w:gridSpan>`) generation for colspan
- [ ] T042 [US1] Implement vertical merge (`<w:vMerge>`) generation for rowspan
- [ ] T043 [US1] Apply table border width to `<w:tcBorders>`
- [ ] T044 [US1] Apply header shading to `<w:shd>` when `header_shaded = True`
- [ ] T045 [US1] Apply header and body alignment to cells
- [ ] T046 [US1] Generate column widths via `<w:tblGrid>` and `<w:gridCol>`
- [ ] T047 [US1] Separate `table.header(...)` processing into `TableHeaderNode`

**Nested Tables (FR-018)**
- [ ] T048 [US1] Implement nested table detection in parser
- [ ] T049 [US1] Generate nested `<w:tbl>` inside `<w:tc>` in writer

**Chapter-Aware References (FR-019, FR-020, FR-021, FR-022, FR-023, FR-024)**
- [ ] T050 [P] [US1] Implement `ChapterContext` in writer for tracking chapter numbers
- [ ] T051 [P] [US1] Update reference resolution in `src/typst_gost_docx/parser/refs.py`
- [ ] T052 [US1] Detect reference patterns by prefix (fig:, tbl:, eq:, ch:)
- [ ] T053 [US1] Implement chapter-aware numbering with counter reset
- [ ] T054 [US1] Format references with localized text from config
- [ ] T055 [US1] Update cross-reference rendering in `src/typst_gost_docx/writers/docx_writer.py`

**TOC Support (FR-028)**
- [ ] T056 [US1] Implement `#outline()` parsing in `src/typst_gost_docx/parser/extractor.py`
- [ ] T057 [US1] Generate DOCX Table of Contents field in writer

**Bidirectional Validation (FR-025, FR-026, FR-027)**
- [ ] T058 [US1] Implement bidirectional validation after IR traversal
- [ ] T059 [US1] Compare defined_labels vs referenced_labels sets
- [ ] T060 [US1] Log WARNING for undefined references
- [ ] T061 [US1] Log INFO for unreferenced labels
- [ ] T062 [US1] Exit with code 1 in strict mode when undefined references found

**CLI Updates**
- [ ] T063 [US1] Add `--math-mode [native|image|fallback]` flag to CLI
- [ ] T064 [US1] Add `--strict` flag to CLI
- [ ] T065 [US1] Add `--debug` flag to CLI for file tree logging

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Rich Text Formatting Support (Priority: P2)

**Goal**: Support inline formatting (bold, italic, code, links) within paragraphs

**Independent Test**: Test on fixture `fixtures/inline_formatting.typ`. Converter generates DOCX where paragraphs contain mixed runs (bold + normal + code in one paragraph).

### Tests for User Story 2

- [ ] T066 [P] [US2] Create inline formatting fixture `fixtures/inline_formatting.typ`
- [ ] T067 [P] [US2] Write unit tests for inline parsing in `tests/unit/test_parser_inline.py`
- [ ] T068 [P] [US2] Write unit tests for inline rendering in `tests/unit/test_writers_inline.py`

### Implementation for User Story 2

**Inline Formatting (FR-029, FR-030, FR-031, FR-032, FR-033)**
- [ ] T069 [P] [US2] Update parser to extract inline formatting in `src/typst_gost_docx/parser/extractor.py`
- [ ] T070 [P] [US2] Parse bold text `*text*` into `InlineRunNode(bold=True)`
- [ ] T071 [P] [US2] Parse italic text `_text_` into `InlineRunNode(italic=True)`
- [ ] T072 [P] [US2] Parse inline code `` `code` `` into `InlineCodeNode`
- [ ] T073 [P] [US2] Parse hyperlinks `#link("url")[text]` into cross-reference nodes
- [ ] T074 [US2] Update paragraph writer to handle runs list in `src/typst_gost_docx/writers/docx_writer.py`
- [ ] T075 [US2] Generate bold formatting with `<w:b/>` runs
- [ ] T076 [US2] Generate italic formatting with `<w:i/>` runs
- [ ] T077 [US2] Generate code formatting with `<w:rStyle w:val="Code"/>` runs
- [ ] T078 [US2] Generate hyperlinks with `<w:hyperlink r:id="...">` elements
- [ ] T079 [US2] Implement backward compatibility: fallback to `content` field when `runs` empty

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Reference Validation and Error Reporting (Priority: P2)

**Goal**: Provide comprehensive reference validation and error reporting for documents

**Independent Test**: Test on document with intentionally undefined references. Converter outputs WARNING for each undefined reference and INFO for each unreferenced label.

### Tests for User Story 3

- [ ] T080 [P] [US3] Create validation test fixture `fixtures/reference_validation.typ`
- [ ] T081 [P] [US3] Write unit tests for validation logic in `tests/unit/test_validation.py`
- [ ] T082 [P] [US3] Write integration test for strict mode exit code in `tests/integration/test_strict_mode.py`

### Implementation for User Story 3

**Note**: Reference validation is implemented in User Story 1 (T058-T062). This story focuses on enhancing and testing the validation.

- [ ] T083 [US3] Enhance validation error messages with file and line information
- [ ] T084 [US3] Add detailed reporting for undefined references
- [ ] T085 [US3] Add detailed reporting for unreferenced labels
- [ ] T086 [US3] Add validation summary statistics (total labels, referenced count, unreferenced count)
- [ ] T087 [US3] Update logging module to support validation-specific log levels
- [ ] T088 [US3] Add validation report generation in `src/typst_gost_docx/parser/refs.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Performance Benchmarking and Regression Testing (Priority: P3)

**Goal**: Implement regression testing and performance benchmarking to ensure quality and stability

**Independent Test**: Run `make regression` and `make benchmark`. System generates reports about discrepancies with golden files and measures conversion time.

### Tests for User Story 4

- [ ] T089 [P] [US4] Create golden file for `fixtures/minimal.typ`
- [ ] T090 [P] [US4] Create golden file for `fixtures/complex_table.typ`
- [ ] T091 [P] [US4] Create golden file for `fixtures/math_example.typ`
- [ ] T092 [P] [US4] Write regression test framework in `tests/regression/test_regression.py`

### Implementation for User Story 4

**Regression Testing (FR-013, FR-036, SC-013)**
- [ ] T093 [US4] Create regression test framework in `tests/regression/`
- [ ] T094 [US4] Implement golden file comparison logic
- [ ] T095 [US4] Add `make regression` target to Makefile
- [ ] T096 [US4] Generate regression reports with diff details
- [ ] T097 [US4] Update golden files after intentional changes

**Performance Benchmarking (FR-037, FR-038, SC-010)**
- [ ] T098 [US4] Create benchmark framework in `benchmarks/`
- [ ] T099 [US4] Implement time measurement for conversion operations
- [ ] T100 [US4] Add `--benchmark` flag to CLI
- [ ] T101 [US4] Store benchmark results in `benchmarks/results.json`
- [ ] T102 [US4] Add performance thresholds: minimal.typ < 1 sec, 01-literature-review.typ < 10 sec
- [ ] T103 [US4] Generate benchmark reports with historical comparisons

**E2E Testing (FR-034, FR-035, SC-004)**
- [ ] T104 [US4] Implement DOCX structure validation in E2E tests
- [ ] T105 [US4] Check heading count in generated documents
- [ ] T106 [US4] Check table presence in generated documents
- [ ] T107 [US4] Check for empty paragraphs and minimize them
- [ ] T108 [US4] Add `make e2e` target to Makefile

**Checkpoint**: All testing infrastructure now complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T109 [P] Update README.md with v0.2 features and usage examples
- [ ] T110 [P] Add documentation for `--math-mode` flag
- [ ] T111 [P] Add documentation for `--strict` flag
- [ ] T112 [P] Add documentation for multi-file include support
- [ ] T113 Update project state.md with completed features
- [ ] T114 [P] Add inline comments to complex table rendering logic
- [ ] T115 [P] Add inline comments to math rendering logic
- [ ] T116 [P] Optimize recursive include loading performance
- [ ] T117 [P] Optimize table generation for large tables
- [ ] T118 [P] Add additional error handling for edge cases
- [ ] T119 Run quickstart.md validation scenarios
- [ ] T120 Update pyproject.toml with new dependencies and version
- [ ] T121 [P] Add smoke tests for new features to maintain v0.1 compatibility (SC-002)
- [ ] T122 Ensure all 25+ new tests pass (SC-003)
- [ ] T123 Verify DOCX files open in Microsoft Word without errors (SC-011)
- [ ] T124 Verify DOCX files open in LibreOffice without errors (SC-011)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 validation (T058-T062), but can enhance independently
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Requires all other stories to have testable implementations

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Core model updates before service layer
- Service layer before UI/writer layer
- Integration after individual components
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- All Foundational tasks marked [P] can run in parallel (T007, T008, T009, T010, T011, T014, T015)
- Once Foundational phase completes, US1, US2, US3 can start in parallel (US4 requires others to be testable)
- All tests for a user story marked [P] can run in parallel
- Math rendering tasks can run in parallel with table parsing tasks (within US1)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create E2E test fixture fixtures/real_vkr/00-vvedenie.typ with multi-file structure"
Task: "Create E2E test fixture fixtures/real_vkr/01-literature-review.typ with references"
Task: "Write E2E test for multi-file include support in tests/e2e/test_multifile.py"
Task: "Write E2E test for math rendering in tests/e2e/test_math.py"
Task: "Write E2E test for complex tables in tests/e2e/test_tables.py"
Task: "Write unit tests for MathNode in tests/unit/test_ir_math.py"
Task: "Write unit tests for table parsing in tests/unit/test_parser_tables.py"

# Launch all table attribute parsing tasks together:
Task: "Parse columns attribute with percentage widths and alignment"
Task: "Parse stroke attribute and convert to border width"
Task: "Parse fill lambda patterns for header shading detection"
Task: "Parse align lambda patterns for header/body alignment"
Task: "Parse colspan and rowspan attributes in cells"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T016) - **CRITICAL**
3. Complete Phase 3: User Story 1 (T017-T065)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready
6. Expected outcome: Multi-file Typst academic document conversion with math, tables, and references

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T016)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T016)
2. Once Foundational is done:
   - Developer A: User Story 1 (Academic Thesis Conversion)
   - Developer B: User Story 2 (Rich Text Formatting)
   - Developer C: User Story 3 (Reference Validation)
3. After US1, US2, US3 are complete:
   - Developer D: User Story 4 (Performance & Regression)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are included per specification (E2E, regression, benchmarking)
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Success Criteria Coverage

Each success criterion from spec.md is covered by tasks:

- **SC-001**: T019, T020, T021 - E2E tests for multi-file conversion
- **SC-002**: T121 - Smoke tests maintain v0.1 compatibility
- **SC-003**: T017-T023, T066-T068, T080-T082, T089-T092 - 25+ new tests
- **SC-004**: T017-T022, T104-T108 - E2E tests on real documents
- **SC-005**: T029, T033 - Math rendering as OMML
- **SC-006**: T034-T046 - Complex table support
- **SC-007**: T050-T055 - Chapter-aware cross-references
- **SC-008**: T069-T078 - Inline formatting
- **SC-009**: T024-T027 - Multi-file include support
- **SC-010**: T098-T103 - Performance benchmarking
- **SC-011**: T123, T124 - DOCX compatibility
- **SC-012**: T058-T062, T080-T088 - Reference validation
- **SC-013**: T093-T097 - Regression testing
