# Typst GOST DOCX Converter

Typst to DOCX converter for academic documents with GOST styling support.

## Status: v0.2.0 (Feature Complete)

Production-ready tool for converting Typst academic documents (especially those using `@preview/modern-g7-32`) to editable DOCX files while preserving structure, references, tables, images, and applying GOST-compliant styling.

## Features

- ✅ Headings (1-3 levels)
- ✅ Paragraphs with inline formatting (emphasis, strong)
- ✅ Bullet and numbered lists
- ✅ Tables with colspan, rowspan, stroke, fill, alignment
- ✅ Nested tables support
- ✅ Figures with captions
- ✅ Labels and chapter-aware cross-references
- ✅ Enhanced math rendering (latex2mathml to OMML)
- ✅ Table of Contents generation
- ✅ Multi-file project support (#include)
- ✅ Custom DOCX templates
- ✅ Bidirectional reference validation
- ✅ IR dump for debugging

## Installation

```bash
pip install -e .
```

Or with dev dependencies:

```bash
make install-dev
```

## Quick Start

```bash
# Basic conversion
typst-gost-docx convert thesis.typ -o thesis.docx

# With custom reference template
typst-gost-docx convert thesis.typ -o thesis.docx --reference-doc ./templates/gost-reference.docx

# Debug mode with IR dump
typst-gost-docx convert thesis.typ -o thesis.docx --dump-ir --debug

# Strict mode for validation
typst-gost-docx convert thesis.typ -o thesis.docx --strict

# Native math rendering
typst-gost-docx convert thesis.typ -o thesis.docx --math-mode native

# Performance benchmark
typst-gost-docx convert thesis.typ -o thesis.docx --benchmark

# With custom assets directory
typst-gost-docx convert thesis.typ -o thesis.docx --assets-dir ./assets
```

## Supported Typst Features (v0.2)

### Structure
- `= Heading 1`
- `== Heading 2`
- `=== Heading 3`
- Paragraphs
- Bullet lists (`- item`)
- Numbered lists (`1. item`)

### Figures
```typst
#figure(
  image("diagram.png"),
  caption: [Diagram of the system],
)
```

### Tables
```typst
#table(
  columns: (1fr, 2fr),
  stroke: 1pt,
  fill: (x, y) => if x == 0 { "DDDDDD" },
  align: (x, y) => if x == 0 { center } else { left },
  table.header([Column 1][Column 2]),
  [Cell 1][Cell 2],
)
```

**Advanced features:**
- Column width specification (fr units or points)
- Cell colspan: `table.cell(colspan: 2, [spanned content])`
- Cell rowspan: `table.cell(rowspan: 2, [spanned content])`
- Cell alignment per column or per cell
- Cell fill/background color
- Nested tables (tables inside figures or cells)

### Labels and References
```typst
#figure(
  image("plot.png"),
  caption: [Experimental results],
) <fig:results>

As shown in @fig:results, the results are promising.
```

**Chapter-aware references:**
- Automatic chapter number tracking
- Figure, table, and equation references include chapter: "Fig. 1.2" (Chapter 1, Figure 2)
- Cross-references update automatically when document structure changes

### Math
- Inline math: `$E = mc^2$`
- Block math: `$$ x = \frac{-b \pm \sqrt{b^2-4ac}}{2a} $$`
- Complex formulas: `$$ \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi} $$`
- Greek letters: `$\alpha, \beta, \gamma, \Omega$`

**Enhanced rendering:**
- LaTeX to OMML (Office Math Markup Language) conversion
- Native rendering with latex2mathml
- Fallback mode for unsupported constructs
- Math mode selection via CLI flag (--math-mode)

### Inline Formatting
- Emphasis: `*italic text*` or `_italic text_`
- Strong: `**bold text**` or `__bold text__`
- Combined: `***bold italic***`
- Preserved in DOCX with proper formatting

### Multi-file Projects
```typst
// main.typ
#include "chapter1.typ"
#include "chapter2.typ"

// chapter1.typ
= Chapter 1

Content...
```

**Features:**
- Recursive file loading with depth protection (max 10 levels)
- Relative path resolution
- Cycle detection
- Debug logging for include tracking
## Architecture

The converter uses a 4-layer pipeline:

1. **Ingest**: Loads Typst project files
2. **Parser**: Extracts document structure into IR
3. **IR**: Intermediate representation with typed nodes
4. **Writer**: Generates DOCX from IR

See `docs/architecture.md` for details.

## CLI Options

```
Usage: typst-gost-docx convert [OPTIONS] INPUT_FILE

Arguments:
  INPUT_FILE  Input .typ file

Options:
  -o, --output PATH              Output .docx file
  --reference-doc PATH           Reference DOCX template
  --assets-dir PATH              Assets directory
  --debug                        Enable debug mode
  --dump-ir                      Dump IR to JSON
  --dump-json                    Dump document JSON
  --strict                       Strict mode (fail on validation errors)
  --math-mode [native|fallback]  Math rendering mode (default: fallback)
  --benchmark                    Run performance benchmark
  --log-level TEXT               Log level
  --help                         Show help message
```

### CLI Flags Details

**--math-mode [native|fallback]**
- `native`: Convert all LaTeX to OMML, fail on errors (use for production)
- `fallback`: Convert LaTeX to OMML, use text placeholder on errors (default)
- Example: `typst-gost-docx convert thesis.typ -o thesis.docx --math-mode native`

**--strict**
- Enable strict validation mode
- Fail conversion if undefined references or broken labels detected
- Useful for production builds to ensure document quality
- Example: `typst-gost-docx convert thesis.typ -o thesis.docx --strict`

**--benchmark**
- Run performance benchmark and display timing information
- Shows Load, Parse, Write, and Total time
- Saves benchmark results to `benchmarks/results/<timestamp>_cli_benchmark.json`
- Example: `typst-gost-docx convert thesis.typ -o thesis.docx --benchmark`

## Project Structure

```
src/typst_gost_docx/
├── cli.py              # CLI interface
├── config.py           # Configuration
├── logging.py          # Logging setup
├── ingest/
│   └── project_loader.py
├── parser/
│   ├── scanner.py      # Typst token scanner
│   ├── extractor.py    # IR extractor
│   ├── labels.py       # Label extraction
│   └── refs.py         # Reference resolution
├── ir/
│   └── model.py        # IR data models
├── writers/
│   ├── docx_writer.py  # Main DOCX writer
│   ├── bookmarks.py    # Bookmark management
│   ├── styles.py       # Style application
│   ├── images.py       # Image handling
│   └── tables.py       # Table generation
└── utils/
    ├── paths.py        # Path utilities
    └── xml.py          # OpenXML utilities
```

## Development

### Run tests
```bash
make test
```

### Lint
```bash
make lint
```

### Format code
```bash
make format
```

## Roadmap

See `docs/roadmap.md` for future plans.

### v0.2 (Completed ✅)
- ✅ Enhanced math rendering with latex2mathml
- ✅ Complex table support (colspan, rowspan, stroke, fill, align)
- ✅ Better reference resolution (chapter-aware)
- ✅ Chapter-aware numbering
- ✅ Inline emphasis and strong formatting
- ✅ Table of Contents generation
- ✅ Multi-file project support
- ✅ Bidirectional reference validation
- ✅ Performance benchmarking
- ✅ Nested tables support

### v0.3 (Planned)
- Code blocks with syntax highlighting
- Bibliography support
- Page breaks and section formatting
- More robust error handling
- Full GOST 7.32-2017 compliance

## Limitations

- Does not support full Typst language (v0.2 scope only)
- Not pixel-perfect layout (editable DOCX focus)
- Very complex math formulas may need manual adjustment
- No support for all Typst packages
- Table of Contents generated as placeholder (manual field update in Word recommended)
- Maximum include depth: 10 levels (configurable in code)

## Contributing

Contributions welcome! Please read the architecture docs first.

## License

MIT License - see LICENSE file.
