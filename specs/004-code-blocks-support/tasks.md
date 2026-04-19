---
description: "Task list for Code Blocks Support feature implementation"
---

# Tasks: Code Blocks Support

**Input**: Design documents from `/specs/004-code-blocks-support/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [ ] T001 [P] Create test fixtures directory `tests/fixtures/typ/code-blocks/`
- [ ] T002 [P] Create test fixture `tests/fixtures/typ/code-blocks/basic.typ` with Python code block

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

⚠️ **CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 [P] Add `CODE_BLOCK` to `NodeType` enum in `src/typst_gost_docx/ir/model.py`
- [ ] T004 [P] Add `CodeBlockNode` class to `src/typst_gost_docx/ir/model.py`
- [ ] T005 Update scanner to recognize code block syntax in `src/typst_gost_docx/parser/scanner.py`
  - Pattern: triple backticks followed by optional language
  - Pattern: ```python, ```rust, ```c++, etc.
  - Pattern: content between triple backticks

---

## Phase 3: User Story 1 - Basic Code Block Conversion (Priority: P1) 🎯 MVP

**Goal**: Convert Typst code blocks to DOCX with monospace font

**Independent Test**: Create Typst document with code block, convert to DOCX, verify monospace font and whitespace preservation

### Tests for User Story 1

> **NOTE**: Tests MUST be written and FAIL before implementation

- [ ] T006 [P] [US1] Write unit test for CodeBlockNode in `tests/unit/test_code_blocks.py`
- [ ] T007 [P] [US1] Write unit test for code block parsing in `tests/unit/test_code_blocks.py`

### Implementation for User Story 1

- [ ] T008 [US1] Update extractor to parse code blocks in `src/typst_gost_docx/parser/extractor_v2.py`
  - Recognize triple backtick syntax
  - Extract language identifier
  - Create CodeBlockNode with content and language
- [ ] T009 [US1] Implement code block writing in `src/typst_gost_docx/writers/docx_writer.py`
  - Generate paragraph with monospace font (Courier New / Consolas)
  - Preserve whitespace and line breaks
  - Apply background shading if style_hints contain fill

**Checkpoint**: At this point, basic code blocks should convert to DOCX

---

## Phase 4: User Story 2 - Code Block Styling (Priority: P2)

**Goal**: Support styling options (background color, etc.)

### Tests for User Story 2

> **NOTE**: Tests MUST be written and FAIL before implementation

- [ ] T010 [P] [US2] Write test for code block styling in `tests/integration/test_code_blocks.py`

### Implementation for User Story 2

- [ ] T011 [US2] Add escape special characters in `src/typst_gost_docx/writers/docx_writer.py`
  - Escape `<`, `>`, `&` for XML well-formed output
  - Handle curly braces if in DOCX field context
- [ ] T012 [US2] Implement background shading for code blocks in `src/typst_gost_docx/writers/docx_writer.py`
  - Apply gray background if fill color specified
  - Use paragraph shading or table cell

**Checkpoint**: Code blocks should have proper styling and handle special characters

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T013 [P] Update README.md with code blocks documentation
- [ ] T014 [P] Update state.md with completed code blocks feature
- [ ] T015 [P] Add inline comments to code block handling in docx_writer.py
- [ ] T016 Run full test suite and verify all tests pass
- [ ] T017 Run ruff check and mypy --strict
- [ ] T018 Update CHANGELOG.md with code blocks feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
- **Polish (Phase 5)**: Depends on all desired user stories being complete

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Foundation models before parser implementation
- Core implementation before styling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001, T002)
- All Foundational tasks marked [P] can run in parallel (T003, T004)
- Tests for a user story marked [P] can run in parallel

---

## Success Criteria Coverage

Each success criterion from spec.md is covered by tasks:

- **SC-001**: T009 - Monospace font in DOCX
- **SC-002**: T009 - Whitespace preservation
- **SC-003**: T011 - Escape special characters
- **SC-004**: T005, T008 - Language detection and preservation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies
