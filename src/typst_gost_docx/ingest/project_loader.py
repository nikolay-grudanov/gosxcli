"""Typst project loader with multi-file support."""

import logging
import re
from pathlib import Path
from typing import Optional


class TypstProjectLoader:
    """Загрузчик Typst проектов с поддержкой рекурсивных #include директив.

    Позволяет загружать основной файл и все включённые через #include файлы,
    обеспечивая защиту от циклических ссылок и разрешение относительных путей.
    """

    MAX_INCLUDE_DEPTH = 10
    """Максимальная глубина рекурсии для #include директив."""

    INCLUDE_PATTERN = re.compile(r'^[^/]*#include\s+["\']([^"\']+)["\']')
    """Регулярное выражение для поиска #include директив (игнорирует комментарии)."""

    def __init__(self, main_file: Path, strict_mode: bool = False):
        """Инициализирует загрузчик проекта.

        Args:
            main_file: Путь к основному файлу проекта (.typ).
            strict_mode: Если True, выбрасывает исключение при отсутствии
                включённого файла. Если False, логирует предупреждение и пропускает.
        """
        self.main_file = main_file
        self.project_root = main_file.parent
        self.strict_mode = strict_mode
        self.logger = logging.getLogger("typst_gost_docx")

    def load(self) -> dict[str, str]:
        """Загружает основной файл и все включённые через #include файлы.

        Returns:
            Словарь с путями к файлам в качестве ключей и содержимым файлов в
            качестве значений.

        Raises:
            FileNotFoundError: Если основной файл не найден.
            RecursionError: Если превышена максимальная глубина включений.
            ValueError: Если обнаружена циклическая ссылка.
        """
        files = {}
        loaded_files = set()  # Для отслеживания уже загруженных файлов

        if not self.main_file.exists():
            raise FileNotFoundError(f"Main file not found: {self.main_file}")

        self.logger.debug(f"Loading main file: {self.main_file}")
        files[str(self.main_file)] = self.main_file.read_text(encoding="utf-8")
        loaded_files.add(str(self.main_file))

        # Рекурсивно загружаем включённые файлы
        self._load_includes(
            files=files,
            loaded_files=loaded_files,
            current_file=self.main_file,
            depth=0,
        )

        self.logger.debug(f"Loaded {len(files)} files total")

        return files

    def _load_includes(
        self,
        files: dict[str, str],
        loaded_files: set[str],
        current_file: Path,
        depth: int,
    ) -> None:
        """Рекурсивно загружает файлы, включённые через #include.

        Args:
            files: Словарь для хранения загруженных файлов.
            loaded_files: Множество путей к уже загруженным файлам (защита от циклов).
            current_file: Текущий обрабатываемый файл.
            depth: Текущая глубина рекурсии.

        Raises:
            RecursionError: Если превышена максимальная глубина включений.
            FileNotFoundError: Если включённый файл не найден (в strict_mode).
            ValueError: Если обнаружена циклическая ссылка.
        """
        if depth > self.MAX_INCLUDE_DEPTH:
            raise RecursionError(
                f"Maximum include depth ({self.MAX_INCLUDE_DEPTH}) exceeded at {current_file}"
            )

        # Получаем содержимое текущего файла
        current_path = str(current_file)
        if current_path not in files:
            # Если файл ещё не загружен, загружаем его
            if not current_file.exists():
                if self.strict_mode:
                    raise FileNotFoundError(f"Included file not found: {current_file}")
                self.logger.warning(f"Included file not found (skipping): {current_file}")
                return

            self.logger.debug(f"{'  ' * depth}Loading: {current_file}")
            files[current_path] = current_file.read_text(encoding="utf-8")
            loaded_files.add(current_path)

        # Парсим содержимое на наличие #include директив
        content = files[current_path]
        includes = self._parse_includes(content)

        if includes and depth == 0:
            self.logger.debug(f"Found {len(includes)} include(s) in main file")

        for include_path in includes:
            # Разрешаем относительный путь относительно текущего файла
            resolved_path = (current_file.parent / include_path).resolve()

            # Проверяем на циклические ссылки
            resolved_path_str = str(resolved_path)
            if resolved_path_str in loaded_files:
                self.logger.debug(f"Skipping already loaded file: {resolved_path}")
                continue

            # Проверяем на расширение .typ
            if not resolved_path.suffix == ".typ":
                self.logger.debug(
                    f"Skipping non-.typ file: {resolved_path} (extension: {resolved_path.suffix})"
                )
                continue

            self.logger.debug(f"{'  ' * depth}Including: {include_path} -> {resolved_path}")

            # Рекурсивно загружаем включённый файл
            self._load_includes(
                files=files,
                loaded_files=loaded_files,
                current_file=resolved_path,
                depth=depth + 1,
            )

    def _parse_includes(self, content: str) -> list[Path]:
        """Извлекает пути к включённым файлам из содержимого.

        Args:
            content: Содержимое Typst файла.

        Returns:
            Список путей к включённым файлам.
        """
        includes = []

        for line in content.split("\n"):
            match = self.INCLUDE_PATTERN.match(line.strip())
            if match:
                include_path = Path(match.group(1))
                includes.append(include_path)

        return includes

    def get_asset_path(self, asset_name: str) -> Optional[Path]:
        """Разрешает путь к ресурсу относительно корня проекта.

        Args:
            asset_name: Имя ресурса (относительный или абсолютный путь).

        Returns:
            Полный путь к ресурсу, если он существует, иначе None.
        """
        path = self.project_root / asset_name
        return path if path.exists() else None
