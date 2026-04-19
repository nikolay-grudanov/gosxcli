"""Performance benchmarks for Typst to DOCX conversion.

This module contains pytest-benchmark tests to measure the performance
of converting various Typst documents to DOCX format.

Performance thresholds:
- Minimal document: < 1 second
- Real VRK document: < 10 seconds
- Math formulas document: < 5 seconds
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from typst_gost_docx.ingest.project_loader import TypstProjectLoader
from typst_gost_docx.parser.extractor_v2 import TypstExtractorV2
from typst_gost_docx.writers.docx_writer import DocxWriter

# Fixture paths
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
MINIMAL_FIXTURE = FIXTURES_DIR / "minimal" / "minimal.typ"
REAL_VKR_FIXTURE = FIXTURES_DIR / "real_vkr" / "main_doc" / "thesis.typ"
MATH_FORMULAS_FIXTURE = FIXTURES_DIR / "equations" / "math-formulas.typ"

# Results directory
RESULTS_DIR = Path(__file__).parent / "results"


def run_conversion(fixture_path: Path) -> dict[str, Any]:
    """Выполняет полную конвертацию Typst → DOCX.

    Args:
        fixture_path: Путь к файлу фиксации.

    Returns:
        Словарь со статистикой конвертации.
    """
    # Создаём временный файл для вывода
    output_path = Path("/tmp") / f"{fixture_path.stem}.docx"

    # Загружаем Typst проект
    loader = TypstProjectLoader(fixture_path)
    files = loader.load()

    # Извлекаем IR
    text = files[str(fixture_path)]
    extractor = TypstExtractorV2(text, str(fixture_path))
    ir_document = extractor.extract()

    # Генерируем DOCX
    writer = DocxWriter()
    stats: dict[str, Any] = writer.write(ir_document, output_path)

    # Удаляем временный файл
    if output_path.exists():
        output_path.unlink()

    return stats


def save_benchmark_result(
    fixture_name: str,
    duration: float,
    threshold: float,
    passed: bool,
) -> None:
    """Сохраняет результат бенчмарка в JSON файл.

    Args:
        fixture_name: Имя фиксации.
        duration: Длительность конвертации в секундах.
        threshold: Пороговое значение в секундах.
        passed: Прошёл ли тест производительности.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = {
        "timestamp": datetime.now().isoformat(),
        "fixture": str(fixture_name),
        "duration_seconds": duration,
        "threshold_seconds": threshold,
        "passed": passed,
    }

    result_path = RESULTS_DIR / f"{timestamp}_{fixture_name}.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


@pytest.mark.benchmark(group="conversion")
def test_benchmark_minimal_conversion(benchmark: Any) -> None:
    """Бенчмарк конвертации минимального документа.

    Пороговое значение: < 1 секунда.

    Args:
        benchmark: pytest-benchmark fixture.
    """
    result = benchmark(run_conversion, MINIMAL_FIXTURE)

    # Проверяем пороговое значение
    assert result is not None, "Conversion result should not be None"

    # Сохраняем результат бенчмарка
    # Получаем duration из pytest-benchmark
    duration = getattr(benchmark, "stats", None)
    if duration and hasattr(duration, "stats") and hasattr(duration.stats, "mean"):
        duration_value = float(duration.stats.mean)
    else:
        duration_value = 0.0

    threshold = 1.0
    passed = duration_value < threshold

    save_benchmark_result("minimal", duration_value, threshold, passed)

    # Проверяем пороговое значение
    if not passed:
        pytest.fail(
            f"Minimal document conversion too slow: {duration_value:.3f}s "
            f"(threshold: {threshold:.3f}s)"
        )


@pytest.mark.benchmark(group="conversion")
def test_benchmark_real_vkr_conversion(benchmark: Any) -> None:
    """Бенчмарк конвертации реального VRK документа.

    Пороговое значение: < 10 секунд.

    Args:
        benchmark: pytest-benchmark fixture.
    """
    result = benchmark(run_conversion, REAL_VKR_FIXTURE)

    # Проверяем пороговое значение
    assert result is not None, "Conversion result should not be None"

    # Сохраняем результат бенчмарка
    duration = getattr(benchmark, "stats", None)
    if duration and hasattr(duration, "stats") and hasattr(duration.stats, "mean"):
        duration_value = float(duration.stats.mean)
    else:
        duration_value = 0.0

    threshold = 10.0
    passed = duration_value < threshold

    save_benchmark_result("real_vkr", duration_value, threshold, passed)

    # Проверяем пороговое значение
    if not passed:
        pytest.fail(
            f"Real VRK document conversion too slow: {duration_value:.3f}s "
            f"(threshold: {threshold:.3f}s)"
        )


@pytest.mark.benchmark(group="conversion")
def test_benchmark_math_formulas_conversion(benchmark: Any) -> None:
    """Бенчмарк конвертации документа с математическими формулами.

    Пороговое значение: < 5 секунд.

    Args:
        benchmark: pytest-benchmark fixture.
    """
    result = benchmark(run_conversion, MATH_FORMULAS_FIXTURE)

    # Проверяем пороговое значение
    assert result is not None, "Conversion result should not be None"

    # Сохраняем результат бенчмарка
    duration = getattr(benchmark, "stats", None)
    if duration and hasattr(duration, "stats") and hasattr(duration.stats, "mean"):
        duration_value = float(duration.stats.mean)
    else:
        duration_value = 0.0

    threshold = 5.0
    passed = duration_value < threshold

    save_benchmark_result("math_formulas", duration_value, threshold, passed)

    # Проверяем пороговое значение
    if not passed:
        pytest.fail(
            f"Math formulas document conversion too slow: {duration_value:.3f}s "
            f"(threshold: {threshold:.3f}s)"
        )


__all__ = [
    "test_benchmark_minimal_conversion",
    "test_benchmark_real_vkr_conversion",
    "test_benchmark_math_formulas_conversion",
]
