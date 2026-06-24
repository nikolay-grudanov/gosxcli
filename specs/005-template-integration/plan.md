# Implementation Plan: GOST Template Integration

**Branch**: `005-template-integration` | **Date**: 2026-05-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-template-integration/spec.md`

## Summary

Заменить ручную настройку стилей (`_configure_styles()`) в DocxWriter на использование готового DOCX-шаблона ВКР (`Шаблон_оформления_ВКР_2026_новый.docx`) как `reference_doc` по умолчанию. Шаблон содержит преднастроенные стили ГОСТ 7.32-2017 (Times New Roman 14pt, чёрные заголовки, центрированные подписи). Добавить StyleResolver для корректного разрешения стилей с учётом нестандартных style_id в шаблоне. Обновить CLI опцией `--reference-doc` с fallback на встроенный шаблон.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: python-docx>=1.1.0, importlib.resources (stdlib), Typer, Pydantic v2
**Storage**: File-based (DOCX template in package, `src/typst_gost_docx/templates/`)
**Testing**: pytest с fixture-based подходом (типовые .typ → .docx конвертации)
**Target Platform**: Cross-platform (Linux, macOS, Windows) — CLI tool
**Project Type**: CLI tool (library + CLI)
**Performance Goals**: Нет существенных требований — загрузка шаблона одноразовая при `Document(reference_doc)`
**Constraints**: python-docx ограниченный API для style lookup (name-based через `__getitem__` может не работать с нестандартными style_id)
**Scale/Scope**: Одиночный файл шаблона (~100KB), 209 стилей в шаблоне, 6 кастомных стилей для маппинга

### Critical Finding: Non-standard style_id

Шаблон ВКР содержит нестандартные style_id для Heading 1-3:
- `Heading 1` → style_id=`781` (стандарт: `Heading1`)
- `Heading 2` → style_id=`782` (стандарт: `Heading2`)
- `Heading 3` → style_id=`783` (стандарт: `Heading3`)

Это означает:
- `doc.styles['Heading 1']` → **KeyError** (python-docx ищет по name→style_id маппингу)
- `doc.add_heading('Test', level=1)` → **KeyError** (внутренне ищет 'Heading 1')
- `doc.add_paragraph('Test', style='Heading 1')` → **KeyError**

**Решение**: StyleResolver с итеративным поиском по имени + кэширование найденных стилей.

### Template Style Analysis

| Стиль | Шрифт | Размер | Bold | Italic | Выравнивание | Особенности |
|-------|-------|--------|------|--------|-------------|-------------|
| Normal | Times New Roman | 14pt | - | - | JUSTIFY | line_spacing=1.5, first_line_indent=~1.25cm, space_after=152400 |
| Heading 1 | (наследуется) | (наследуется) | True | - | CENTER | keep_together, keep_with_next, page_break_before |
| Heading 2 | (наследуется) | (наследуется) | True | - | (наследуется) | color=000000, keep_together, keep_with_next, space_before=25400 |
| Heading 3 | (наследуется) | (наследуется) | True | - | (наследуется) | keep_together, keep_with_next, space_before=25400 |
| Заг_не_содержание | (наследуется) | (наследуется) | True | - | CENTER | keep_together, keep_with_next, page_break_before |
| Титул | (наследуется) | (наследуется) | - | - | CENTER | — |
| Подпись рисунков | (наследуется) | (наследуется) | - | - | CENTER | first_line_indent=0 |
| Таблица название | (наследуется) | 14pt | - | False | (наследуется) | first_line_indent=0, keep_with_next, space_after=76200 |
| Формулы | (наследуется) | (наследуется) | - | - | (наследуется) | space_before=152400 |
| Table Grid | — | — | — | — | — | Table style (borders) |

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Единственная ответственность пайплайна
- ✅ PASS — Изменения затрагивают только Writer слой (`writers/docx_writer.py`, `writers/styles.py`)
- Ingest, Parser, IR слои не затрагиваются

### Gate 2: IR как священный контракт
- ✅ PASS — IR модель не изменяется
- Writer по-прежнему получает IRDocument и генерирует DOCX

### Gate 3: Тихий пропуск запрещён
- ✅ PASS — При отсутствии стиля в шаблоне: warning в лог + fallback на стандартный стиль
- При отсутствии шаблона: warning + fallback на `Document()`

### Gate 4: 4-слойная архитектура ненарушаема
- ✅ PASS — StyleResolver живёт в `writers/styles.py` (Writer слой)
- Template loading через `importlib.resources` в Writer

### Gate 5: Строгий режим не ломает мягкий
- ✅ PASS — Fallback на `Document()` работает в обоих режимах
- В strict mode: предупреждение о fallback → ошибка (по существующей логике)

### GOST-первичность
- ✅ PASS — Использование ГОСТ шаблона по умолчанию
- Пользовательский шаблон имеет приоритет (обратная совместимость)

### Violations: НЕТ

## Project Structure

### Documentation (this feature)

```text
specs/005-template-integration/
├── plan.md              # Этот файл
├── research.md          # Phase 0: исследование
├── data-model.md        # Phase 1: модели данных
├── quickstart.md        # Phase 1: быстрый старт
└── contracts/           # Phase 1: контракты
    └── style-resolution.md
```

### Source Code (repository root)

```text
src/typst_gost_docx/
├── templates/                              # NEW — пакет данных с шаблоном
│   └── Шаблон_оформления_ВКР_2026_новый.docx   # Встроенный ГОСТ шаблон
├── writers/
│   ├── docx_writer.py                      # MODIFY — убрать _configure_styles(), добавить StyleResolver
│   ├── styles.py                           # MODIFY → REWRITE — StyleResolver class
│   ├── tables.py                           # MINOR — использовать Table Grid из шаблона
│   └── ... (остальные без изменений)
├── cli.py                                  # MODIFY — --reference-doc default path
├── config.py                               # MINOR — default reference_doc path
└── ...

tests/
├── unit/
│   ├── test_style_resolver.py              # NEW — тесты StyleResolver
│   └── test_template_loading.py            # NEW — тесты загрузки шаблона
├── integration/
│   └── test_template_conversion.py         # NEW — E2E с шаблоном
└── fixtures/
    └── ... (существующие фикстуры)
```

**Structure Decision**: Single project layout (CLI tool). Добавляется `templates/` директория внутри пакета для хранения встроенного шаблона. StyleResolver переписывается в `writers/styles.py`.

## Complexity Tracking

> Violations: нет
