# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-04-19

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
- Strict mode: fail on validation errors
- Detailed validation reporting with file and line information

#### CLI Flags
- `--math-mode [native|fallback]`: Math rendering mode
- `--strict`: Enable strict validation mode
- `--benchmark`: Run performance benchmark
- `--debug`: Enable debug mode with file tree logging

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
- Added inline comments to complex code sections (tables.py, math_renderer.py)

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