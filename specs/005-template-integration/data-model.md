# Data Model: GOST Template Integration

**Feature**: 005-template-integration | **Date**: 2026-05-24

## Entities

### 1. StyleResolver

**Purpose**: Разрешение имён стилей из шаблона DOCX с учётом нестандартных style_id

**Location**: `src/typst_gost_docx/writers/styles.py`

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `_doc` | `Optional[_Document]` | Ссылка на Document для style lookup |
| `_style_cache` | `dict[str, Optional[str]]` | Кэш: style_name → style_id (None = not found) |
| `_template_styles` | `dict[str, str]` | Маппинг: normalized_name → style_id для fuzzy matching |

**Methods**:
| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(doc: Optional[_Document])` | Инициализация с Document |
| `resolve_style` | `(name: str) -> Optional[str]` | Найти стиль по имени, вернуть style_id |
| `apply_style` | `(paragraph: DocxParagraph, name: str) -> bool` | Применить стиль к параграфу |
| `get_style` | `(name: str) -> Optional[Style]` | Получить объект стиля |
| `_resolve_by_direct_lookup` | `(name: str) -> Optional[str]` | Стандартный python-docx lookup |
| `_resolve_by_iteration` | `(name: str) -> Optional[str]` | Итеративный поиск (fallback) |
| `_resolve_by_fuzzy` | `(name: str) -> Optional[str]` | Fuzzy matching по подстроке |

**State transitions**: Нет (stateless resolver с кэшем)

### 2. StyleMapping (constants)

**Purpose**: Маппинг типов IR-элементов на имена стилей

**Location**: `src/typst_gost_docx/writers/styles.py`

**Structure**:
```python
# IR element type → список возможных имён стилей (по приоритету)
IR_STYLE_MAP: dict[str, list[str]] = {
    "heading_1": ["Heading 1"],
    "heading_2": ["Heading 2"],
    "heading_3": ["Heading 3"],
    "heading_unnumbered": ["Заг_не_содержание"],
    "title": ["Титул"],
    "caption_figure": ["Подпись рисунков", "Caption"],
    "caption_table": ["Таблица название"],
    "equation": ["Формулы"],
    "normal": ["Normal"],
    "table_grid": ["Table Grid"],
}

# Ключевые слова для определения ненумерованных заголовков
UNNUMBERED_KEYWORDS: frozenset[str] = frozenset({
    "РЕФЕРАТ", "ВВЕДЕНИЕ", "ЗАКЛЮЧЕНИЕ", "СПИСОК ЛИТЕРАТУРЫ",
    "ABSTRACT", "INTRODUCTION", "CONCLUSION", "BIBLIOGRAPHY", "REFERENCES",
})
```

### 3. TemplateLoader

**Purpose**: Загрузка встроенного шаблона ГОСТ

**Location**: `src/typst_gost_docx/writers/styles.py` (или отдельный модуль)

**Methods**:
| Method | Signature | Description |
|--------|-----------|-------------|
| `get_default_template_path` | `() -> Optional[Path]` | Получить путь к встроенному шаблону |
| `load_template` | `(path: Optional[Path] = None) -> _Document` | Загрузить Document из шаблона или fallback |

**Behaviour**:
1. Если `path` указан и существует → `Document(path)`
2. Иначе → попробовать встроенный шаблон через `importlib.resources`
3. Если встроенный шаблон недоступен → `Document()` + warning
4. Возвращает `_Document` (python-docx Document)

### 4. DocxWriter (modified)

**Changes**:
- `_configure_styles()` → **УДАЛИТЬ** (стили из шаблона)
- `__init__` → добавить `TemplateLoader`/`StyleResolver`
- `write()` → использовать `TemplateLoader.load_template()`
- `_write_section()` → использовать `StyleResolver` для стилей заголовков
- `_write_caption()` → использовать `StyleResolver` для подписей
- `_write_table()` → использовать `Table Grid` из шаблона
- `_get_heading_style()` → заменить на `StyleResolver.resolve_style()`
- Добавить `_is_unnumbered_heading()` для определения ненумерованных заголовков

## Relationships

```
DocxWriter
  ├── TemplateLoader (uses for Document creation)
  │   └── importlib.resources (access to embedded template)
  └── StyleResolver (uses for style resolution)
      ├── IR_STYLE_MAP (constants for mapping)
      ├── _doc reference (python-docx Styles)
      └── _style_cache (performance optimization)
```

## Validation Rules

1. **StyleResolver.resolve_style()** всегда возвращает Optional — None если стиль не найден
2. При None → warning в лог + fallback на стандартный стиль Word
3. TemplateLoader.load_template() никогда не бросает исключение — всегда возвращает Document (с warning при fallback)
4. Кэш StyleResolver инвалидируется при смене Document (новый шаблон)

## IR Impact

**Нет изменений в IR модели.** Это чисто Writer-side изменение. IR Contract (`ir/model.py`) не затрагивается.

IR_1_0 версия сохраняется.
