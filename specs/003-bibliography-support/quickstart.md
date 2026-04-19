# Quickstart: Bibliography Support

**Feature**: Bibliography Support (v0.3)
**Date**: 2026-04-19

This guide provides integration scenarios for the Bibliography feature.

---

## Scenario 1: Basic Citation (Numeric Style)

### Files

**`thesis.typ`**:
```typst
#import "@preview/modern-g7-32:0.1.0": template

#show template.with(
  title: "Заголовок",
  author: "Автор",
)

= Введение

Исследования показывают [@[smith2020]], что...

= Заключение

#bibliography("refs.bib")
```

**`refs.bib`**:
```bibtex
@article{smith2020,
  author = {Smith, John},
  title = {Research Methods},
  journal = {Journal of Science},
  year = {2020},
}
```

### Expected Output

DOCX with:
- Inline [1] at citation point
- "Список литературы" section at end
- Entry format: `1. Smith J. Research Methods // Journal of Science. — 2020.`

---

## Scenario 2: Multiple Citations

### Files

**`multi.typ`**:
```typst
= Обзор литературы

В работе [@[jones2019]] показано... 
Далее [@[brown2021]] и [@[jones2019]] подтверждают...

#bibliography("references.bib")
```

### Expected Output

- Inline markers: [1], [2], [1] (jones repeated)
- Bibliography: 2 entries (jones=1, brown=2)

---

## Scenario 3: Author-Year Style

### CLI Command

```bash
typst-gost-docx convert thesis.typ -o thesis.docx --bibliography-style author-year
```

### Expected Output

- Inline: (Smith, 2020) instead of [1]
- Bibliography: Sorted by author, year in parentheses

---

## Scenario 4: Missing Key Handling

### Files

**`broken.typ`**:
```typst
В работе [@[unknown2020]] показано...

#bibliography("refs.bib")
```

### Expected Behavior

- Warning logged: "Citation 'unknown2020' not found in bibliography"
- DOCX generated with placeholder: [unknown]
- Bibliography section contains only found entries

---

## Scenario 5: Different Entry Types

### Files

**`mixed.bib`**:
```bibtex
@article{art1,
  author = {Петров А.},
  title = {Статья},
  journal = {Журнал},
  year = {2023},
}

@book{book1,
  author = {Сидоров Б.},
  title = {Книга},
  publisher = {Москва: Наука},
  year = {2022},
}

@inproceedings{conf1,
  author = {Иванов В.},
  title = {Материалы конференции},
  booktitle = {Труды конференции},
  year = {2021},
}
```

### Expected Output (ГОСТ format)

```
1. Петров А. Статья // Журнал. — 2023.
2. Сидоров Б. Книга. — Москва: Наука, 2022.
3. Иванов В. Материалы конференции // Труды конференции. — 2021.
```

---

## Common Issues

### Issue: Cyrillic not rendering

**Cause**: BibTeX file not UTF-8 encoded

**Solution**: Ensure .bib file is saved as UTF-8

### Issue: Missing bibliography section

**Cause**: `#bibliography()` not at end of document

**Solution**: Place `#bibliography("file.bib")` at document end before closing

---

## Configuration Reference

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--bibliography-style` | numeric, author-year | numeric | Citation format |
| Bibliography file | .bib path | Required | Path to BibTeX file |

No config file changes required - CLI flags sufficient for MVP.