#!/usr/bin/env python3
"""Генерация golden DOCX файлов для regression тестов.

Этот скрипт конвертирует Typst файлы из fixtures/ в DOCX файлы,
которые используются как эталонные (golden) файлы для регрессионного тестирования.

Использование:
    python scripts/generate_golden.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path

# Базовый путь к проекту
PROJECT_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = PROJECT_ROOT / "fixtures"

# Определения golden файлов: (source_path, output_path)
GOLDEN_FILES = [
    # Minimal fixture
    (
        FIXTURES_DIR / "minimal" / "minimal_golden.typ",
        FIXTURES_DIR / "minimal" / "minimal_golden.docx",
    ),
    # Complex table fixture
    (
        FIXTURES_DIR / "complex_table" / "complex_table.typ",
        FIXTURES_DIR / "complex_table" / "complex_table.docx",
    ),
    # Equations fixture
    (
        FIXTURES_DIR / "equations" / "math-formulas.typ",
        FIXTURES_DIR / "equations" / "math-formulas.docx",
    ),
]


def generate_golden_file(source_path: Path, output_path: Path) -> bool:
    """Генерирует golden DOCX файл из Typst источника.

    Args:
        source_path: Путь к исходному Typst файлу.
        output_path: Путь для сохранения DOCX файла.

    Returns:
        True если генерация успешна, иначе False.
    """
    if not source_path.exists():
        print(f"[ERROR] Source file not found: {source_path}")
        return False

    print(f"[INFO] Converting {source_path.relative_to(PROJECT_ROOT)} -> {output_path.relative_to(PROJECT_ROOT)}")

    # Запускаем CLI для конвертации
    result = subprocess.run(
        [
            "python",
            "-m",
            "typst_gost_docx.cli",
            str(source_path),
            "-o",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )

    if result.returncode != 0:
        print(f"[ERROR] Conversion failed with return code {result.returncode}")
        print(f"[ERROR] stdout: {result.stdout}")
        print(f"[ERROR] stderr: {result.stderr}")
        return False

    if not output_path.exists():
        print(f"[ERROR] Output file not created: {output_path}")
        return False

    print(f"[OK] Generated {output_path.relative_to(PROJECT_ROOT)}")
    return True


def main() -> int:
    """Главная функция генерации golden файлов.

    Returns:
        0 если все файлы успешно сгенерированы, иначе 1.
    """
    print("=" * 80)
    print("Golden Files Generation")
    print("=" * 80)

    success_count = 0
    total_count = len(GOLDEN_FILES)

    for source_path, output_path in GOLDEN_FILES:
        if generate_golden_file(source_path, output_path):
            success_count += 1
        print()

    print("=" * 80)
    print(f"Generated: {success_count}/{total_count} golden files")

    if success_count == total_count:
        print("[OK] All golden files generated successfully")
        return 0
    else:
        print(f"[ERROR] Failed to generate {total_count - success_count} golden files")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
