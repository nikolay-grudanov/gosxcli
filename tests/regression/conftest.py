"""Shared fixtures for regression tests."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import pytest

# Базовый путь к проекту
PROJECT_ROOT = Path(__file__).parent.parent.parent
FIXTURES_DIR = PROJECT_ROOT / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Возвращает путь к директории fixtures.

    Returns:
        Путь к директории fixtures.
    """
    return FIXTURES_DIR


@pytest.fixture
def golden_docx_path() -> dict[str, Path]:
    """Возвращает словарь путей к golden DOCX файлам.

    Returns:
        Словарь с путями к golden DOCX файлам.
    """
    return {
        "minimal": FIXTURES_DIR / "minimal" / "minimal_golden.docx",
        "complex_table": FIXTURES_DIR / "complex_table" / "complex_table.docx",
        "equations": FIXTURES_DIR / "equations" / "math-formulas.docx",
    }


@pytest.fixture
def golden_typst_path() -> dict[str, Path]:
    """Возвращает словарь путей к исходным Typst файлам для golden.

    Returns:
        Словарь с путями к Typst файлам.
    """
    return {
        "minimal": FIXTURES_DIR / "minimal" / "minimal_golden.typ",
        "complex_table": FIXTURES_DIR / "complex_table" / "complex_table.typ",
        "equations": FIXTURES_DIR / "equations" / "math-formulas.typ",
    }


@pytest.fixture
def convert_to_docx() -> Callable[[Path, Path | None], Path]:
    """Возвращает функцию для конвертации Typst в DOCX.

    Returns:
        Функция, которая принимает Path к Typst файлу и возвращает Path к DOCX.
    """

    def _convert(typst_path: Path, output_dir: Path | None = None) -> Path:
        """Конвертирует Typst файл в DOCX.

        Args:
            typst_path: Путь к исходному Typst файлу.
            output_dir: Директория для вывода (по умолчанию временная).

        Returns:
            Путь к созданному DOCX файлу.
        """
        if output_dir is None:
            output_dir = Path(tempfile.gettempdir())

        output_path = output_dir / typst_path.with_suffix(".docx").name

        result = subprocess.run(
            [
                "python",
                "-m",
                "typst_gost_docx.cli",
                str(typst_path),
                "-o",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Conversion failed for {typst_path}: "
                f"return code {result.returncode}, "
                f"stdout: {result.stdout}, "
                f"stderr: {result.stderr}"
            )

        if not output_path.exists():
            raise RuntimeError(f"Output file not created: {output_path}")

        return output_path

    return _convert


def pytest_addoption(parser: pytest.Parser) -> None:
    """Добавляет опцию --update-golden для pytest.

    Args:
        parser: Pytest parser объект.
    """
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Update golden files instead of comparing",
    )
