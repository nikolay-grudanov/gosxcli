# Project State: gosxcli

**Last Updated:** 2026-06-24 (v0.5.0 → Spec 001 Enhanced Academic Support closed)
**Version:** v0.5.0 (Enhanced Academic Support)
**Status:** Spec 001-enhanced-academic-support полностью реализован ✅ (T001-T124 closed)

### Key Metrics
- Lines of Code: ~6,800 (35 Python source files)
- Test Files: 33 (+ unit/regression/benchmark suites)
- Test Cases: 310 (all passing, 0 ruff/mypy errors)

### Spec 001 — Enhanced Academic Support (closed)
- T073 + T078: Inline `#link()` rendered as `<w:hyperlink r:id>` with TargetMode="External" relationships.
- T081, T083-T088: `ReferenceValidator` collects source locations; new `ValidationIssue` with file:line; `format_report` groups by kind and prints `path:N: @label`. Strict mode exits with code 1.
- T103: `benchmarks/compare.py` reads `benchmarks/results/*.json`, groups by fixture, emits min/mean/max/stddev trend report. Old-schema files are skipped with a warning.
- Regression suite (`tests/regression/`) compares output DOCX against golden files for `minimal`, `complex_table`, `equations`.
- Benchmark suite (`benchmarks/test_benchmarks.py`) tracks conversion time against per-fixture thresholds (1 s / 5 s / 10 s).
- Ruff Errors: 0
- Mypy: Passing (0 errors)
- Source Files: 31

---

## Progress Tracker

### v0.1 (MVP) ✅
| Feature | Status | Notes |
|---------|--------|-------|
| Headings | ✅ Complete | Levels 1-3 supported |
| Paragraphs | ✅ Complete | Basic formatting |
| Lists | ✅ Complete | Bullet and numbered |
| Tables | ✅ Complete | Basic support only |
| Figures | ✅ Complete | With captions |
| References | ✅ Complete | @label resolution |
| Math | ⚠️ MVP | Complex formulas as placeholders |

### v0.2 (Feature Complete) ✅
| Feature | Status | Notes |
|---------|--------|-------|
| Enhanced math | ✅ Complete | latex2mathml integration, T028-T031 |
| Table attributes | ✅ Complete | columns, stroke, fill, align, colspan, rowspan |
| colspan/rowspan | ✅ Complete | TablesManager с gridSpan, vMerge |
| Better refs | ✅ Complete | CrossRefNode, ChapterContext, chapter-aware numbering |
| Chapter numbering | ✅ Complete | ChapterContext integrated in DocxWriter |
| Inline formatting | ✅ Complete | InlineNode, InlineRunNode, emphasis, strong |
| Bidirectional validation | ✅ Complete | ReferenceValidator, ValidationResult |
| Table of Contents | ✅ Complete | #outline() parsing и DOCX TOC generation |
| Multi-file support | ✅ Complete | #include recursive loading with depth protection |
| Bibliography | ✅ Complete | BibTeX parser, @[key] citations, numeric/author-year styles |
| CLI flags | ✅ Complete | --math-mode, --strict, --debug, --benchmark |
| Nested tables | ✅ Complete | Table detection in figures, nested table generation |
| Performance benchmarking | ✅ Complete | pytest-benchmark, ~13-20ms |
| E2E structure tests | ✅ Complete | 10 E2E tests for DOCX validation |
| Regression testing | ✅ Complete | Golden file comparison framework |

### v0.2.1 (Code Blocks Support) ✅
| Feature | Status | Notes |
|---------|--------|-------|
| Code blocks IR | ✅ Complete | CodeBlockNode model |
| Code blocks parsing | ✅ Complete | ```language\n...\n``` extraction |
| Code blocks writer | ✅ Complete | Monospace font, XML escaping, background shading |
| Code blocks tests | ✅ Complete | 14 unit + 8 integration tests |

### v0.3.0 (Syntax Highlighting) ✅
| Feature | Status | Notes |
|---------|--------|-------|
| Pygments integration | ✅ Complete | pygments>=2.17.0 in dependencies |
| VS Code Dark+ scheme | ✅ Complete | Dark theme with proper token colors |
| Syntax highlighting writer | ✅ Complete | writers/code_highlighter.py |
| Language support | ✅ Complete | Python, Rust, JavaScript, C, C++, Go |
| DocxWriter integration | ✅ Complete | _write_code_block() with highlighting |

---

## v0.3.1 — Bug Fixes + Style Improvements ✅

### Parser Bug Fixes ✅ (commit d68f209)
1. **OMML rendering** — создан `writers/mml2omml.py` (MathML→OMML конвертер)
2. **Label misattribution** — whitespace token skipping перед LABEL check
3. **Table not parsed** — автоматически исправлен фиксом label
4. **Ref colon support** — scanner поддерживает `@tbl:test`, `@eq:formula`

### Style & Formatting Fixes ✅ (commit b2355f7)
5. **Font Normal** — Times New Roman 14pt через `_configure_styles()` + XML rFonts
6. **Heading color** — чёрный вместо синего (RGBColor(0,0,0))
7. **Heading font** — Times New Roman через XML rFonts для Heading 1-3
8. **Heading numbering** — иерархическая нумерация (1, 1.1, 1.1.1) через `heading_counters` в ChapterContext
9. **Inline math** — `_write_text_with_inline_math()` для разбора `$...$` внутри текста
10. **Cross-reference resolution** — `label_number_map` для резолвинга номеров фигур/таблиц/формул
11. **Image path resolution** — `base_dir` в ImagesManager, резолвинг относительно `input_file.parent`
12. **Test image** — `fixtures/minimal/test.png` (200x100 PNG) для тестирования вставки

### Real Thesis Bug Fixes ✅ (new)
13. **Image path resolution for chapters** — добавлен метод `_rewrite_image_paths()` в project_loader.py для исправления путей изображений из глав (chapters/) относительно корня проекта
14. **Bibliography citation recognition** — добавлен параметр `bib_keys` в TypstExtractorV2 для распознавания цитирований `@key` против перекрёстных ссылок
15. **Missing styles fallback** — добавлен метод `_create_fallback_style()` в StyleResolver для динамического создания стилей List Bullet, List Number, Heading N при отсутствии в шаблоне

### ⏳→✅ BLOCKING RESOLVED: Референсный документ получен
**Шаблон получен:** `template/Шаблон_оформления_ВКР_2026_новый.docx`
- Проанализированы стили через python-docx и XML ✅
- Создан план интеграции: `specs/005-template-integration/` ✅
- **Критическое открытие:** Нестандартные style_id ('781','782','783') для Heading 1-3 — `doc.styles['Heading 1']` → KeyError
- Решение: StyleResolver с итеративным fallback + кэширование ✅

---

## v0.4.0 — GOST Template Integration (spec 005) ✅

### Phase 1: Setup ✅ (T001-T003)
- `src/typst_gost_docx/templates/` с встроенным ГОСТ шаблоном
- `pyproject.toml` обновлён для включения `templates/*.docx`
- Шаблон доступен через `importlib.resources`

### Phase 2: Foundation ✅ (T004-T008)
- `StyleResolver` с итеративным lookup + кэширование + fuzzy fallback
- `load_document()` с fallback chain: custom → built-in → Document()
- Monkeypatch `Styles.__getitem__` для обхода BabelFish bug с нестандартными style_id
- `_configure_styles()` полностью удалён из DocxWriter
- `initialize_fallback_styles()` для Document() fallback

### Phase 3: Default GOST Template ✅ (T009-T013)
- Все writer методы используют StyleResolver: `_write_section()`, `_write_paragraph()`, `_write_caption()`, `_write_toc()`, `_write_bibliography()`, `_write_list()`
- Normal: Times New Roman 14pt из шаблона
- Heading 1-3: чёрные, Times New Roman, наследование из шаблона

### Phase 4: Custom Template Styles ✅ (T014-T018)
- `_is_unnumbered_heading()`: ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ → стиль `Заг_не_содержание`
- Подписи рисунков → `Подпись рисунков`, таблиц → `Таблица название`
- Формулы → стиль `Формулы`
- Таблицы → `Table Grid` из шаблона

### Phase 5: CLI Template Override ✅ (T019-T021)
- `--reference-doc` для пользовательского шаблона
- Template info в `_print_summary()` (path + source)
- Fallback chain верифицирован: custom → built-in → Document()

### Phase 6: Polish ✅ (T022-T024)
- ruff check: ✅ All checks passed
- mypy --strict: ✅ 0 errors in 32 files
- pytest: ✅ 262 passed
- E2E конвертация с шаблоном верифицирована

---

## Code Review v0.3.0 — Исправления применены

### P0 Quick Fixes ✅ (все выполнены)
1. **`__init__.py`**: `__version__` обновлён "0.2.0" → "0.3.0"
2. **`extractor_v2.py`**: `import re` перемещён на уровень модуля, удалены 13 inline imports
3. **`logging.py`**: Добавлена проверка `if not logger.handlers` для предотвращения handler leak
4. **`ir/model.py`**: `_content: str = ""` → `_content: str = PrivateAttr(default="")` (Pydantic v2)

### P1 Medium Fixes ✅ (все выполнены)
5. **`writers/math_renderer.py`**: Удалён (187 строк мёртвого кода)
6. **`writers/docx_writer.py`**: Удалён неиспользуемый `styles_manager`
7. **Создан `utils/ref_utils.py`**: Функция `infer_ref_kind()` — дедупликация DRY
8. **`docx_writer.py`**: `para: Any` → `para: DocxParagraph` в 4 методах
9. **`code_highlighter.py`**: Bare except теперь логирует debug перед fallback
10. **`images.py`**: Warning при отсутствии файла изображения

### Дополнительные исправления
11. **`bibliography.py`**: Исправлены invalid escape sequences в docstring
12. **`cli.py`, `bibliography.py`**: ruff format применён
13. **`test_chapter_aware_refs.py`**: Обновлён для `infer_ref_kind()` из utils

### Верификация
- ruff check: ✅ All checks passed
- ruff format: ✅ 30 files already formatted
- mypy --strict: ✅ 0 errors in 30 files
- pytest: ✅ 262 passed (0 warnings)

### Файлы изменены
- Modified: `__init__.py`, `extractor_v2.py`, `logging.py`, `ir/model.py`, `docx_writer.py`, `refs.py`, `code_highlighter.py`, `images.py`, `bibliography.py`, `cli.py`, `test_chapter_aware_refs.py`
- Created: `utils/ref_utils.py`
- Deleted: `writers/math_renderer.py`

### Оставшиеся проблемы (P2 — к следующей итерации)
- [A2] Неиспользуемые модули: typst_client.py, typst_query_parser.py, unified_parser.py, regex_fallback_parser.py, labels.py
- [A4] Config duplication: bibliography_style в Config и DocxWriter
- [D2] latex2mathml/pygments как обязательные зависимости (лучше optional)
- [S3] TOC placeholder вместо реального field
- [S4] XML double-escaping риск в _escape_xml_text
- [S6] Отсутствие тестов для Managers (BookmarksManager, ImagesManager)

---

## Known Issues

### High (P1)
1. **Python 3.14 untested** — Project requires >=3.12 but not tested on 3.14
   - Impact: Potential compatibility issues
   - Status: 🟡 Open

### Medium (P2)
2. **Missing tests for Managers** — No tests for ImagesManager, BookmarksManager
   - Impact: Low test coverage for writer components
   - Status: 🟡 Open

3. **Unused parser modules** — typst_client.py, typst_query_parser.py, unified_parser.py, regex_fallback_parser.py not integrated in CLI pipeline
   - Impact: Dead code, confusion
   - Status: 🟡 Open

4. **TOC placeholder** — _write_toc() uses placeholder text instead of real TOC field
   - Impact: Users must manually update TOC in Word
   - Status: 🟡 Open (documented limitation)

5. **XML double-escaping risk** — _escape_xml_text() may double-escape if python-docx also escapes
   - Impact: `&lt;` → `&amp;lt;` in DOCX
   - Status: 🟡 Needs investigation

6. **Dependencies not optional** — latex2mathml, pygments are mandatory but feature-specific
   - Impact: Larger install size for users who don't need these features
   - Status: 🟡 Open

---

## Branch History Anomaly

| Номер | Spec | Ветка | PR | Статус в main |
|-------|------|-------|-----|---------------|
| 001 | ✅ | ❌ | ❌ | Не начата |
| 002 | ✅ | ✅ | ✅ #1 | Вмержена |
| 003 | ✅ | ❌ (работа в 002) | ✅ (в 002) | Вмержена через 002 |
| 004 | ✅ | ✅ | ✅ #2 | Вмержена |
| 005 | ✅ | ✅ | ✅ (pending) | В процессе мержа |

**001 требует отдельной реализации** — spec есть, работа не начата.

---

## Branch History Anomaly (Важное)

### Описание
Ветки 001 и 003 НЕ были созданы как отдельные feature branches. Это особенность исторического развития проекта:

| Номер | Spec существует | Ветка создана | PR |
|-------|-----------------|---------------|-----|
| 001 | ✅ specs/001-enhanced-academic-support/ | ❌ НЕТ | ❌ НЕТ |
| 002 | ✅ (часть 002 работы) | ✅ Да | ✅ #1 (merged) |
| 003 | ✅ specs/003-bibliography-support/ | ❌ НЕТ (работа в 002) | ✅ #1 (вмержена в 002) |
| 004 | ✅ specs/004-code-blocks-support/ | ✅ Да | ✅ #2 (merged) |

### Причина
- **003 (bibliography)**: Работа была выполнена в ветке 002 вместо отдельной 003
- **001 (enhanced academic)**: Spec создан, но работа НЕ начата

### Как работать с этим
1. При создании новой фичи - создавай отдельную ветку с номером
2. Не объединяй разные фичи в одну ветку
3. 001 требует отдельной реализации с нуля

### Текущее состояние
- `main` = 002 + 004 (bibliography + code blocks вмержены)
- 001 и 003 работают в main но не как отдельные ветки

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Ratify constitution v1.0.0 | Establish project governance principles |
| 2026-04-19 | Add state.md | Track project status and progress |
| 2026-04-19 | 4-layer pipeline: Ingest → Parser → IR → Writer | Clean separation of concerns |
| 2026-04-19 | Pydantic v2 for all models | Consistent validation and serialization |
| 2026-04-19 | Multi-file loading with #include | Real VRK documents use multiple files |
| 2026-04-19 | TOC placeholder approach | python-docx limited TOC field support |
| 2026-04-19 | Bidirectional reference validation | Catch broken references early |
| 2026-04-20 | Code blocks with Pygments highlighting | VS Code Dark+ theme for readability |
| 2026-05-12 | v0.3.0 Code Review fixes | Removed dead code, fixed Pydantic, DRY dedup, type safety |
| 2026-05-12 | Delete math_renderer.py (dead code) | Inline rendering in docx_writer; separate module was unused |
| 2026-05-12 | Extract infer_ref_kind() to utils/ref_utils.py | DRY principle — was duplicated in docx_writer.py and refs.py |
| 2026-05-12 | PrivateAttr for _content in Paragraph | Pydantic v2 doesn't support _-prefixed fields without PrivateAttr |
| 2026-05-24 | Spec 005-template-integration plan created | Референсный ВКР шаблон получен, StyleResolver с итеративным fallback для нестандартных style_id |
| 2026-05-24 | Non-standard style_id workaround | Heading 1-3 имеют style_id '781-783' вместо стандартных 'Heading1-3'; решается итеративным поиском |
| 2026-05-24 | 005 Phase 2: StyleResolver + TemplateLoader | Monkeypatch Styles.__getitem__ для обхода BabelFish bug; _clear_document_body() для очистки контента шаблона; initialize_fallback_styles() для Document() fallback |
| 2026-05-24 | 005 Phase 4: Custom Template Styles | Реализованы T014-T018: _is_unnumbered_heading(), обнаружение ненумерованных заголовков, раздельные стили caption_table/caption_figure, equation стиль, обработка KeyError для Table Grid |
| 2026-05-29 | 005 Spec полностью завершён | Все Phase 1-6 реализованы (T001-T024). Удалён tmp-test/ мусор. StyleResolver + TemplateLoader работают. E2E верификация пройдена |

---

## Next Steps

### ✅ Spec 005 — Полностью завершён
- [x] Реализовать spec 005-template-integration Phase 1-2 (T001-T008)
- [x] Реализовать spec 005 Phase 3 (T009-T013)
- [x] Реализовать spec 005 Phase 4 (T014-T018)
- [x] Реализовать spec 005 Phase 5-6 (T019-T024)
- [x] Очистка tmp-test/ и .gitignore
- [x] Обновить state.md

### ✅ Spec 001 — Полностью завершён
- [x] T073 + T078: inline `#link()` parser + writer
- [x] T081, T083-T088: validation with file:line, summary stats, dedicated report
- [x] T089-T108: regression suite + benchmark suite + historical report
- [x] T109-T113, T120: README, state.md, version bump
- [x] Push 4 commits (984aac6, 2b25a1b, 5b2faeb, 6a0d002) → origin/001-enhanced-academic-support
- [ ] Open PR → main
- [x] **Dead-code cleanup:** removed 5 unused parser modules (parser/unified_parser.py, parser/typst_query_parser.py, parser/regex_fallback_parser.py, parser/labels.py, ingest/typst_client.py). Migrated `tests/test_refs.py` and `tests/real_vkr/test_real_vkr.py` to use the canonical `TypstExtractorV2` + `RefResolver` pipeline.

### Immediate
- [ ] Open PR for 001-enhanced-academic-support → main
- [ ] Consider git tag v0.5.0 after PR merge

### Short Term (v0.5.x)
1. ~~Remove 5 dead parser modules (typst_client, typst_query_parser, unified_parser, regex_fallback_parser, labels)~~ ✅ done in v0.5.0 cleanup
2. Make `latex2mathml`, `pygments` optional dependencies
3. Add tests for `BookmarksManager`, `ImagesManager`
4. Investigate XML double-escaping risk in `_escape_xml_text`

### Medium Term (v0.6)
5. Real TOC field generation (replace placeholder with `<w:fldChar>`)
6. Full GOST 7.32-2017 compliance audit
7. Better error handling for edge cases in `#include` parsing
8. Full GOST 7.32-2017 compliance
9. Code blocks with syntax highlighting improvements
10. Better error handling for edge cases

---

## Resources

- **Constitution:** [.specify/memory/constitution.md](.specify/memory/constitution.md)
- **Architecture:** [AGENTS.md](AGENTS.md)
- **README:** [README.md](README.md)
- **Roadmap:** [docs/roadmap.md](docs/roadmap.md)

---

**Last Updated by:** @gosxcli-orchestrator (2026-05-29)
