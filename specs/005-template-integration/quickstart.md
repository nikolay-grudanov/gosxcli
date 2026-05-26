# Quickstart: GOST Template Integration

**Feature**: 005-template-integration | **Date**: 2026-05-24

## Для разработчика: что менять

### Изменения в кодовой базе

#### 1. Создать `src/typst_gost_docx/templates/` и переместить шаблон

```bash
mkdir -p src/typst_gost_docx/templates
cp template/Шаблон_оформления_ВКР_2026_новый.docx src/typst_gost_docx/templates/
touch src/typst_gost_docx/templates/__init__.py  # Необязательно, но для pkgutil
```

#### 2. Обновить `pyproject.toml`

```toml
[tool.setuptools.package-data]
typst_gost_docx = ["templates/*.docx"]
```

#### 3. Переписать `writers/styles.py`

Заменить заглушку `StylesManager` на:
- `StyleResolver` — разрешение стилей с итеративным fallback
- `TemplateLoader` — загрузка встроенного шаблона
- `IR_STYLE_MAP` — константа маппинга
- `UNNUMBERED_KEYWORDS` — константа ключевых слов

#### 4. Обновить `writers/docx_writer.py`

- Удалить метод `_configure_styles()`
- В `write()`: использовать `load_document(reference_doc)` вместо `Document(reference_doc)` / `Document()`
- Инициализировать `StyleResolver` после создания Document
- Заменить все обращения к стилям на `self._style_resolver.resolve(ir_type)`
- Заменить `paragraph.style = 'Heading 1'` на `self._style_resolver.apply_paragraph_style(paragraph, style_name)`
- Добавить `_is_unnumbered_heading()` для определения ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ и т.д.
- Обновить `_write_caption()` для использования `Подпись рисунков` / `Таблица название`

#### 5. Обновить `cli.py`

- Добавить fallback: если `--reference-doc` не указан, использовать встроенный шаблон
- Вывести информацию о используемом шаблоне в debug output

### Порядок реализации

```
Phase 1: Инфраструктура (templates/ + pyproject.toml + TemplateLoader)
    ↓
Phase 2: StyleResolver (writers/styles.py rewrite)
    ↓
Phase 3: DocxWriter integration (remove _configure_styles, use StyleResolver)
    ↓
Phase 4: Тесты (unit + integration)
    ↓
Phase 5: CLI update + verification
```

### Тестирование

```bash
# После каждого Phase:
ruff check src/ && ruff format src/ && mypy --strict src/

# После Phase 4:
pytest tests/ -v

# После Phase 5 (E2E):
typst-gost-docx convert test.typ -o test.docx --debug
# Проверить что стили из шаблона применены
```

### Ключевые проверки после реализации

1. **Heading стили**: Заголовки 1-3 уровня используют стили из шаблона (чёрные, Times New Roman)
2. **Unnumbered**: ВВЕДЕНИЕ/ЗАКЛЮЧЕНИЕ используют `Заг_не_содержание` (без нумерации)
3. **Captions**: Подписи рисунков → `Подпись рисунков`, таблиц → `Таблица название`
4. **Fallback**: Без шаблона → Document() + warnings в лог
5. **Custom template**: `--reference-doc custom.docx` использует пользовательский шаблон

## Для пользователя: как использовать

### С встроенным шаблоном (по умолчанию)

```bash
typst-gost-docx convert thesis.typ -o thesis.docx
```

Автоматически используется встроенный шаблон ГОСТ 7.32-2017.

### С пользовательским шаблоном

```bash
typst-gost-docx convert thesis.typ -o thesis.docx --reference-doc my-template.docx
```

### Без шаблона (plain DOCX)

```bash
typst-gost-docx convert thesis.typ -o thesis.docx --no-template
```

*(Опциональная фича — добавить если будет запрос)*
