# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-06-24

### 🎉 Enhanced Academic Support (spec 001 closed)

Closes spec 001 (T001-T124) — the v0.2-era roadmap for full academic document support. Most tasks were already shipped through the v0.4.x cross-reference, list, math, and template work; this release adds the missing piece and finalises the polish.

### ✨ New Features

- **Inline hyperlinks** (`#link("url")[label]`) rendered as real `<w:hyperlink r:id>` elements with `TargetMode="External"` relationships. URLs survive round-tripping through Microsoft Word.
- **Source-attributed validation**: `ReferenceValidator` now tracks source locations for every defined label, reference, and citation. The validation report prints `path:N: @label` instead of a bare `@label`.
- **Dedicated report generator** in `parser/refs.py::RefResolver.build_validation_report` that lifts resolver warnings back into structured `ValidationIssue` entries.
- **Validation summary statistics**: `get_validation_summary()` now includes `citation_keys_total/_defined/_missing` alongside the existing label/reference counts.
- **Benchmark history** via `benchmarks/compare.py` — reads `benchmarks/results/*.json`, groups by fixture, emits min/mean/max/stddev per fixture in either console or Markdown form.
- **`pytest-benchmark` integration**: conversion timings for `minimal`, `math_formulas`, `real_vkr` are now part of the test suite with per-fixture thresholds (1 s / 5 s / 10 s).

### 🐛 Bug Fixes

- Inline math `$E = mc^2$` is now extracted into a proper `InlineMathNode` (was previously emitted as plain text).
- Block equation latex no longer carries leading/trailing newlines that broke `latex2mathml`.
- `_extract_ref` now sets `source_location` on every `CrossReference`, so validation reports can pinpoint the offending source line.

### 🔧 Improvements

- CLI no longer duplicates `WARNING: Unresolved reference` logs — `ReferenceValidator` is now the single source of truth and logs each issue with its source location.
- `ValidationResult.format_report()` supports both the legacy `set[str]` API and the new rich `ValidationIssue` list, so callers upgrade at their own pace.

### 📊 Metrics

| Metric | Value |
|---|---|
| Lines of Code | ~6,800 |
| Source Files | 35 |
| Test Files | 33 |
| Test Cases | 310 (262 → 310, +48) |
| Regression fixtures | 3 (minimal, complex_table, equations) |
| Benchmark fixtures | 3 (with thresholds) |

## [0.4.0] - 2026-05-29

### 🎉 Syntax Highlighting

- Pygments-based syntax highlighting for code blocks
- VS Code Dark+ color scheme
- Support for Python, Rust, JavaScript, C, C++, Go
- Colored keywords, strings, comments, numbers, functions
- Dark background (#1E1E1E) for code blocks
- Monospace font (Courier New, 9pt)

### 🎉 GOST Template Integration (spec 005)

Интеграция референсного ГОСТ 7.32-2017 шаблона как встроенного шаблона по умолчанию и поддержка пользовательских шаблонов через `--reference-doc`.

### ✨ New Features

#### Встроенный ГОСТ-шаблон
- Бандл `templates/*.docx` (Шаблон_оформления_ВКР_2026_новый.docx) — Times New Roman 14pt, чёрные заголовки
- `pyproject.toml` включает `templates/*.docx` через `package-data`
- Шаблон доступен через `importlib.resources` без внешних файлов

#### StyleResolver с итеративным fallback
- Итеративный lookup по стилям + кэширование
- Fuzzy fallback для нестандартных `style_id` (Heading 1 → "781" в шаблоне ВКР)
- Обход `python-docx` BabelFish bug с нестандартными ID через monkeypatch `Styles.__getitem__`

#### Template fallback chain
- `load_document()`: `--reference-doc` (custom) → встроенный ГОСТ → `Document()` fallback
- `_configure_styles()` полностью удалён из `DocxWriter` (больше не нужен)
- `initialize_fallback_styles()` для случая fallback на `Document()`

#### Специальные стили шаблона
- `_is_unnumbered_heading()`: ВВЕДЕНИЕ / ЗАКЛЮЧЕНИЕ → стиль `Заг_не_содержание`
- Подписи рисунков → стиль `Подпись рисунков`
- Подписи таблиц → стиль `Таблица название`
- Формулы → стиль `Формулы`
- Таблицы → `Table Grid` из шаблона (с обработкой KeyError)

#### CLI: `--reference-doc`
- Пользовательский шаблон через CLI-флаг
- Template info (path + source) в `_print_summary()`

### 🔧 Verification

- ruff check: ✅ All checks passed
- mypy --strict: ✅ 0 errors in 32 files
- pytest: ✅ 262 passed
- E2E конвертация с шаблоном верифицирована

### 📊 Metrics

| Metric | Value |
|--------|-------|
| Lines of Code | ~5,800 |
| Source Files | 31 |
| Test Files | 29 |
| Test Cases | 262 |

## [0.3.1] - 2026-05-12

### 🐛 Bug Fixes

#### Parser
1. **OMML rendering** — MathML → OMML конвертер (`writers/mml2omml.py`)
2. **Label misattribution** — whitespace token skipping перед LABEL check
3. **Table not parsed** — автоматически исправлен фиксом label
4. **Ref colon support** — scanner поддерживает `@tbl:test`, `@eq:formula`

#### Style & Formatting
5. **Font Normal** — Times New Roman 14pt через `_configure_styles()` + XML rFonts
6. **Heading color** — чёрный вместо синего (`RGBColor(0,0,0)`)
7. **Heading font** — Times New Roman через XML rFonts для Heading 1-3
8. **Heading numbering** — иерархическая нумерация (1, 1.1, 1.1.1) через `heading_counters`
9. **Inline math** — `_write_text_with_inline_math()` для `$...$` внутри текста
10. **Cross-reference resolution** — `label_number_map` для номеров фигур/таблиц/формул
11. **Image path resolution** — `base_dir` в `ImagesManager`, резолвинг относительно `input_file.parent`
12. **Test image** — `fixtures/minimal/test.png` (200×100 PNG)

#### Real Thesis Fixes
13. **Image path resolution for chapters** — `_rewrite_image_paths()` в `project_loader.py`
14. **Bibliography citation recognition** — параметр `bib_keys` в `TypstExtractorV2` для отличия цитирований `@key` от cross-refs
15. **Missing styles fallback** — `_create_fallback_style()` в `StyleResolver` для динамического создания List Bullet / List Number / Heading N при отсутствии в шаблоне

## [0.3.0] - 2026-05-12

### ✨ Syntax Highlighting

- Pygments-based syntax highlighting for code blocks
- VS Code Dark+ color scheme
- Support for Python, Rust, JavaScript, C, C++, Go
- Colored keywords, strings, comments, numbers, functions
- Dark background (#1E1E1E) for code blocks
- Monospace font (Courier New, 9pt)

## [0.2.1] - 2026-05-12

### 🎉 Feature Complete - Code Blocks & Testing

This release adds code blocks support, E2E testing, benchmarks, and critical bug fixes.

### ✨ New Features

#### Code Blocks Support
- Multi-line code blocks with language specification (```python, ```rust, etc.)
- Monospace font (Courier New) for code display
- Background shading (light gray #F0F0F0) for visual distinction
- XML special character escaping (<, >, &)
- Preserved indentation and line breaks
- Small font size (9pt) for code blocks
- CodeBlockNode IR model with content, language, and source location

#### E2E Structure Tests
- DOCX structure validation (headings, paragraphs, tables, figures)
- Schema validation for document integrity
- Test fixtures with real documents for E2E testing
- Test helpers for extracting document elements

#### Regression Testing Framework
- Golden file comparison for output validation
- Snapshot testing for IR documents
- Test isolation with proper fixture management

#### Performance Benchmarking
- pytest-benchmark integration
- Benchmark fixtures for conversion speed
- Performance regression detection

### 📝 Documentation

- Added Code Blocks section to README.md
- Documented supported languages (Python, Rust, JavaScript, C, C++, plain text)
- Added code examples for code blocks
- Updated state.md with Code Blocks Support

### 🐛 Bug Fixes

- Fixed mypy --strict violations in:
  - `parsers/extractor_v2.py`: missing return types
  - `ir/model.py`: pydantic model issues
  - `utils/paths.py`: type annotations
- Fixed architecture boundary violation in labels.py (imported Document from writers)
- Fixed bibliography entry validation errors
- Fixed table cell content alignment issues
- Fixed reference resolution for nested structures
- Fixed math fallback rendering for complex formulas
- Fixed bibliography key parsing for special characters

### 🔧 Maintenance

- All tests passing (175 existing + 22 code blocks tests)
- 0 Ruff errors
- Mypy --strict compliance verified
- Comprehensive inline comments added
- Type hints verified for all public functions

### 📊 Metrics

| Metric | Value |
|--------|-------|
| Lines of Code | ~4,750 |
| Test Files | 19 |
| Test Cases | 197 |
| Ruff Errors | 0 |

## [0.2.0] - 2026-04-20

### 🎉 Feature Complete - Release Ready

This release brings comprehensive academic document support with improved math rendering, complex tables, and enhanced reference handling.

### ✨ New Features

#### Enhanced Math Rendering
- LaTeX to OMML (Office Math Markup Language) conversion via `latex2mathml`
- Native and fallback rendering modes
- Greek letters support (α, β, γ, Ω, etc.)
- Complex formulas support with proper fraction rendering

#### Table Attributes Support
- Column width specification (fr units or points)
- Cell colspan: `table.cell(colspan: 2, [spanned content])`
- Cell rowspan: `table.cell(rowspan: 2, [spanned content])`
- Cell alignment per column or per cell
- Cell fill/background color
- Table stroke/border configuration
- Nested tables (tables inside figures or cells)

#### Chapter-Aware References
- Automatic chapter number tracking
- Figure, table, and equation references include chapter prefix
- Format: "Fig. 1.2" (Chapter 1, Figure 2)
- Cross-references update automatically with document structure changes

#### Inline Formatting
- Emphasis: `*italic text*` or `_italic text_`
- Strong: `**bold text**` or `__bold text__`
- Combined: `***bold italic***`
- Preserved in DOCX with proper formatting

#### Table of Contents
- `#outline()` parsing and DOCX TOC generation
- Placeholder generation for manual field update in Word

#### Multi-file Projects
- Recursive file loading with `#include` support
- Depth protection (max 10 levels)
- Relative path resolution
- Cycle detection
- Debug logging for include tracking

#### Bidirectional Validation
- Reference validation (undefined references detection)
- Label usage tracking (unused labels warning)
- Citation key validation (missing bibliography entries detection)
- Strict mode: fail on validation errors
- Detailed validation reporting with file and line information

#### Bibliography Support
- BibTeX file support (.bib files) with custom parser
- Inline citations with @[key] syntax
- Two citation styles: numeric ([1], [2]) and author-year (Smith, 2023)
- Bibliography section formatting per ГОСТ 7.32-2017
- Alphabetical sorting for author-year style
- Placeholder text for incomplete entries ([Без автора], [Без названия])
- Citation key validation with warnings for missing entries

#### CLI Flags
- `--math-mode [native|fallback]`: Math rendering mode
- `--strict`: Enable strict validation mode
- `--benchmark`: Run performance benchmark
- `--debug`: Enable debug mode with file tree logging
- `--bibliography PATH`: Path to BibTeX bibliography file
- `--bibliography-style [numeric|author-year]`: Citation style for bibliography (default: numeric)

#### Performance & Testing
- Performance benchmarking with pytest-benchmark
- Regression testing framework with golden file comparison
- E2E structure tests for DOCX validation
- v0.1 compatibility smoke tests

### 🛠️ Improvements

- Migrated Token from dataclass to Pydantic v2
- New parser architecture: TypstQueryParser + RegexFallbackParser + UnifiedParser
- Enhanced label parsing (supports labels with colons and hyphens)
- Improved error handling for edge cases
- Added inline comments to complex code sections (tables.py, math_renderer.py, bibliography.py, docx_writer.py)
- Bibliography parser with LaTeX command stripping and special character handling
- Citation key validation integrated into ReferenceValidator
- Placeholder text for incomplete bibliography entries

### 📝 Documentation

- Updated README.md with v0.2 features
- Documented all CLI flags
- Added code examples for new features
- Updated roadmap (v0.2 complete, v0.3 planned)

### 🔧 Maintenance

- 135 tests passing (0 failures)
- 0 Ruff errors
- Mypy --strict for critical modules
- Code quality: inline comments, type hints, Google Style docstrings

### 📊 Metrics

| Metric | Value |
|--------|-------|
| Lines of Code | ~4,450 |
| Test Files | 17 |
| Test Cases | 135 |
| Performance (minimal) | ~13ms |
| Performance (math) | ~18ms |
| Performance (real_vkr) | ~20ms |

## [0.1.0] - 2026-04-17

### 🎉 Initial MVP Release

Basic Typst to DOCX conversion with GOST styling support.

### Features

- Headings (1-3 levels)
- Paragraphs with basic formatting
- Bullet and numbered lists
- Basic tables
- Figures with captions
- Labels and cross-references (@label)
- Basic math (inline and block)
- Custom DOCX templates
- IR dump for debugging

---

**Note**: Full GOST 7.32-2017 compliance is planned for v0.3.