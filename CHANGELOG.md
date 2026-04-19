# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-04-20

### 🎉 Code Blocks Support MVP

This release adds basic code blocks support with monospace font, XML escaping, and background shading.

### ✨ New Features

#### Code Blocks Support
- Multi-line code blocks with language specification (```python, ```rust, etc.)
- Monospace font (Courier New) for code display
- Background shading (light gray #F0F0F0) for visual distinction
- XML special character escaping (<, >, &)
- Preserved indentation and line breaks
- Small font size (9pt) for code blocks
- CodeBlockNode IR model with content, language, and source location
- Unit tests (14 tests) for CodeBlockNode model and extraction
- Integration tests (8 tests) for code block rendering

### 📝 Documentation

- Added Code Blocks section to README.md
- Documented supported languages (Python, Rust, JavaScript, C, C++, plain text)
- Added code examples for code blocks
- Updated state.md with Code Blocks Support (Phase 5 completed)

### 🔧 Maintenance

- All 197 tests passing (175 existing + 22 code blocks tests)
- 0 Ruff errors
- Mypy --strict for new code blocks code (extractor_v2.py)
- Comprehensive inline comments in _write_code_block() and _extract_code_block()

### 📊 Metrics

| Metric | Value |
|--------|-------|
| Lines of Code | ~4,750 (+280 code blocks) |
| Test Files | 19 (added test_code_blocks.py) |
| Test Cases | 197 (+22 code blocks tests) |

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