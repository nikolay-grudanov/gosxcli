# Contract: Style Resolution

**Feature**: 005-template-integration | **Date**: 2026-05-24

## Interface: StyleResolver

### Public API

```python
class StyleResolver:
    """Разрешение имён стилей из DOCX шаблона с учётом нестандартных style_id."""

    def __init__(self, doc: Optional[Document]) -> None: ...
    
    def resolve(self, ir_type: str) -> Optional[str]:
        """Разрешить IR-тип в имя стиля шаблона.
        
        Args:
            ir_type: Тип IR-элемента (например 'heading_1', 'caption_figure')
            
        Returns:
            Имя стиля из шаблона или None если стиль не найден.
            Всегда логирует warning при None.
        """
        ...
    
    def apply_paragraph_style(self, paragraph: DocxParagraph, style_name: str) -> bool:
        """Применить стиль к параграфу напрямую (обход style_id проблемы).
        
        Args:
            paragraph: Параграф python-docx
            style_name: Имя стиля для применения
            
        Returns:
            True если стиль применён, False если не найден.
        """
        ...
```

### Resolution Algorithm

```
resolve(ir_type: str) -> Optional[str]:
    1. Получить список кандидатов из IR_STYLE_MAP[ir_type]
    2. Для каждого кандидата:
       a. Проверить кэш (_style_cache)
       b. Если не в кэше → _lookup_style(candidate_name)
       c. Если найден → вернуть имя, обновить кэш
    3. Если ни один кандидат не найден → fuzzy matching
    4. Если fuzzy не нашёл → warning + return None
```

```
_lookup_style(name: str) -> Optional[Style]:
    1. Попытка doc.styles[name] (стандартный lookup)
    2. При KeyError → итеративный поиск: next((s for s in doc.styles if s.name == name), None)
    3. Кэшировать результат
```

### Error Handling

| Condition | Behaviour |
|-----------|-----------|
| Document is None | Все resolve() возвращают None + warning |
| Style not found by name | Fallback: итеративный поиск |
| Style not found by iteration | Fallback: fuzzy matching |
| Style not found at all | Warning в лог, return None |
| Template file missing | Document() fallback + warning |

### IR_TYPE Mapping Contract

| IR Type | Primary Style | Fallback Style | Context |
|---------|--------------|----------------|---------|
| `heading_1` | `Heading 1` | — | Заголовок уровня 1 |
| `heading_2` | `Heading 2` | — | Заголовок уровня 2 |
| `heading_3` | `Heading 3` | — | Заголовок уровня 3 |
| `heading_unnumbered` | `Заг_не_содержание` | `Heading 1` | ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ и т.д. |
| `title` | `Титул` | `Title` | Титульный элемент |
| `caption_figure` | `Подпись рисунков` | `Caption` | Подпись к рисунку |
| `caption_table` | `Таблица название` | `Caption` | Подпись к таблице |
| `equation` | `Формулы` | — | Формула |
| `normal` | `Normal` | — | Обычный текст |
| `table_grid` | `Table Grid` | — | Стиль таблицы |

### Unnumbered Heading Detection Contract

```python
def is_unnumbered_heading(text: str) -> bool:
    """Определить, является ли заголовок ненумерованным по ключевому слову."""
    return text.strip().upper() in UNNUMBERED_KEYWORDS
```

**UNNUMBERED_KEYWORDS**: `frozenset` ключевых слов (русские + английские)

### Invariants

1. StyleResolver **никогда не бросает исключения** — всегда возвращает Optional
2. Каждый miss логируется как warning через проектный logger
3. Кэш одноразовый — привязан к конкретному Document
4. Thread-unsafe (один resolver на одну конвертацию)

### Dependencies

- `docx.Document` — для доступа к стилям
- `docx.enum.style.WD_STYLE_TYPE` — для фильтрации типов стилей
- Проектный `logging.py` — для warnings

## Interface: TemplateLoader

### Public API

```python
def get_default_template_path() -> Optional[Path]:
    """Получить путь к встроенному шаблону ГОСТ.
    
    Returns:
        Path к шаблону или None если шаблон недоступен.
    """

def load_document(reference_doc: Optional[Path] = None) -> Document:
    """Загрузить Document из шаблона.
    
    Args:
        reference_doc: Путь к пользовательскому шаблону (приоритет)
        
    Returns:
        Document загруженный из шаблона.
        Fallback на Document() если шаблон недоступен.
    """
```

### Loading Priority

```
load_document(reference_doc):
    1. reference_doc указан и существует → Document(reference_doc)
    2. reference_doc указан но не существует → warning + шаг 3
    3. Встроенный шаблон доступен → Document(default_path)
    4. Встроенный шаблон недоступен → warning + Document()
```
