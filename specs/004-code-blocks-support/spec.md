# Feature Specification: Code Blocks Support

**Feature Branch**: `[004-code-blocks-support]`
**Created**: 2026-04-20
**Status**: Draft
**Input**: Typst code blocks with syntax highlighting

## User Scenarios & Testing

### User Story 1 - Code Block Conversion (Priority: P1)

Автор академической работы включает листинги программного кода в диссертацию для демонстрации алгоритмов. После конвертации код отображается с моноширинным шрифтом, сохраняет форматирование (отступы, переносы строк) и опционально имеет подсветку синтаксиса.

**Independent Test**: Создать Typst документ с code block, конвертировать в DOCX, проверить что код сохраняет структуру.

**Acceptance Scenarios**:

1. **Given** документ содержит code block с Python кодом, **When** конвертер обрабатывает блок, **Then** DOCX содержит параграф с моноширинным шрифтом (Courier New / Consolas), сохраняет отступы и переносы строк
2. **Given** code block имеет язык программирования (python, rust, c++), **When** конвертер обрабатывает блок, **Then** опционально применяется подсветка синтаксиса через color styling
3. **Given** code block содержит специальные символы (`<`, `>`, `&`, `{`, `}`), **When** конвертер обрабатывает блок, **Then** символы корректно экранируются для DOCX/XML

### User Story 2 - Code Block Styling (Priority: P2)

Автор хочет кастомизировать внешний вид code blocks (фон, рамка, отступы). После конвертации code blocks имеют заданный стиль.

**Acceptance Scenarios**:

1. **Given** Typst code block имеет `fill: rgb("f0f0f0")`, **When** конвертер обрабатывает блок, **Then** DOCX параграф имеет серый фон
2. **Given** Typst code block имеет `radius: 4pt`, **When** конвертер обрабатывает блок, **Then** DOCX применяет border/frame если возможно

---

## Requirements

### FR-001: Code Block Recognition
System MUST распознавать Typst code blocks синтаксис:
- Многострочные блоки между ``` и ```
- Поддержка языка программирования: ```python, ```rust, ```c++, etc.

### FR-002: IR Model
System MUST добавить `CodeBlockNode` в IR model:
```python
class CodeBlockNode(BaseNode):
    node_type: NodeType = NodeType.CODE_BLOCK
    content: str = ""  # Raw code content
    language: Optional[str] = None  # python, rust, c++, etc.
    style_hints: dict[str, Any] = Field(default_factory=dict)  # fill, stroke, etc.
```

### FR-003: DOCX Generation
System MUST генерировать code blocks в DOCX:
- Моноширинный шрифт: Courier New или Consolas
- Сохранение whitespace и переносов строк
- Опциональный фон (gray shading)

### FR-004: Escape Special Characters
System MUST корректно экранировать XML специальные символы в code blocks:
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `{` → `&#123;` (если в контексте DOCX field)

### FR-005: Language Detection
System MUST определять язык программирования из code block:
- Извлекать язык из ```python, ```rust, etc.
- Default: None (plain text)

---

## Key Entities

### CodeBlockNode
Узел блока кода в IR. Содержит raw content, опциональный language identifier, и style hints для рендеринга.

---

## Success Criteria

- **SC-001**: Code block с Python кодом конвертируется в DOCX с моноширинным шрифтом
- **SC-002**: Многострочный код сохраняет отступы и переносы строк
- **SC-003**: Специальные символы не ломают DOCX (XML well-formed)
- **SC-004**: Language identifier сохраняется в IR

---

## Edge Cases

1. Пустой code block → генерировать пустой параграф с моноширинным шрифтом
2. Code block без языка → treated as plain text
3. Code block с очень длинными строками → сохранять как есть (DOCX поддерживает)
4. Вложенные фигурные скобки в коде → корректная обработка без ошибок парсинга

---

## Implementation Notes

### Typst Syntax Examples

Old syntax (0.10):
```typst
#let code = ```python
def hello():
    print("Hello")
```
```

New syntax (0.11+):
```typst
```python
def hello():
    print("Hello")
```
```

### DOCX Approach

python-docx имеет ограниченную поддержку для code blocks. Варианты:

1. **Simple approach**: Paragraph с моноширинным шрифтом, preserve spaces
2. **Advanced approach**: Table с одной ячейкой для лучшего контроля форматирования

Рекомендуем: Начать с Simple approach, улучшить позже если потребуется.

### Syntax Highlighting

Полная подсветка синтаксиса требует тяжёлых зависимостей (Pygments, etc.). Для MVP:
- Сохранять информацию о языке
- Применять базовое форматирование (моноширинный шрифт)
- Future: интеграция с Pygments для подсветки
