# Architecture

## Overview

The converter follows a 4-layer pipeline architecture:

```
Input: .typ file
   ↓
[1] Ingest Layer
   ↓
[2] Parser Layer
   ↓
[3] IR Layer
   ↓
[4] Writer Layer
   ↓
Output: .docx file
```

## Layer 1: Ingest

**Purpose**: Load and prepare Typst project files.

**Components**:
- `TypstProjectLoader`: Main entry point for loading files
- Handles `include` and `import` statements
- Tracks asset locations

**Output**: Dictionary of file paths to content.

## Layer 2: Parser

**Purpose**: Extract semantic structure from Typst syntax.

**Components**:
- `TypstScanner`: Token-level scanning
- `TypstExtractor`: Build IR from tokens
- `LabelExtractor`: Extract labels and refs
- `RefResolver`: Resolve cross-references

**Output**: IR document with typed nodes.

**Supported Typst patterns**:
- Headings: `=`, `==`, `===`
- Lists: `-`, `1.`
- Figures: `#figure(...)`
- Tables: `#table(...)`
- Math: `$`, `$$`
- Labels: `<label>`
- Refs: `@label`

## Layer 3: IR (Intermediate Representation)

**Purpose**: Typed, extensible document model.

**Core entities**:
- `Document`: Root node
- `Block nodes`: Section, Paragraph, ListBlock, Table, Figure, Equation
- `Inline nodes`: TextRun, Emphasis, Strong, InlineCode
- `Meta nodes`: Bookmark, CrossReference, Caption

**Design decisions**:
- Dataclasses over Pydantic for MVP simplicity
- Stable IDs for all nodes
- Optional source locations
- Explicit typing via NodeType enum

## Layer 4: Writer

**Purpose**: Generate DOCX from IR.

**Components**:
- `DocxWriter`: Main orchestrator
- `BookmarksManager`: Word bookmarks
- `StylesManager`: Style application
- `ImagesManager`: Image insertion
- `TablesManager`: Table creation

**Style mapping**:
- Heading 1/2/3 → Word styles
- Normal → Word Normal
- Caption → Word Caption
- Custom styles via `--reference-doc`

## Math Handling

**Fallback strategy** (MVP):
1. Parse LaTeX from Typst math
2. If unsupported → Log warning, insert placeholder
3. Future: `latex2mathml` for native rendering

## Cross-References

**Implementation**:
1. Labels → Word bookmarks
2. Refs → Word hyperlinks to bookmarks
3. Counter tracking per type (figure/table/equation)

## Error Handling

**Unsupported features**:
- Log as warning
- Insert placeholder or skip
- Continue conversion
- Report in summary

**Strict mode**:
- Fail on warnings
- Better for CI/CD

## Data Flow

```
typst file → text content
              ↓
           tokens
              ↓
           IR nodes
              ↓
        DOCX XML
              ↓
         .docx file
```

## Extensibility

**Adding new Typst patterns**:
1. Extend `TypstScanner` with new regex
2. Handle in `TypstExtractor`
3. Add IR node type if needed
4. Map in `DocxWriter`

**Adding new writers**:
- Implement `write()` for IR node types
- Use `python-docx` where possible
- Direct OpenXML for complex cases

## MVP Limitations

**Not supported**:
- Complex table layouts
- Nested lists
- Page breaks
- Bibliography
- Custom page layouts
- Typst functions beyond basic calls

**Reason**: Focus on core academic document features first.

## Future Directions

See `roadmap.md` for planned enhancements.
