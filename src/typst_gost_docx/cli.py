"""CLI interface for Typst to DOCX converter."""

from pathlib import Path
from typing import Optional
import typer
import json
from rich.console import Console
from rich.table import Table as RichTable

from .config import Config, MathMode
from .logging import setup_logging
from .ingest.project_loader import TypstProjectLoader
from .parser.scanner import TypstScanner
from .parser.extractor import TypstExtractor
from .parser.labels import LabelExtractor
from .parser.refs import RefResolver
from .writers.docx_writer import DocxWriter

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
    log_level: str = typer.Option("INFO", "--log-level", help="Log level"),
):
    """Convert a Typst document to DOCX with GOST styling."""

    logger = setup_logging(log_level)

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
        strict=strict,
        math_mode=math_mode,
        log_level=log_level,
    )

    try:
        with console.status("[bold green]Converting..."):
            result = _run_conversion(config)

        _print_summary(result)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


def _run_conversion(config: Config) -> dict:
    loader = TypstProjectLoader(config.input_file)
    files = loader.load()

    scanner = TypstScanner(files[str(config.input_file)])
    extractor = TypstExtractor(scanner, str(config.input_file))
    ir_document = extractor.extract()

    if config.dump_ir or config.dump_json:
        ir_json = _ir_to_json(ir_document)
        json_path = config.output_file.with_suffix(".ir.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(ir_json, f, indent=2, ensure_ascii=False)
        console.print(f"[dim]IR dumped to: {json_path}[/dim]")

    writer = DocxWriter(config.reference_doc)
    stats = writer.write(ir_document, config.output_file)

    return stats


def _ir_to_json(document) -> dict:
    def node_to_dict(node):
        result = {"node_type": node.node_type, "id": node.id}
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


def _print_summary(stats: dict) -> None:
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

    console.print()
    console.print(table)


if __name__ == "__main__":
    app()
