# Tasks: GOST Template Integration

**Input**: Design documents from `/specs/005-template-integration/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/style-resolution.md, quickstart.md

**Tests**: Тесты не запрошены в спецификации — задачи по тестам не включены.

**Organization**: Задачи сгруппированы по user stories для независимой реализации и тестирования.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Можно выполнять параллельно (разные файлы, нет зависимостей)
- **[Story]**: Принадлежность к user story (US1, US2, US3)
- Все пути указаны относительно корня репозитория

## Path Conventions

- **Single project layout**: `src/typst_gost_docx/`, `tests/` в корне репозитория

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Создание инфраструктуры для встроенного шаблона ГОСТ

- [x] T001 Create `src/typst_gost_docx/templates/` directory with `__init__.py` and copy `Шаблон_оформления_ВКР_2026_новый.docx` from `template/` directory
- [x] T002 Add `[tool.setuptools.package-data]` section to `pyproject.toml` to include `templates/*.docx` in package distribution
- [x] T003 [P] Verify template packaging: run `pip install -e .` and confirm template file is accessible via `importlib.resources`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core StyleResolver и TemplateLoader — MUST complete before ANY user story

**⚠️ CRITICAL**: Работа над user stories не может начаться до завершения этой фазы

- [x] T004 [P] Replace stub `StylesManager` with `IR_STYLE_MAP` dict constant and `UNNUMBERED_KEYWORDS` frozenset constant in `src/typst_gost_docx/writers/styles.py`
- [x] T005 [P] Implement `get_default_template_path()` using `importlib.resources` and `load_document()` with fallback logic in `src/typst_gost_docx/writers/styles.py`
- [x] T006 Implement `StyleResolver` class with `resolve()`, `apply_paragraph_style()`, `_lookup_style()`, `_resolve_by_fuzzy()` methods in `src/typst_gost_docx/writers/styles.py` (depends on T004)
- [x] T007 Remove `_configure_styles()` method from `DocxWriter` and add `StyleResolver` initialization in `__init__()` in `src/typst_gost_docx/writers/docx_writer.py`
- [x] T008 Update `DocxWriter.write()` to use `load_document()` from `styles.py` instead of direct `Document()` constructor, initialize `StyleResolver` after document creation in `src/typst_gost_docx/writers/docx_writer.py`

**Checkpoint**: Foundation ready — StyleResolver и TemplateLoader работают, `_configure_styles()` удалён

---

## Phase 3: User Story 1 — Default GOST Template Output (Priority: P1) 🎯 MVP

**Goal**: Конвертация Typst→DOCX использует встроенный шаблон ВКР по умолчанию: Times New Roman 14pt, чёрные заголовки, без вызова `_configure_styles()`

**Independent Test**: Конвертировать тестовый .typ файл без `--reference-doc`, проверить что DOCX использует стили из шаблона (Times New Roman, чёрные Heading 1-3) без ручной настройки шрифтов в коде

### Implementation for User Story 1

- [x] T009 [US1] Update `_write_section()` to use `StyleResolver.apply_paragraph_style()` for heading styles instead of `style=style_name` string in `src/typst_gost_docx/writers/docx_writer.py`
- [x] T010 [US1] Update `_write_paragraph()` to use `StyleResolver` for applying Normal style from template in `src/typst_gost_docx/writers/docx_writer.py`
- [x] T011 [US1] Update `_write_caption()` to use `StyleResolver` for Caption style instead of hardcoded `style="Caption"` in `src/typst_gost_docx/writers/docx_writer.py`
- [x] T012 [US1] Update `_write_toc()` and `_write_bibliography()` to use `StyleResolver.apply_paragraph_style()` for Heading 1 style in `src/typst_gost_docx/writers/docx_writer.py`
- [x] T013 [US1] Update `_write_list()` to use `StyleResolver` for list styles (List Bullet, List Number) in `src/typst_gost_docx/writers/docx_writer.py`

**Checkpoint**: User Story 1 полностью функционален — конвертация без `--reference-doc` использует встроенный ГОСТ шаблон, стили применяются корректно

---

## Phase 4: User Story 2 — Custom Template Styles for Structural Elements (Priority: P2)

**Goal**: Структурные элементы (ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ, подписи рисунков/таблиц, формулы) используют специализированные стили из шаблона ВКР

**Independent Test**: Конвертировать документ с ненумерованными заголовками (ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ), подписями рисунков и таблиц, проверить что применяются `Заг_не_содержание`, `Подпись рисунков`, `Таблица название` стили из шаблона

### Implementation for User Story 2

- [x] T014 [US2] Add `_is_unnumbered_heading()` helper method using `UNNUMBERED_KEYWORDS` to `DocxWriter` in `src/typst_gost_docx/writers/docx_writer.py`
- [x] T015 [US2] Update `_write_section()` to detect unnumbered headings via `_is_unnumbered_heading()` and apply `Заг_не_содержание` style via `StyleResolver` with fallback to `Heading 1` in `src/typst_gost_docx/writers/docx_writer.py`
- [x] T016 [US2] Update `_write_caption()` to differentiate figure vs table captions: use `Подпись рисунков` for figures and `Таблица название` for tables via `StyleResolver` in `src/typst_gost_docx/writers/docx_writer.py`
- [x] T017 [US2] Update `_write_equation()` to apply `Формулы` style from template via `StyleResolver` for equation paragraphs in `src/typst_gost_docx/writers/docx_writer.py`
- [x] T018 [US2] Update `TablesManager.add_table()` to use `Table Grid` style from template in `src/typst_gost_docx/writers/tables.py`

**Checkpoint**: User Story 2 полностью функционален — кастомные стили шаблона применяются для всех структурных элементов

---

## Phase 5: User Story 3 — CLI Template Path Override (Priority: P3)

**Goal**: Пользователь может указать свой шаблон через `--reference-doc`, использовать встроенный шаблон по умолчанию, или получить fallback на `Document()` при отсутствии шаблона

**Independent Test**: Запустить CLI с `--reference-doc custom.docx` → используется пользовательский шаблон. Без `--reference-doc` → используется встроенный. Удалить шаблон → fallback с warning.

### Implementation for User Story 3

- [x] T019 [US3] Update `cli.py` `_run_conversion()` to pass resolved template path to DocxWriter and show which template is used in debug output in `src/typst_gost_docx/cli.py`
- [x] T020 [US3] Add template info to `_print_summary()` output (template path, fallback status) in `src/typst_gost_docx/cli.py`
- [x] T021 [US3] Verify fallback chain in `load_document()`: custom `--reference-doc` → built-in template → `Document()` with warnings in `src/typst_gost_docx/writers/styles.py`

**Checkpoint**: Все три user stories независимо функциональны

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Качество кода, валидация, финальная проверка

- [x] T022 [P] Run `ruff check src/typst_gost_docx/writers/` and `ruff format src/typst_gost_docx/writers/` to fix linting and formatting issues
- [x] T023 [P] Run `mypy --strict src/typst_gost_docx/writers/styles.py src/typst_gost_docx/writers/docx_writer.py` and fix type errors
- [x] T024 Run quickstart.md validation scenarios: (1) default template conversion, (2) custom `--reference-doc`, (3) fallback without template

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion — BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start after Phase 2
  - US2 (Phase 4): Depends on US1 (modifies same methods in docx_writer.py)
  - US3 (Phase 5): Can start after Phase 2 (mostly CLI changes, independent of US1/US2)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (StyleResolver + TemplateLoader)
    ↓
Phase 3: US1 (Default GOST Template) ── MVP
    ↓
Phase 4: US2 (Custom Structural Styles) ← depends on US1
    ↓
Phase 5: US3 (CLI Override) ← can start after Phase 2
    ↓
Phase 6: Polish
```

- **US1 (P1)**: Depends on Foundational only — no dependencies on other stories
- **US2 (P2)**: Depends on US1 — extends `_write_section()`, `_write_caption()` methods modified in US1
- **US3 (P3)**: Depends on Foundational only — mostly CLI changes, independent of US1/US2

### Parallel Opportunities

Within Phase 1:
- T001 and T002 can run in parallel (different files: directory creation vs pyproject.toml)

Within Phase 2:
- T004, T005 can run in parallel (different concerns in same file, but additive — constants vs loader functions)

Within Phase 6:
- T022 and T023 can run in parallel (different tools: ruff vs mypy)

---

## Parallel Example: Phase 2

```bash
# Launch in parallel (different code sections in styles.py):
Task: "Replace StylesManager with IR_STYLE_MAP and UNNUMBERED_KEYWORDS in writers/styles.py"
Task: "Implement TemplateLoader functions (get_default_template_path, load_document) in writers/styles.py"

# Then sequential:
Task: "Implement StyleResolver class in writers/styles.py"
Task: "Update DocxWriter to use StyleResolver and TemplateLoader in writers/docx_writer.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup — templates/ directory + pyproject.toml
2. Complete Phase 2: Foundational — StyleResolver + TemplateLoader
3. Complete Phase 3: User Story 1 — basic template usage
4. **STOP and VALIDATE**: Convert test .typ file, verify styles from template
5. Confirm: Times New Roman 14pt, black headings, no `_configure_styles()` call

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test (MVP: default GOST template works) → Validate
3. Add US2 → Test (structural styles: ВВЕДЕНИЕ, подписи) → Validate
4. Add US3 → Test (CLI override: --reference-doc) → Validate
5. Polish → Final validation with quickstart.md

### Key Files Modified

| File | Action | Phase |
|------|--------|-------|
| `src/typst_gost_docx/templates/__init__.py` | CREATE | Phase 1 |
| `src/typst_gost_docx/templates/Шаблон_оформления_ВКР_2026_новый.docx` | COPY | Phase 1 |
| `pyproject.toml` | MODIFY | Phase 1 |
| `src/typst_gost_docx/writers/styles.py` | REWRITE | Phase 2 |
| `src/typst_gost_docx/writers/docx_writer.py` | MODIFY | Phase 2-4 |
| `src/typst_gost_docx/writers/tables.py` | MODIFY | Phase 4 |
| `src/typst_gost_docx/cli.py` | MODIFY | Phase 5 |

---

## Notes

- [P] tasks = разные файлы или разные участки кода, нет зависимостей
- [Story] label привязывает задачу к конкретному user story
- Каждый user story независимо тестируем и доставляем
- IR модель (`ir/model.py`) НЕ затрагивается — чисто Writer-side изменения
- После каждой фазы: `ruff check src/ && ruff format src/ && mypy --strict src/`
- Проверить что `_configure_styles()` полностью удалён и нигде не вызывается
- Шаблон ВКР содержит нестандартные style_id (781, 782, 783) — StyleResolver должен обрабатывать это через итеративный поиск
