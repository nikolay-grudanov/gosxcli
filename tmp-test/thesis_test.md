---
lang: ru-RU
title: Тестирование конвейера gosxcli
subtitle: Проверка скиллов drawio-from-spec и gost-docx-pipeline
author: Николай Груданов
org: Институт ядерных технологий
date: 2026
---

# СОДЕРЖАНИЕ
{:.标注}
1 Введение
2 Описание проекта
3 Архитектура системы
4 Конвейер конвертации
5 Структура данных
6 Заключение

---

# 1 Введение

В рамках подготовки выпускной квалификационной работы (ВКР) было проведено тестирование двух новых программных скиллов: `drawio-from-spec` — для генерации диаграмм в формате draw.io из JSON-спецификаций, и `gost-docx-pipeline` — для сборки DOCX-файлов по ГОСТ 7.32-2017.

Цель тестирования — оценить применимость скиллов для академической документации и документирования проекта `gosxcli` (Typst GOST DOCX Converter) — инструмента для конвертации Typst-документов в DOCX с поддержкой стилизации по ГОСТ.

# 2 Описание проекта gosxcli

## 2.1 Назначение

**gosxcli** (Typst GOST DOCX Converter) — CLI-инструмент для конвертации Typst-документов в формат DOCX с полной поддержкой стилизации по ГОСТ 7.32-2017 (научно-технический отчёт). Проект предназначен для академических документов, диссертаций и научных работ [](cite: gosxcligithub).

## 2.2 Технологический стек

Проект построен на Python 3.12+ с использованием следующих ключевых библиотек:

- **Typer** — CLI-интерфейс;
- **Pydantic v2** — валидация данных и конфигурации;
- **python-docx** — генерация DOCX;
- **lxml** — XML/HTML-парсинг;
- **Rich** — форматированный вывод в CLI.

## 2.3 Текущий статус

Статус проекта: MVP v0.3.1 [](cite: gosxcliproject). Реализована базовая поддержка заголовков, параграфов, списков, рисунков, таблиц, формул, меток и ссылок.

# 3 Архитектура системы

Проект использует 4-слойную архитектуру конвейера обработки документов [](cite: cleanarch).

## Рисунок 1 — Архитектура gosxcli (компонентная диаграмма)

{#figure:assets/gosxcli_pipeline.png:Архитектура четырёхслойного конвейера gosxcli}

На рисунке 1 представлена компонентная диаграмма архитектуры системы. Конвейер состоит из следующих слоёв:

1. **CLI (Typer)** — интерфейс командной строки, принимает команды пользователя;
2. **Ingest (project loader)** — загрузка Typst-проектов из файловой системы;
3. **Parser (scanner + extractor)** — извлечение структуры документа в промежуточное представление;
4. **IR (Pydantic models)** — типизированные модели данных промежуточного представления;
5. **Writer (docx_writer)** — генерация финального DOCX из IR.

Вспомогательные модули: `styles.py` (стилизация по ГОСТ), `tables.py` (генерация таблиц), `images.py` (обработка изображений), `config.py` (конфигурация через Pydantic).

## 3.1 Модуль Ingest

Модуль `ingest/` отвечает за загрузку Typst-проектов. Содержит:

- `typst_client.py` — клиент для взаимодействия с Typst-компилятором;
- `project_loader.py` — загрузчик проектов с файловой системы.

## 3.2 Модуль Parser

Модуль `parser/` преобразует Typst-исходники в IR-узлы. Содержит:

- `scanner.py` — токенизация Typst-синтаксиса;
- `extractor.py` — извлечение структурных элементов;
- `labels.py` — работа с метками;
- `refs.py` — разрешение перекрёстных ссылок;
- `typst_json_converter.py` — конвертация JSON-модели Typst.

## 3.3 Модуль Writer

Модуль `writers/` отвечает за генерацию DOCX. Содержит:

- `docx_writer.py` — основной writer;
- `styles.py` — применение стилей ГОСТ (Times New Roman 14pt);
- `tables.py` — генерация таблиц с поддержкой colspan/rowspan;
- `images.py` — вставка изображений с подписями;
- `bookmarks.py` — закладки;
- `code_highlighter.py` — подсветка кода;
- `mml2omml.py` — конвертация MathML в OMML.

# 4 Конвейер конвертации

## 4.1 Основной workflow

Процесс конвертации Typst → DOCX включает следующие фазы [](cite: pipelinepattern):

#figure:assets/gosxcli_flowchart.png:Конвейер конвертации Typst в DOCX

Конвейер состоит из фаз загрузки, парсинга, валидации IR, маршрутизации по типу узла и финальной записи.

## 4.2 Последовательность вызовов

На рисунке 3 представлена диаграмма последовательностей основного процесса конвертации.

#figure:assets/gosxcli_sequence.png:Диаграмма последовательностей процесса конвертации

Типичный сценарий:

1. CLI вызывает `load_config()` — загрузка конфигурации;
2. CLI вызывает `load_project()` — загрузка Typst-проекта;
3. Вызывается `typst.compile()` — компиляция Typst;
4. Parser генерирует IR-узлы (Paragraph, Heading, Figure и др.);
5. DocxWriter получает список IR-узлов;
6. Для каждого узла применяется стиль через `apply_style()`;
7. Результат — файл `thesis_final.docx`.

# 5 Структура данных

## 5.1 Промежуточное представление (IR)

Промежуточное представление (IR) основано на Pydantic v2 моделях [](cite: pydanticbook). Структура данных представлена на рисунке 4.

#figure:assets/gosxcli_er.png:ER-диаграмма промежуточного представления gosxcli

Корневой элемент — `IRDocument`. К нему привязаны: `IRHeading` (заголовки), `IRParagraph` (параграфы), `IRFigure` (рисунки), `IRTable` (таблицы), `IRMath` (формулы).

`IRTable` содержит `IRTableCell` (ячейки). `IRParagraph` и `IRFigure` могут содержать `IRLabel` (метки). `IRFigure` связан с `IRImage` (данные изображения). `IRParagraph` может содержать `IRRef` (перекрёстные ссылки).

## 5.2 IRDocument

```python
class IRDocument(BaseModel):
    id: UUID
    title: str
    elements: list[IRNode]  # Heading, Paragraph, Figure, Table, Math
```

## 5.3 IRHeading

```python
class IRHeading(BaseModel):
    id: str           # уникальный идентификатор (@sec:intro)
    level: int        # 1, 2, 3
    text: str         # текст заголовка
```

## 5.4 IRFigure

```python
class IRFigure(BaseModel):
    path: Path        # путь к файлу изображения
    caption: str     # подпись к рисунку
    label: IRLabel | None
    image: IRImage
```

## 5.5 IRTable

```python
class IRTable(BaseModel):
    grid: list[list[str]]   # двумерный массив ячеек
    headers: bool          # есть ли заголовок
    cells: list[IRTableCell]
```

# 6 Заключение

В результате тестирования скиллов `drawio-from-spec` и `gost-docx-pipeline` установлено:

1. **drawio-from-spec** позволяет декларативно описывать диаграммы в JSON и генерировать из них .drawio-файлы. Поддерживаются component, flowchart, sequence и ER-диаграммы. Корректно работает экспорт в PNG через drawio-desktop [](cite: drawiotools).

2. **gost-docx-pipeline** обеспечивает полный конвейер Markdown → DOCX с нормализацией стилей, таблиц, формул и валидацией через OfficeCLI.

3. Совместное использование скиллов позволяет создавать академическую документацию с диаграммами, автоматически встраиваемыми в DOCX [](cite: academicwriting).

---

# СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ

[1] gosxcli GitHub Repository. https://github.com/nikolay-grudanov/gosxcli (дата обращения: 26.05.2026).

[2] gosxcli Project Status and Architecture. Internal project documentation.

[3] Clean Architecture Principles in Python Documentation.

[4] Pipeline Design Pattern. Software Engineering Handbook.

[5] Pydantic V2 Documentation. https://docs.pydantic.dev/

[6] draw.io Diagram Tools. https://www.diagrams.net/

[7] Academic Writing and Technical Documentation Standards.

---

# СПИСОКРИСУНКОВ

Рисунок 1 — Архитектура gosxcli (компонентная диаграмма)
Рисунок 2 — Конвейер конвертации Typst в DOCX
Рисунок 3 — Диаграмма последовательностей процесса конвертации
Рисунок 4 — ER-диаграмма промежуточного представления gosxcli
