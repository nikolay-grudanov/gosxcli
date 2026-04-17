# Typst GOST DOCX Converter

Typst to DOCX converter for academic documents with GOST styling support.

## Status: MVP v0.1

This is an MVP tool for converting Typst academic documents (especially those using `@preview/modern-g7-32`) to editable DOCX files while preserving structure, references, tables, images, and applying GOST-compliant styling.

## Features

- ✅ Headings (1-3 levels)
- ✅ Paragraphs
- ✅ Bullet and numbered lists
- ✅ Tables (basic support)
- ✅ Figures with captions
- ✅ Labels and cross-references
- ✅ Custom DOCX templates
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

# With custom assets directory
typst-gost-docx convert thesis.typ -o thesis.docx --assets-dir ./assets
```

## Supported Typst Features (v0.1)

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
  columns: 2,
  table.header([Column 1][Column 2]),
  [Cell 1][Cell 2],
)
```

### Labels and References
```typst
#figure(
  image("plot.png"),
  caption: [Experimental results],
) <fig:results>

As shown in @fig:results, the results are promising.
```

### Math
- Inline math: `$E = mc^2$`
- Block math: `$$ x = \frac{-b \pm \sqrt{b^2-4ac}}{2a} $$`

Note: Math support is MVP - complex formulas may render as placeholders with warnings.

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
  --strict                       Strict mode (fail on warnings)
  --math-mode [native|fallback]  Math rendering mode
  --log-level TEXT               Log level
  --help                         Show help message
```

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

### v0.2 (Planned)
- Enhanced math rendering with latex2mathml
- Complex table support (colspan, rowspan)
- Better reference resolution
- Chapter-aware numbering
- Inline emphasis and strong formatting

### v0.3 (Planned)
- Code blocks with syntax highlighting
- Bibliography support
- Page breaks and section formatting
- More robust error handling

## Limitations

- Does not support full Typst language (MVP scope only)
- Not pixel-perfect layout (editable DOCX focus)
- Complex math may need manual adjustment
- No support for all Typst packages

## Contributing

Contributions welcome! Please read the architecture docs first.

## License

MIT License - see LICENSE file.
