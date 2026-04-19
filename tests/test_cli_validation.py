"""Интеграционный тест bidirectional validation в CLI."""

import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from typst_gost_docx.ir.model import (
    Caption,
    CrossReference,
    Document,
    Figure,
    NumberingKind,
    Paragraph,
    TextRun,
)
from typst_gost_docx.writers.docx_writer import DocxWriter


def test_cli_validation_with_undefined_ref():
    """Тест валидации в CLI с неопределённой ссылкой."""
    # Создаём тестовый IR документ
    doc = Document()
    doc.blocks = [
        Figure(
            label="fig:results",
            caption=Caption(text="Results", numbering_kind=NumberingKind.FIGURE),
        ),
        Paragraph(
            runs=[
                TextRun(text="See "),
                CrossReference(target_label="fig:missing"),
            ],
        ),
    ]

    # Создаём writer и валидируем
    writer = DocxWriter()
    validation_result = writer.validate_references(doc)

    assert validation_result.has_errors
    assert "fig:missing" in validation_result.undefined_refs
    assert "fig:results" not in validation_result.undefined_refs


def test_cli_validation_no_errors():
    """Тест валидации в CLI без ошибок."""
    # Создаём тестовый IR документ
    doc = Document()
    doc.blocks = [
        Figure(
            label="fig:results",
            caption=Caption(text="Results", numbering_kind=NumberingKind.FIGURE),
        ),
        Paragraph(
            runs=[
                TextRun(text="See "),
                CrossReference(target_label="fig:results"),
            ],
        ),
    ]

    # Создаём writer и валидируем
    writer = DocxWriter()
    validation_result = writer.validate_references(doc)

    assert not validation_result.has_errors
    assert len(validation_result.undefined_refs) == 0
    assert len(validation_result.unreferenced_labels) == 0


def test_cli_validation_with_unreferenced_label():
    """Тест валидации с неиспользуемой меткой."""
    # Создаём тестовый IR документ
    doc = Document()
    doc.blocks = [
        Figure(
            label="fig:unused",
            caption=Caption(text="Unused", numbering_kind=NumberingKind.FIGURE),
        ),
    ]

    # Создаём writer и валидируем
    writer = DocxWriter()
    validation_result = writer.validate_references(doc)

    assert not validation_result.has_errors
    assert len(validation_result.undefined_refs) == 0
    assert len(validation_result.unreferenced_labels) == 1
    assert "fig:unused" in validation_result.unreferenced_labels


def test_cli_validation_stats_update():
    """Тест что статистика обновляется корректно."""
    # Создаём тестовый IR документ
    doc = Document()
    doc.blocks = [
        Figure(
            label="fig:results",
            caption=Caption(text="Results", numbering_kind=NumberingKind.FIGURE),
        ),
        Paragraph(
            runs=[
                TextRun(text="See "),
                CrossReference(target_label="fig:missing"),
                TextRun(text=" and "),
                CrossReference(target_label="fig:another_missing"),
            ],
        ),
    ]

    # Создаём writer и валидируем
    writer = DocxWriter()
    initial_stats = writer.stats.copy()

    writer.validate_references(doc)

    # Проверяем что статистика обновилась
    assert writer.stats["refs_unresolved"] == 2
    assert writer.stats["refs_unresolved"] > initial_stats["refs_unresolved"]


def test_cli_validation_multiple_calls():
    """Тест что валидация может вызываться несколько раз."""
    # Создаём writer
    writer = DocxWriter()

    # Первый документ с undefined refs
    doc1 = Document()
    doc1.blocks = [
        Paragraph(
            runs=[
                CrossReference(target_label="fig:missing"),
            ],
        ),
    ]

    result1 = writer.validate_references(doc1)
    assert result1.has_errors
    assert len(result1.undefined_refs) == 1

    # Второй документ без ошибок
    doc2 = Document()
    doc2.blocks = [
        Figure(
            label="fig:results",
            caption=Caption(text="Results", numbering_kind=NumberingKind.FIGURE),
        ),
        Paragraph(
            runs=[
                CrossReference(target_label="fig:results"),
            ],
        ),
    ]

    result2 = writer.validate_references(doc2)
    assert not result2.has_errors
    assert len(result2.undefined_refs) == 0
