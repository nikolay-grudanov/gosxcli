"""Integration tests for strict mode validation."""

import subprocess
import tempfile
from pathlib import Path


def test_strict_mode_with_undefined_reference():
    """Тест что strict mode возвращает exit code 1 при неопределённой ссылке."""
    typst_content = """
#figure(
  image("plot.png"),
  caption: [Results],
) <fig:results>

See @missing for details.
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        typst_file = tmpdir_path / "test.typ"
        output_file = tmpdir_path / "test.docx"

        # Записываем тестовый Typst файл
        typst_file.write_text(typst_content, encoding="utf-8")

        # Запускаем CLI с флагом --strict
        result = subprocess.run(
            [
                "python",
                "-m",
                "typst_gost_docx.cli",
                str(typst_file),
                "-o",
                str(output_file),
                "--strict",
            ],
            capture_output=True,
            text=True,
            cwd="/home/gna/workspase/projects/gosxcli",
        )

        # Проверяем что exit code = 1 (ошибка)
        assert result.returncode == 1, f"Expected exit code 1, got {result.returncode}"

        # Проверяем что WARNING выводится в stdout/stderr
        output = result.stdout + result.stderr
        assert "WARNING" in output or "undefined reference" in output.lower(), (
            f"Expected WARNING in output, got: {output}"
        )


def test_strict_mode_without_undefined_reference():
    """Тест что strict mode проходит при отсутствии неопределённых ссылок."""
    typst_content = """
#figure(
  image("plot.png"),
  caption: [Results],
) <fig>

See @fig for details.
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        typst_file = tmpdir_path / "test.typ"
        output_file = tmpdir_path / "test.docx"

        # Записываем тестовый Typst файл
        typst_file.write_text(typst_content, encoding="utf-8")

        # Запускаем CLI с флагом --strict
        result = subprocess.run(
            [
                "python",
                "-m",
                "typst_gost_docx.cli",
                str(typst_file),
                "-o",
                str(output_file),
                "--strict",
            ],
            capture_output=True,
            text=True,
            cwd="/home/gna/workspase/projects/gosxcli",
        )

        # Проверяем что exit code = 0 (успех)
        assert result.returncode == 0, (
            f"Expected exit code 0, got {result.returncode}. "
            f"stdout: {result.stdout}, stderr: {result.stderr}"
        )

        # Проверяем что DOCX файл создан
        assert output_file.exists(), "Output DOCX file should be created"


def test_normal_mode_with_undefined_reference():
    """Тест что normal mode (без --strict) не завершается с ошибкой."""
    typst_content = """
#figure(
  image("plot.png"),
  caption: [Results],
) <fig:results>

See @missing for details.
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        typst_file = tmpdir_path / "test.typ"
        output_file = tmpdir_path / "test.docx"

        # Записываем тестовый Typst файл
        typst_file.write_text(typst_content, encoding="utf-8")

        # Запускаем CLI БЕЗ флага --strict
        result = subprocess.run(
            [
                "python",
                "-m",
                "typst_gost_docx.cli",
                str(typst_file),
                "-o",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            cwd="/home/gna/workspase/projects/gosxcli",
        )

        # Проверяем что exit code = 0 (успех, несмотря на undefined reference)
        assert result.returncode == 0, (
            f"Expected exit code 0, got {result.returncode}. "
            f"stdout: {result.stdout}, stderr: {result.stderr}"
        )

        # Проверяем что WARNING всё равно выводится
        output = result.stdout + result.stderr
        assert "WARNING" in output or "undefined reference" in output.lower(), (
            f"Expected WARNING in output, got: {output}"
        )
