# Roadmap

## Version 0.1 (Current)

**Status**: MVP - Core features working

**Features**:
- ✅ Basic CLI interface
- ✅ Headings (1-3 levels)
- ✅ Paragraphs
- ✅ Bullet and numbered lists
- ✅ Basic figures with captions
- ✅ Basic tables
- ✅ Labels and cross-references
- ✅ Math fallback (placeholder)
- ✅ Custom reference templates
- ✅ IR dump for debugging
- ✅ Basic test suite

**Known limitations**:
- Math is placeholder only
- Tables are simplistic
- No nested structures
- Limited Typst syntax support

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

## Timeline Estimate

- v0.2: 4-6 weeks
- v0.3: 6-8 weeks
- v0.4: 8-12 weeks

**Note**: Timeline depends on community contribution and priority shifts.
