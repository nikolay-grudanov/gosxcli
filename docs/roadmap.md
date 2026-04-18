# Roadmap

## Version 0.1 (Current)

**Status**: MVP - Core features working

**Features**:
- ✅ Basic CLI interface
- ✅ Headings (1-3 levels)
- ✅ Paragraphs
- ✅ Bullet and numbered lists
- ✅ Basic figures with captions
- ✅ Basic tables with proper row/cell structure
- ✅ Labels and cross-references with inline @fig/@tbl/@eq parsing
- ✅ Math fallback (placeholder) with latex2mathml support
- ✅ Custom reference templates
- ✅ IR dump for debugging
- ✅ Basic test suite
- ✅ Real bookmarks in DOCX via OpenXML
- ✅ Hyperlinks to bookmarks
- ✅ State-machine based parser (replacing regex-based approach)
- ✅ Typst-py integration for document structure extraction
- ✅ Typst JSON to IR conversion

**Known limitations**:
- Math fallback when latex2mathml unavailable
- Tables are simplistic (no colspan/rowspan)
- Limited nested structure support
- Typst-py optional dependency
- Cross-reference resolution warnings

## Version 0.2

**Planned Features**:

### Enhanced Math
- Native math rendering via `latex2mathml`
- Support for:
  - Fractions
  - Sums and integrals
  - Matrices
  - Complex expressions
- Fallback to image for unsupported

### Better Tables
- `colspan` support
- `rowspan` support
- Nested tables
- Table caption positioning

### Improved References
- Chapter-aware numbering
- Reference text formatting ("Рис. 1.2")
- Auto-numbering updates
- Bidirectional ref validation

### Formatting
- Inline emphasis (`*text*`)
- Inline strong (`_text_`)
- Inline code (`\`code\``)
- Links

### Testing
- E2E test with real thesis sample
- Regression test suite
- Performance benchmarks

## Version 0.3

**Planned Features**:

### Advanced Content
- Code blocks with syntax highlighting
- Footnotes
- Bibliography
- TOC generation
- Page breaks

### Layout
- Page margins (from reference doc)
- Section breaks
- Multi-column layout (basic)

### Images
- SVG rasterization
- Image scaling
- Image positioning

### Quality
- Better error messages
- Configurable warnings
- Validation modes

## Version 0.4

**Planned Features**:

### Integration
- Watch mode (auto-rebuild on change)
- Batch conversion
- CI/CD friendly output

### Export Options
- PDF export (via Word)
- Different DOCX versions
- Custom style presets

### Performance
- Caching
- Parallel processing for large docs
- Incremental rebuilds

## Future Considerations

### Potential Extensions
- Other output formats (ODT, Markdown)
- Typst package ecosystem integration
- Web UI for visual debugging
- VS Code extension

### Language Support
- Better multi-language text handling
- Font management
- Character encoding issues

### Dependencies
- Evaluate `typst2ir` project if matures
- Consider Rust extension for parsing speed

## Contribution Priority

High priority areas for contributions:
1. Test coverage improvements
2. Bug fixes
3. Documentation
4. Math rendering improvements
5. Table layout enhancements

## Recent Fixes (2026-04-17 - 2026-04-18)

**Critical issues resolved**:
1. ✅ Fixed NodeType enum - added TABLE_ROW and TABLE_CELL
2. ✅ Implemented minimal table parser with row/cell extraction
3. ✅ Added inline @fig/@tbl/@eq reference parsing in paragraphs
4. ✅ Added _write_equation() with latex2mathml support and fallback
5. ✅ Added _write_cross_reference() with hyperlink to bookmarks
6. ✅ Fixed stats tracking for refs_resolved and refs_unresolved
7. ✅ Implemented real bookmarks via OpenXML (bookmarkStart/bookmarkEnd)
8. ✅ Added add_hyperlink_to_bookmark() method
9. ✅ Created comprehensive e2e test in test_smoke.py
10. ✅ Created minimal.typ fixture with all test cases

**Major architectural improvements (2026-04-17)**:
11. ✅ Created ingest/typst_client.py for Typst-py integration
12. ✅ Implemented TypstJsonToIRConverter for Typst JSON → IR conversion
13. ✅ Created extractor_v2.py with state-machine parser (replacing regex-based approach)
14. ✅ Fixed scanner.py BULLET pattern to avoid false matches in labels
15. ✅ Fixed BaseNode dataclass field ordering for Python 3.14 compatibility

**Critical scanner fixes (2026-04-18)**:
16. ✅ Fixed infinite loop in scanner - added fallback for unmatched characters
17. ✅ Fixed LABEL pattern to support dashes and underscores (<fig-test>)
18. ✅ Fixed line-start pattern matching - removed ^ anchor and added column check
19. ✅ Fixed NEWLINE pattern matching - position not advanced in "other patterns" loop
20. ✅ Fixed list extraction - now correctly groups consecutive list items into single ListBlock
21. ✅ All smoke tests now passing (7/7)

## Timeline Estimate

- v0.2: 4-6 weeks
- v0.3: 6-8 weeks
- v0.4: 8-12 weeks

**Note**: Timeline depends on community contribution and priority shifts.
