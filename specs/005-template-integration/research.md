# Research: GOST Template Integration

**Feature**: 005-template-integration | **Date**: 2026-05-24

## Research Items

### R-001: python-docx reference_doc loading and style inheritance

**Decision**: Использовать `Document(reference_doc_path)` для загрузки шаблона

**Rationale**:
- python-docx поддерживает загрузку из шаблона: `Document(path)` загружает все стили, настройки страницы, колонтитулы
- Стили из шаблона наследуются всеми параграфами, добавленными через `add_paragraph()`, `add_heading()` и т.д.
- Настройки страницы (margins, page size) также наследуются из шаблона

**Alternatives considered**:
- `Document()` с ручной настройкой `_configure_styles()` — текущий подход, не работает полностью для Heading стилей
- Копирование стилей из шаблона в новый документ — сложнее, не нужно при `Document(reference_doc)`

### R-002: Non-standard style_id in ВКР template — heading lookup failure

**Decision**: Создать StyleResolver с двухэтапным разрешением стилей:
1. Попытка `doc.styles[name]` (стандартный python-docx lookup)
2. При KeyError — итеративный поиск по `style.name == target_name`
3. Кэширование найденных style объектов для производительности

**Rationale**:
- Шаблон ВКР имеет нестандартные style_id ('781', '782', '783') для Heading 1-3
- python-docx `__getitem__` на `Styles` использует внутренний name→style_id маппинг, который не может найти стили с нестандартными ID
- Итеративный поиск работает: `style.name` корректно возвращает 'Heading 1', 'Heading 2', 'Heading 3'
- Применение стиля через `paragraph.style = style_object` работает корректно

**Alternatives considered**:
- Исправить style_id в шаблоне — возможно, но ломает другие документы, использующие шаблон
- XML-манипуляция для добавления правильного маппинга — хрупкий подход
- Не использовать шаблон — теряем все ГОСТ стили

### R-003: Template packaging with importlib.resources

**Decision**: Использовать `importlib.resources` (Python 3.12+) для доступа к шаблону внутри пакета

**Rationale**:
- `importlib.resources` — стандартный способ доступа к ресурсам пакета в Python 3.12+
- Работает после `pip install` (wheel/egg), не зависит от расположения исходников
- `importlib.resources.files('typst_gost_docx.templates') / 'Шаблон_оформления_ВКР_2026_новый.docx'` возвращает `Traversable` путь
- Для python-docx нужен `str()` или `Path` — конвертируем через `Path(traversable)`

**Implementation notes**:
```python
from importlib.resources import files

def get_default_template_path() -> Path:
    """Возвращает путь к встроенному шаблону ГОСТ."""
    resource = files('typst_gost_docx.templates') / 'Шаблон_оформления_ВКР_2026_новый.docx'
    return Path(str(resource))
```

**Alternatives considered**:
- `pkgutil.get_data()` — возвращает bytes, не подходит для `Document(path)`
- `__file__`-based paths — не работает после `pip install` (zip-safe packages)
- Встроить шаблон как base64 — неэффективно, усложняет код

### R-004: Style mapping dictionary design

**Decision**: Двухэтапный маппинг IR type → имена стилей:

1. **Жёстко заданный словарь** (primary mapping):
   ```python
   STYLE_MAP = {
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
   ```

2. **Fuzzy fallback** — поиск по частичному совпадению имени:
   - Нормализация имени (lowercase, strip)
   - Поиск подстроки в имени стиля шаблона
   - Пример: "подпись" → найдёт "Подпись рисунков"

3. **Final fallback** — стандартный Word-стиль + warning

**Rationale**:
- Жёсткий словарь обеспечивает детерминированное поведение для известных стилей
- Fuzzy fallback позволяет находить стили при локальных вариациях имён
- Warning обеспечивает видимость при fallback'ах

**Alternatives considered**:
- Только жёсткий словарь — негибко, ломается при малейших изменениях шаблона
- Только fuzzy — недетерминированно, может найти неверный стиль
- Конфигурационный файл — overkill для текущего масштаба

### R-005: Unnumbered heading detection

**Decision**: Фиксированный список ключевых слов (из clarifications spec)

```python
UNNUMBERED_KEYWORDS = frozenset({
    # Русские
    "РЕФЕРАТ", "ВВЕДЕНИЕ", "ЗАКЛЮЧЕНИЕ", "СПИСОК ЛИТЕРАТУРЫ",
    # Английские
    "ABSTRACT", "INTRODUCTION", "CONCLUSION", "BIBLIOGRAPHY", "REFERENCES",
})
```

**Rationale**: Простой, предсказуемый, легко расширяющийся. Определяется при парсинге заголовка в writer.

### R-006: pyproject.toml configuration for template inclusion

**Decision**: Использовать `[tool.setuptools.package-data]` для включения .docx файлов

```toml
[tool.setuptools.package-data]
typst_gost_docx = ["templates/*.docx"]
```

**Rationale**: setuptools по умолчанию включает только .py файлы. Нужна явная конфигурация для включения .docx.

### R-007: Caption style resolution

**Decision**: Для подписей использовать приоритетный список:
- Рисунки: `["Подпись рисунков", "Caption"]` (русский шаблон → встроенный fallback)
- Таблицы: `["Таблица название"]` (кастомный стиль из шаблона)
- Формулы: `["Формулы"]` (кастомный стиль из шаблона)

**Rationale**: Шаблон ВКР содержит русские кастомные стили для подписей. Встроенный `Caption` — fallback если кастомный стиль отсутствует.

## Summary of Decisions

| ID | Decision | Key Trade-off |
|----|----------|---------------|
| R-001 | `Document(reference_doc)` для загрузки шаблона | Простота vs гибкость |
| R-002 | StyleResolver с итеративным fallback | Работает с нестандартными style_id |
| R-003 | `importlib.resources` для доступа к шаблону | Кросс-платформенность после install |
| R-004 | Жёсткий словарь + fuzzy fallback | Детерминированность + гибкость |
| R-005 | Фиксированные ключевые слова | Простота, расширяемость |
| R-006 | `package-data` в pyproject.toml | Включение .docx в wheel |
| R-007 | Приоритетный список для Caption | Русский стиль → fallback |
