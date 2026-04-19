"""Regression tests for DOCX output.

Эти тесты сравнивают сгенерированные DOCX файлы с golden (эталонными) файлами,
чтобы убедиться, что изменения в конвертере не ломают существующую функциональность.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Callable
from dataclasses import dataclass

from lxml import etree  # type: ignore[import-untyped]

import pytest


@dataclass
class DocxDiff:
    """Различие между двумя DOCX документами.

    Attributes:
        path: Путь к элементу в документе (XML путь).
        expected: Ожидаемое значение.
        actual: Фактическое значение.
        message: Сообщение о различии.
    """

    path: str
    expected: str
    actual: str
    message: str


class DocxComparator:
    """Сравнивает два DOCX документа."""

    def __init__(self, golden_path: Path, generated_path: Path):
        """Инициализирует компаратор.

        Args:
            golden_path: Путь к golden DOCX файлу.
            generated_path: Путь к сгенерированному DOCX файлу.
        """
        self.golden_path = golden_path
        self.generated_path = generated_path
        self.diffs: list[DocxDiff] = []

    def compare_structure(self) -> bool:
        """Сравнивает структуру документов (headings, paragraphs, tables).

        Returns:
            True если структуры совпадают, иначе False.
        """
        golden_doc = self._parse_docx_structure(self.golden_path)
        generated_doc = self._parse_docx_structure(self.generated_path)

        # Сравниваем количество элементов
        elements_to_compare = [
            "headings",
            "paragraphs",
            "tables",
            "figures",
        ]

        for element in elements_to_compare:
            golden_count = golden_doc.get(element, 0)
            generated_count = generated_doc.get(element, 0)

            if golden_count != generated_count:
                self.diffs.append(
                    DocxDiff(
                        path=f"document.{element}",
                        expected=str(golden_count),
                        actual=str(generated_count),
                        message=f"Number of {element} differs: expected {golden_count}, got {generated_count}",
                    )
                )

        return len(self.diffs) == 0

    def check_empty_paragraphs(self, max_empty: int = 0) -> bool:
        """Проверяет количество пустых параграфов.

        Args:
            max_empty: Максимальное допустимое количество пустых параграфов.

        Returns:
            True если количество пустых параграфов <= max_empty, иначе False.
        """
        generated_empty = self._count_empty_paragraphs(self.generated_path)

        if generated_empty > max_empty:
            self.diffs.append(
                DocxDiff(
                    path="document.empty_paragraphs",
                    expected=f"<={max_empty}",
                    actual=str(generated_empty),
                    message=f"Too many empty paragraphs: {generated_empty} (max allowed: {max_empty})",
                )
            )
            return False

        return True

    def compare_xml_content(self) -> bool:
        """Сравнивает XML содержимое документов.

        Returns:
            True если содержимое совпадает, иначе False.
        """
        golden_xml = self._extract_document_xml(self.golden_path)
        generated_xml = self._extract_document_xml(self.generated_path)

        # Нормализуем XML для сравнения (удаляем пробелы)
        golden_normalized = self._normalize_xml(golden_xml)
        generated_normalized = self._normalize_xml(generated_xml)

        if golden_normalized != generated_normalized:
            self.diffs.append(
                DocxDiff(
                    path="document.xml",
                    expected="<golden XML>",
                    actual="<generated XML>",
                    message="XML content differs",
                )
            )
            return False

        return True

    def format_diff_report(self) -> str:
        """Форматирует отчет о различиях.

        Returns:
            Строка с отчетом о различиях.
        """
        if not self.diffs:
            return "No differences found."

        lines = ["=" * 80, "Regression Test Differences", "=" * 80, ""]

        for i, diff in enumerate(self.diffs, 1):
            lines.append(f"Diff #{i}:")
            lines.append(f"  Path: {diff.path}")
            lines.append(f"  Expected: {diff.expected}")
            lines.append(f"  Actual: {diff.actual}")
            lines.append(f"  Message: {diff.message}")
            lines.append("")

        lines.append("=" * 80)
        lines.append(f"Total differences: {len(self.diffs)}")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _parse_docx_structure(self, docx_path: Path) -> dict[str, int]:
        """Извлекает структуру DOCX документа.

        Args:
            docx_path: Путь к DOCX файлу.

        Returns:
            Словарь с количеством элементов каждого типа.
        """
        xml_content = self._extract_document_xml(docx_path)

        # Парсим XML
        root = etree.fromstring(xml_content.encode("utf-8"))

        # Пространства имён
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        structure = {
            "headings": 0,
            "paragraphs": 0,
            "tables": 0,
            "figures": 0,
        }

        # Подсчитываем параграфы
        structure["paragraphs"] = len(root.xpath("//w:p", namespaces=ns))

        # Подсчитываем заголовки (проверяем стиль)
        for paragraph in root.xpath("//w:p", namespaces=ns):
            styles = paragraph.xpath(".//w:pStyle/@w:val", namespaces=ns)
            for style in styles:
                if style.startswith("Heading"):
                    structure["headings"] += 1

        # Подсчитываем таблицы
        structure["tables"] = len(root.xpath("//w:tbl", namespaces=ns))

        # Подсчитываем рисунки (проверяем наличие изображений)
        structure["figures"] = len(root.xpath("//w:drawing", namespaces=ns))

        return structure

    def _count_empty_paragraphs(self, docx_path: Path) -> int:
        """Подсчитывает количество пустых параграфов в документе.

        Args:
            docx_path: Путь к DOCX файлу.

        Returns:
            Количество пустых параграфов.
        """
        xml_content = self._extract_document_xml(docx_path)
        root = etree.fromstring(xml_content.encode("utf-8"))

        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        empty_count = 0

        for paragraph in root.xpath("//w:p", namespaces=ns):
            # Проверяем есть ли текст в параграфе
            texts = paragraph.xpath(".//w:t/text()", namespaces=ns)
            text_content = "".join(texts).strip()

            if not text_content:
                empty_count += 1

        return empty_count

    def _extract_document_xml(self, docx_path: Path) -> str:
        """Извлекает document.xml из DOCX файла.

        Args:
            docx_path: Путь к DOCX файлу.

        Returns:
            Содержимое document.xml как строка.
        """
        with zipfile.ZipFile(docx_path, "r") as zip_file:
            # document.xml находится в word/document.xml
            return zip_file.read("word/document.xml").decode("utf-8")

    def _normalize_xml(self, xml_content: str) -> str:
        """Нормализует XML содержимое для сравнения.

        Args:
            xml_content: XML содержимое.

        Returns:
            Нормализованное XML содержимое.
        """
        # Удаляем лишние пробелы и переносы строк
        normalized = xml_content.replace("\n", "").replace("\r", "").replace("\t", "")

        # Удаляем множественные пробелы
        while "  " in normalized:
            normalized = normalized.replace("  ", " ")

        return normalized.strip()


class TestRegression:
    """Регрессионные тесты для DOCX вывода."""

    def test_minimal_regression(
        self,
        golden_docx_path: dict[str, Path],
        golden_typst_path: dict[str, Path],
        convert_to_docx: Callable[[Path, Path | None], Path],
        tmp_path: Path,
        request: pytest.FixtureRequest,
    ) -> None:
        """Регрессионный тест для minimal fixture."""
        self._run_regression_test(
            fixture_name="minimal",
            golden_docx_path=golden_docx_path,
            golden_typst_path=golden_typst_path,
            convert_to_docx=convert_to_docx,
            tmp_path=tmp_path,
            request=request,
        )

    def test_complex_table_regression(
        self,
        golden_docx_path: dict[str, Path],
        golden_typst_path: dict[str, Path],
        convert_to_docx: Callable[[Path, Path | None], Path],
        tmp_path: Path,
        request: pytest.FixtureRequest,
    ) -> None:
        """Регрессионный тест для complex_table fixture."""
        self._run_regression_test(
            fixture_name="complex_table",
            golden_docx_path=golden_docx_path,
            golden_typst_path=golden_typst_path,
            convert_to_docx=convert_to_docx,
            tmp_path=tmp_path,
            request=request,
        )

    def test_equations_regression(
        self,
        golden_docx_path: dict[str, Path],
        golden_typst_path: dict[str, Path],
        convert_to_docx: Callable[[Path, Path | None], Path],
        tmp_path: Path,
        request: pytest.FixtureRequest,
    ) -> None:
        """Регрессионный тест для equations fixture."""
        self._run_regression_test(
            fixture_name="equations",
            golden_docx_path=golden_docx_path,
            golden_typst_path=golden_typst_path,
            convert_to_docx=convert_to_docx,
            tmp_path=tmp_path,
            request=request,
        )

    def _run_regression_test(
        self,
        fixture_name: str,
        golden_docx_path: dict[str, Path],
        golden_typst_path: dict[str, Path],
        convert_to_docx: Callable[[Path, Path | None], Path],
        tmp_path: Path,
        request: pytest.FixtureRequest,
    ) -> None:
        """Запускает регрессионный тест для указанного fixture.

        Args:
            fixture_name: Имя fixture.
            golden_docx_path: Словарь путей к golden DOCX файлам.
            golden_typst_path: Словарь путей к Typst файлам.
            convert_to_docx: Функция для конвертации Typst в DOCX.
            tmp_path: Временная директория для вывода.
            request: Pytest request объект для опций.
        """
        # Проверяем опцию --update-golden
        update_golden = request.config.getoption("--update-golden", default=False)

        golden_docx = golden_docx_path[fixture_name]
        typst_file = golden_typst_path[fixture_name]

        # Если запрошено обновление golden файлов
        if update_golden:
            generated_docx = convert_to_docx(typst_file, tmp_path)
            # Копируем сгенерированный файл в golden
            import shutil

            shutil.copy2(generated_docx, golden_docx)
            pytest.skip(f"Golden file updated: {golden_docx}")

        # Генерируем DOCX
        generated_docx = convert_to_docx(typst_file, tmp_path)

        # Сравниваем с golden
        comparator = DocxComparator(golden_docx, generated_docx)

        # Проверяем структуру
        structure_match = comparator.compare_structure()

        # Проверяем пустые параграфы (допускаем до 10, так как уравнения и таблицы создают пустые параграфы)
        no_empty_paragraphs = comparator.check_empty_paragraphs(max_empty=10)

        # Формируем отчет о различиях
        diff_report = comparator.format_diff_report()

        # Если есть различия, выводим отчет и проваливаем тест
        if not structure_match or not no_empty_paragraphs:
            pytest.fail(
                f"Regression test failed for {fixture_name}:\n\n{diff_report}",
                pytrace=False,
            )
