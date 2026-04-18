# Typst GOST DOCX Converter

## Project Overview

**Typst GOST DOCX Converter (gosxcli)** — CLI инструмент для конвертации Typst документов в DOCX с поддержкой стилизации по ГОСТ 7.32-2017. Проект предназначен для академических документов, диссертаций и научных работ.

**Status:** MVP v0.1

**Tech Stack:** Python 3.12+, Typer, Pydantic v2, python-docx, lxml, Rich

**Constitution:** [.specify/memory/constitution.md](.specify/memory/constitution.md) — принципы проекта, IR-контракт, правила работы агентов

**Project State:** [state.md](state.md) — текущий статус, прогресс, известные проблемы (ОБЯЗАТЕЛЬНО читать перед работой и обновлять после)

---

## Architecture

### 4-Layer Pipeline

Проект использует 4-слойную архитектуру для конвертации документов:

```
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│  Ingest │  →   │ Parser  │  →   │   IR    │  →   │  Writer │
└─────────┘      └─────────┘      └─────────┘      └─────────┘
   .typ            IR nodes      Pydantic         .docx
```

1. **Ingest** — загрузка Typst проектов
2. **Parser** — извлечение структуры документа в IR
3. **IR** — промежуточное представление с типизированными узлами
4. **Writer** — генерация DOCX из IR

### Directory Structure

```
src/typst_gost_docx/
├── cli.py                  # CLI интерфейс (Typer)
├── config.py               # Конфигурация (Pydantic)
├── logging.py              # Логирование
├── ingest/                 # Загрузка Typst проектов
│   ├── project_loader.py   # Загрузчик проектов
│   └── typst_client.py     # Клиент Typst
├── parser/                 # Парсинг Typst → IR
│   ├── scanner.py          # Токенизация Typst
│   ├── extractor.py        # Извлечение структуры
│   ├── labels.py           # Работа с метками
│   ├── refs.py             # Разрешение ссылок
│   └── typst_json_converter.py  # Конвертация JSON
├── ir/                     # Промежуточное представление
│   └── model.py            # IR модели (Pydantic v2)
├── writers/                # Генерация DOCX
│   ├── docx_writer.py      # Основной writer
│   ├── bookmarks.py        # Закладки
│   ├── styles.py           # Применение стилей
│   ├── images.py           # Обработка изображений
│   └── tables.py           # Генерация таблиц
└── utils/                  # Утилиты
    ├── paths.py            # Работа с путями
    └── xml.py              # OpenXML утилиты
```

---

## Supported Typst Features (MVP v0.1)

### Structure
- Headings (1-3 levels)
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

**Note:** Math support is MVP - complex formulas may render as placeholders.

---

## Coding Conventions

### Language
- **Code and docstrings:** English
- **User communication:** Russian

### Standards
- **PEP 8** compliance
- **Line length:** 100 characters (ruff)
- **Type hints:** обязательны для всех публичных функций (Python 3.12+ syntax)
- **Docstrings:** Google Style для всех публичных классов, методов, функций
- **Configuration:** Pydantic v2 `BaseModel`
- **Testing:** pytest

### Stack Versions

| Компонент | Версия | Назначение |
|-----------|--------|-----------|
| Python | 3.12+ | Основной язык |
| Typer | >= 0.9.0 | CLI интерфейс |
| Pydantic | v2 | Валидация данных |
| python-docx | >= 1.1.0 | Генерация DOCX |
| lxml | >= 4.9.0 | XML/HTML парсинг |
| Rich | >= 13.0.0 | CLI форматирование |
| ruff | latest | Линтинг |
| mypy | latest | Статическая типизация |
| pytest | >= 7.0.0 | Тестирование |

---

## Architecture Constraints

### 4-Layer Pipeline Rule
**КРИТИЧНО:** Никогда не смешивать логику разных слоёв:
- Ingest модули не должны импортировать Writer
- Writer модули не должны работать напрямую с .typ файлами
- IR модули должны быть independent от Ingest и Writer

### Module Boundaries
- **Ingest/** — только загрузка Typst проектов
- **Parser/** — только парсинг и извлечение IR
- **IR/** — только модели данных (Pydantic), без бизнес-логики
- **Writers/** — только генерация DOCX из IR

### OpenXML Access
**Только через Writer модули:**
- Прямая работа с `lxml.etree` или `docx.Document` вне `writers/` — запрещено
- Все манипуляции с DOCX должны быть в `writers/docx_writer.py` или соответствующих модулях

---

## Common Tasks

### Add New Typst Feature

1. **Изучить синтаксис:** Используй `@gosxcli-researcher`
2. **Обновить IR модель:** Добавь новые типы узлов в `ir/model.py`
3. **Обновить Parser:** Добавь извлечение в `parser/extractor.py`
4. **Обновить Writer:** Добавь генерацию в соответствующий writer модуль
5. **Напиши тесты:** Добавь в `tests/`
6. **Code Review:** Используй `@gosxcli-reviewer`

### Implement Table Enhancement (e.g., colspan)

1. **Изучить Typst colspan синтаксис:** `@gosxcli-researcher`
2. **Изучить python-docx cell merging:** `@gosxcli-researcher`
3. **Обновить IR модель:** Добавь `colspan` в `IRTableCell`
4. **Обновить Parser:** Извлекай colspan из Typst
5. **Обновить Writer:** Реализуй cell merging в `writers/tables.py`
6. **Code Review:** `@gosxcli-reviewer`

### Add New CLI Option

1. **Изучить текущий CLI:** Прочитай `cli.py`
2. **Добавь опцию через Typer:** Используй `@gosxcli-developer`
3. **Обнови config:** Добавь в `config.py` (Pydantic)
4. **Обнови документацию:** README.md
5. **Code Review:** `@gosxcli-reviewer`

---

## Development Workflow

### Quality Checks

Перед коммитом обязательно:

```bash
# Линтинг
ruff check src/

# Форматирование
ruff format src/

# Типизация
mypy --strict src/

# Тесты
pytest tests/
```

### Debug Mode

Для отладки используйте:

```bash
typst-gost-docx convert thesis.typ -o thesis.docx --debug --dump-ir
```

---

## GOST Standards

### ГОСТ 7.32-2017 Requirements

Проект стремится к соответствию ГОСТ 7.32-2017 для академических документов:

- Структура документа: титульный лист, содержание, введение, основная часть, заключение, список литературы
- Нумерация разделов, подразделов, пунктов
- Ссылки на литературные источники
- Оформление таблиц, иллюстраций, приложений

### Current Implementation (MVP)

Базовая поддержка GOST:
- Стилизация заголовков
- Форматирование списков
- Подписи к рисункам и таблицам
- Нумерация страниц (базовая)

**Planned (v0.2-v0.3):**
- Полная реализация GOST 7.32-2017
- Автоматическая генерация оглавления
- Сноски и библиография

---

## Agent Workflow

**ВАЖНО:** Перед выполнением любой задачи ОБЯЗАТЕЛЬНО прочитайте [state.md](state.md) чтобы:
- Понять текущий статус проекта
- Проверить нет ли дубликатов работы
- Избежать конфликтов с активными задачами
- Понять приоритеты и контекст

После завершения задачи ОБЯЗАТЕЛЬНО обновите [state.md](state.md).

### Orchestration Pattern

1. **User** → `gosxcli-orchestrator` (анализ и планирование)
2. `gosxcli-orchestrator` → `gosxcli-researcher` (сбор информации)
3. `gosxcli-orchestrator` → `gosxcli-developer` (реализация)
4. `gosxcli-developer` → `gosxcli-reviewer` (ревью)
5. `gosxcli-reviewer` → `gosxcli-orchestrator` (отчёт)
6. `gosxcli-orchestrator` → User (финальный результат)

### Task Delegation

Subagents вызываются через @-упоминание или Task tool.

**Examples:**
- `@gosxcli-researcher "найди документацию по python-docx cell merging"`
- `@gosxcli-developer "реализуй поддержку colspan"`
- `@gosxcli-reviewer "проверь качество кода в writers/tables.py"`

---

## Roadmap

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
- Full GOST 7.32-2017 compliance

---

## Contributing

### Before Contributing

Перед началом работы:

1. **Прочитайте конституцию:** [.specify/memory/constitution.md](.specify/memory/constitution.md)
2. **Прочитайте состояние проекта:** [state.md](state.md) — ОБЯЗАТЕЛЬНО
   - Изучите текущий статус и метрики
   - Проверьте Known Issues (может быть уже решена?)
   - Посмотрите Next Steps (может быть ваша задача?)
   - Проверьте Current Work (что уже в процессе)
3. Изучите архитектуру проекта (4-layer pipeline)
4. Понимайте границы модулей
5. Соблюдайте coding conventions
6. Пройдите code review через `@gosxcli-reviewer`

### After Contributing

После завершения работы:

1. **Обновите state.md:**
   - Отметьте выполненные задачи в Current Work
   - Обновите статус в Progress Tracker
   - Закройте решённые проблемы в Known Issues
   - Добавьте новые решения в Decisions Log
   - Обновите Last Updated дату
2. Создайте коммит с изменениями

### Pull Request Checklist

- [ ] Код проходит `ruff check`
- [ ] Код проходит `mypy --strict`
- [ ] Тесты проходят (`pytest tests/`)
- [ ] Docstrings добавлены/обновлены
- [ ] 4-layer architecture соблюдена
- [ ] Code review пройден

---

## License

MIT License - see LICENSE file.