"""CLI interface for Typst to DOCX converter."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import typer
from rich.console import Console
from rich.table import Table as RichTable

from .config import Config, MathMode, RefLabels
from .ir.model import CitationStyle
from .ingest.project_loader import TypstProjectLoader
from .logging import setup_logging
from .parser.extractor_v2 import TypstExtractorV2
from .writers.docx_writer import DocxWriter
from .writers.styles import get_default_template_path

if TYPE_CHECKING:
    from .ir.model import BaseNode, Document

app = typer.Typer(help="Typst to DOCX converter for academic documents")
console = Console()


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Input .typ file"),
    output: Path = typer.Option(None, "-o", "--output", help="Output .docx file"),
    reference_doc: Optional[Path] = typer.Option(
        None, "--reference-doc", help="Reference DOCX template"
    ),
    assets_dir: Optional[Path] = typer.Option(None, "--assets-dir", help="Assets directory"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    dump_ir: bool = typer.Option(False, "--dump-ir", help="Dump IR to JSON"),
    dump_json: bool = typer.Option(False, "--dump-json", help="Dump document JSON"),
    strict: bool = typer.Option(False, "--strict", help="Strict mode (fail on warnings)"),
    math_mode: MathMode = typer.Option(
        MathMode.FALLBACK, "--math-mode", help="Math rendering mode"
    ),
    bibliography_style: CitationStyle = typer.Option(
        CitationStyle.NUMERIC,
        "--bibliography-style",
        help="Citation style (numeric or author-year)",
    ),
    log_level: str = typer.Option("INFO", "--log-level", help="Log level"),
    benchmark: bool = typer.Option(False, "--benchmark", help="Enable benchmark mode"),
) -> None:
    """Convert a Typst document to DOCX with GOST styling."""

    setup_logging(log_level)

    if not input_file.exists():
        console.print(f"[red]Error: Input file not found: {input_file}[/red]")
        raise typer.Exit(1)

    if output is None:
        output = input_file.with_suffix(".docx")

    config = Config(
        input_file=input_file,
        output_file=output,
        reference_doc=reference_doc,
        assets_dir=assets_dir,
        debug=debug,
        dump_ir=dump_ir,
        dump_json=dump_json,
        strict_mode=strict,
        math_mode=math_mode,
        bibliography_style=bibliography_style,
        log_level=log_level,
        ref_labels=RefLabels(),
        benchmark_mode=benchmark,
    )

    try:
        with console.status("[bold green]Converting..."):
            result = _run_conversion(config)

        _print_summary(result)

        # Режим бенчмарка: выводим результаты производительности
        if benchmark:
            _print_benchmark_summary(result)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


def _run_conversion(config: Config) -> dict[str, Any]:
    """Выполняет конвертацию Typst → DOCX.

    Args:
        config: Конфигурация конвертации.

    Returns:
        Словарь со статистикой конвертации.

    Raises:
        SystemExit: Если strict_mode=True и есть неразрешённые ссылки.
    """
    import logging

    logger = logging.getLogger(__name__)

    # Измеряем время выполнения
    total_start_time = time.time()

    # Загрузка проекта
    load_start_time = time.time()
    loader = TypstProjectLoader(config.input_file)
    files = loader.load()
    load_time = time.time() - load_start_time

    # Извлечение IR
    parse_start_time = time.time()
    text = loader.resolve_includes(files)

    # Поиск библиографических файлов для распознавания цитирований
    bib_keys: set[str] = set()
    bib_files = list(config.input_file.parent.glob("*.bib"))
    if bib_files:
        from .parser.bibliography import parse_bibliography

        for bib_file in bib_files:
            try:
                bib_content = bib_file.read_text(encoding="utf-8")
                parsed = parse_bibliography(bib_content)
                bib_keys.update(parsed.entries.keys())
                logger.debug(
                    "Загружены ключи библиографии из %s: %d", bib_file.name, len(parsed.entries)
                )
            except Exception as e:
                logger.warning("Ошибка чтения библиографии %s: %s", bib_file, e)

    extractor = TypstExtractorV2(text, str(config.input_file), bib_keys=bib_keys)
    ir_document = extractor.extract()
    parse_time = time.time() - parse_start_time

    # Dump IR если нужно
    if config.dump_ir or config.dump_json:
        ir_json = _ir_to_json(ir_document)
        json_path = config.output_file.with_suffix(".ir.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(ir_json, f, indent=2, ensure_ascii=False)
        console.print(f"[dim]IR dumped to: {json_path}[/dim]")

    # Resolve template path for reporting and debug output
    resolved_template: Optional[Path] = None
    template_source: str = "none"
    if config.reference_doc is not None:
        if config.reference_doc.exists():
            resolved_template = config.reference_doc
            template_source = "custom"
        else:
            logger.warning("Пользовательский шаблон не найден: %s", config.reference_doc)
            resolved_template = get_default_template_path()
            template_source = "built-in" if resolved_template else "none"
    else:
        resolved_template = get_default_template_path()
        template_source = "built-in" if resolved_template else "none"

    logger.info(
        "Шаблон: %s (%s)",
        resolved_template or "нет",
        template_source,
    )

    # Генерация DOCX
    write_start_time = time.time()
    writer = DocxWriter(
        reference_doc=config.reference_doc,
        math_mode=config.math_mode,
        ref_labels=config.ref_labels,
        base_dir=config.input_file.parent,
    )
    stats = writer.write(ir_document, config.output_file)
    write_time = time.time() - write_start_time

    # Add template info to stats
    stats["template_path"] = str(resolved_template) if resolved_template else "—"
    stats["template_source"] = template_source

    total_time = time.time() - total_start_time

    # Выполняем bidirectional валидацию ссылок
    validation_result = writer.validate_references(ir_document)

    # Добавляем информацию о файле в результат валидации
    validation_result.file_path = str(config.input_file)

    # Форматируем и выводим отчёт о валидации
    report = validation_result.format_report()

    # Выводим отчёт построчно с форматированием Rich
    for line in report.split("\n"):
        if line.startswith("WARNING"):
            console.print(f"[yellow]{line}[/yellow]")
        elif line.startswith("INFO"):
            logger.info(line[6:].strip())  # Убираем "INFO: " префикс
        elif "Undefined references" in line:
            console.print(f"[bold yellow]{line}[/bold yellow]")
        elif "Unreferenced labels" in line:
            console.print(f"[dim cyan]{line}[/dim cyan]")
        elif line.strip():  # Не пустые строки
            console.print(line)

    # Проверка strict mode
    if config.strict_mode and validation_result.has_errors:
        error_count = len(validation_result.undefined_refs)
        console.print(
            f"[red]Error: {error_count} undefined reference(s) found in strict mode[/red]"
        )
        raise SystemExit(1)

    # Добавляем информацию о производительности в stats
    stats["load_time"] = load_time
    stats["parse_time"] = parse_time
    stats["write_time"] = write_time
    stats["total_time"] = total_time

    return stats


def _ir_to_json(document: "Document") -> dict[str, Any]:
    """Convert IR document to JSON-serializable dictionary.

    Args:
        document: IR document to convert.

    Returns:
        JSON-serializable dictionary representation.
    """

    def node_to_dict(node: "BaseNode") -> dict[str, Any]:
        result: dict[str, Any] = {"node_type": node.node_type, "id": node.id}
        if hasattr(node, "label") and node.label:
            result["label"] = node.label
        if hasattr(node, "blocks"):
            result["blocks"] = [node_to_dict(b) for b in node.blocks]
        if hasattr(node, "content"):
            result["content"] = [node_to_dict(c) for c in node.content]
        if hasattr(node, "items"):
            result["items"] = [node_to_dict(i) for i in node.items]
        if hasattr(node, "rows"):
            result["rows"] = [node_to_dict(r) for r in node.rows]
        if hasattr(node, "cells"):
            result["cells"] = [node_to_dict(c) for c in node.cells]
        if hasattr(node, "text"):
            result["text"] = node.text
        if hasattr(node, "title"):
            result["title"] = [node_to_dict(t) for t in node.title]
        if hasattr(node, "level"):
            result["level"] = node.level
        if hasattr(node, "image_path"):
            result["image_path"] = node.image_path
        if hasattr(node, "caption") and node.caption:
            result["caption"] = node_to_dict(node.caption)
        return result

    return node_to_dict(document)


def _print_summary(stats: dict[str, Any]) -> None:
    table = RichTable(title="Conversion Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="magenta")

    table.add_row("Headings", str(stats.get("headings", 0)))
    table.add_row("Paragraphs", str(stats.get("paragraphs", 0)))
    table.add_row("Tables", str(stats.get("tables", 0)))
    table.add_row("Figures", str(stats.get("figures", 0)))
    table.add_row("Equations", str(stats.get("equations", 0)))
    table.add_row("References resolved", str(stats.get("refs_resolved", 0)))
    table.add_row("References unresolved", str(stats.get("refs_unresolved", 0)))
    table.add_row("Warnings", str(stats.get("warnings", 0)))
    table.add_row("Template", str(stats.get("template_path", "—")))
    table.add_row("Template source", str(stats.get("template_source", "—")))

    console.print()
    console.print(table)


def _print_benchmark_summary(stats: dict[str, Any]) -> None:
    """Выводит результаты бенчмарка.

    Args:
        stats: Словарь со статистикой конвертации, включая времена.
    """
    table = RichTable(title="Benchmark Results")
    table.add_column("Phase", style="cyan")
    table.add_column("Time (s)", style="magenta")
    table.add_column("%", style="yellow")

    total_time = stats.get("total_time", 0)
    load_time = stats.get("load_time", 0)
    parse_time = stats.get("parse_time", 0)
    write_time = stats.get("write_time", 0)

    table.add_row("Load", f"{load_time:.3f}", f"{load_time / total_time * 100:.1f}")
    table.add_row("Parse", f"{parse_time:.3f}", f"{parse_time / total_time * 100:.1f}")
    table.add_row("Write", f"{write_time:.3f}", f"{write_time / total_time * 100:.1f}")
    table.add_row("Total", f"{total_time:.3f}", "100.0")

    console.print()
    console.print(table)

    # Сохраняем результаты в JSON файл
    results_dir = Path("benchmarks/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = {
        "timestamp": datetime.now().isoformat(),
        "total_time_seconds": total_time,
        "load_time_seconds": load_time,
        "parse_time_seconds": parse_time,
        "write_time_seconds": write_time,
    }

    result_path = results_dir / f"{timestamp}_cli_benchmark.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    console.print(f"[dim]Benchmark results saved to: {result_path}[/dim]")


if __name__ == "__main__":
    app()
