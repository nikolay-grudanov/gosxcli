"""Typst project loader with multi-file support."""

import logging
import re
from pathlib import Path


class TypstProjectLoader:
    """Загрузчик Typst проектов с поддержкой рекурсивных #include директив.

    Позволяет загружать основной файл и все включённые через #include файлы,
    обеспечивая защиту от циклических ссылок и разрешение относительных путей.
    """

    MAX_INCLUDE_DEPTH = 10
    """Максимальная глубина рекурсии для #include директив."""

    INCLUDE_PATTERN = re.compile(r'^[^/]*#include\s+["\']([^"\']+)["\']')
    """Регулярное выражение для поиска #include директив (игнорирует комментарии)."""

    # Паттерны для поиска путей к изображениям
    IMAGE_PATTERN = re.compile(r'image\s*\(\s*["\']([^"\']+)["\']')
    """Регулярное выражение для поиска image("...") или image('...')."""

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
        files: dict[str, str] = {}
        loaded_files: set[str] = set()  # Для отслеживания уже загруженных файлов

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
        includes: list[Path] = []

        for line in content.split("\n"):
            match = self.INCLUDE_PATTERN.match(line.strip())
            if match:
                include_path = Path(match.group(1))
                includes.append(include_path)

        return includes

    def resolve_includes(self, files: dict[str, str]) -> str:
        """Заменяет #include директивы в главном файле на содержимое включённых файлов.

        Рекурсивно обрабатывает вложенные #include, защищая от циклов.
        Пропускает закомментированные строки (//).
        После раскрытия всех #include удаляет неподдерживаемые Typst-директивы.

        Args:
            files: Словарь загруженных файлов (путь → содержимое).

        Returns:
            Объединённый текст со всеми #include раскрытыми.
        """
        processed_files: set[str] = set()
        main_content = files.get(str(self.main_file), "")

        result = self._resolve_includes_recursive(
            content=main_content,
            current_file=self.main_file,
            files=files,
            processed_files=processed_files,
        )

        return self._strip_unhandled_directives(result)

    def _resolve_includes_recursive(
        self,
        content: str,
        current_file: Path,
        files: dict[str, str],
        processed_files: set[str],
        depth: int = 0,
    ) -> str:
        """Рекурсивно раскрывает #include директивы в содержимом файла.

        Args:
            content: Содержимое текущего файла.
            current_file: Путь к текущему файлу.
            files: Словарь загруженных файлов.
            processed_files: Множество уже обработанных файлов.
            depth: Текущая глубина рекурсии.

        Returns:
            Объединённый текст с раскрытыми #include.
        """
        if depth > self.MAX_INCLUDE_DEPTH:
            self.logger.warning(
                "Превышена максимальная глубина включений (%d) в %s",
                self.MAX_INCLUDE_DEPTH,
                current_file,
            )
            return content

        resolved_path_str = str(current_file.resolve())
        if resolved_path_str in processed_files:
            self.logger.debug("Файл уже обработан: %s", resolved_path_str)
            return content

        processed_files.add(resolved_path_str)

        # Разбиваем на строки и обрабатываем каждую
        lines = content.split("\n")
        resolved_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            match = self.INCLUDE_PATTERN.match(stripped)

            if match:
                # Нашли #include директиву
                include_path = Path(match.group(1))
                # Разрешаем путь относительно текущего файла
                resolved_include = (current_file.parent / include_path).resolve()
                include_path_str = str(resolved_include)

                # Проверяем, загружен ли файл
                if include_path_str in files:
                    # Проверяем на цикл
                    if include_path_str in processed_files:
                        self.logger.debug("Пропуск циклической ссылки: %s", include_path)
                        continue

                    # Получаем содержимое включённого файла
                    included_content = files[include_path_str]

                    # Рекурсивно обрабатываем включённый файл
                    resolved_content = self._resolve_includes_recursive(
                        content=included_content,
                        current_file=resolved_include,
                        files=files,
                        processed_files=processed_files,
                        depth=depth + 1,
                    )

                    # Переписываем пути к изображениям относительно корня проекта
                    resolved_content = self._rewrite_image_paths(
                        resolved_content, resolved_include, self.main_file
                    )

                    resolved_lines.append(resolved_content)
                    self.logger.debug("Раскрыт include: %s -> %s", include_path, resolved_include)
                else:
                    # Файл не найден в словаре
                    if self.strict_mode:
                        self.logger.warning("Файл не найден: %s", resolved_include)
                    resolved_lines.append(line)  # Оставляем оригинальную строку
            else:
                # Обычная строка, без #include
                resolved_lines.append(line)

        return "\n".join(resolved_lines)

    def get_asset_path(self, asset_name: str) -> Path | None:
        """Разрешает путь к ресурсу относительно корня проекта.

        Args:
            asset_name: Имя ресурса (относительный или абсолютный путь).

        Returns:
            Полный путь к ресурсу, если он существует, иначе None.
        """
        path = self.project_root / asset_name
        return path if path.exists() else None

    def _rewrite_image_paths(self, content: str, included_file: Path, main_file: Path) -> str:
        """Переписывает пути к изображениям относительно корня проекта.

        Когда глава включена через #include из подкаталога (например, chapters/),
        пути к изображениям вида "../diagrams/image.png" становятся некорректными
        относительно основного файла. Этот метод разрешает их относительно
        корня проекта (main_file.parent).

        Args:
            content: Содержимое включённого файла с путями к изображениям.
            included_file: Путь к включённому файлу.
            main_file: Путь к основному файлу проекта.

        Returns:
            Содержимое с переписанными путями к изображениям.
        """
        if "image(" not in content:
            return content

        # Папка корня проекта (где находится основной файл)
        project_root = main_file.parent

        # Функция для замены пути
        def replace_path(match: re.Match[str]) -> str:
            image_path_raw = match.group(1)

            # Пропускаем абсолютные пути и URL
            if image_path_raw.startswith("/") or image_path_raw.startswith("http"):
                return match[0]

            # Разрешаем путь относительно папки включённого файла
            included_dir = included_file.parent
            resolved_path = (included_dir / image_path_raw).resolve()

            # Если resolved path находится в проекте, делаем его относительным
            try:
                # Пытаемся сделать относительно проекта
                rel_path = resolved_path.relative_to(project_root)
                # Формируем новый относительный путь
                new_path_str = str(rel_path).replace("\\", "/")
                return f'image("{new_path_str}"'
            except ValueError:
                # Путь вне проекта, используем как есть
                self.logger.debug(
                    "Изображение вне проекта: %s (resolved from %s)",
                    resolved_path,
                    image_path_raw,
                )
                # Возвращаем оригинальный текст (весь match)
                matched_text = match.group(0)
                return matched_text

        # Находим и заменяем все image("...")
        result = self.IMAGE_PATTERN.sub(replace_path, content)

        return result

    def _strip_unhandled_directives(self, content: str) -> str:
        """Удаляет неподдерживаемые Typst-директивы из текста.

        Удаляет #import, #show, #set, #outline директивы и // комментарии,
        которые не могут быть обработаны парсером и утекают как plain text в DOCX.

        Args:
            content: Текст с раскрытыми #include директивами.

        Returns:
            Текст с удалёнными неподдерживаемыми директивами.
        """
        lines = content.split("\n")
        result_lines: list[str] = []
        skip_until_balanced = False
        paren_depth = 0

        for line in lines:
            stripped = line.strip()

            # Если мы внутри многострочного блока директивы, отслеживаем скобки
            if skip_until_balanced:
                paren_depth += stripped.count("(") - stripped.count(")")
                if paren_depth <= 0:
                    skip_until_balanced = False
                continue

            # Пропускаем строчные комментарии //
            if stripped.startswith("//"):
                continue

            # Пропускаем #import строки
            if stripped.startswith("#import"):
                continue

            # Пропускаем #set строки
            if stripped.startswith("#set"):
                continue

            # Пропускаем #outline строки (одно- или многострочные)
            if stripped.startswith("#outline"):
                paren_depth = stripped.count("(") - stripped.count(")")
                if paren_depth > 0:
                    skip_until_balanced = True
                continue

            # Пропускаем #show строки (одно- или многострочные с #show: ...)
            if stripped.startswith("#show"):
                paren_depth = stripped.count("(") - stripped.count(")")
                if paren_depth > 0:
                    skip_until_balanced = True
                continue

            result_lines.append(line)

        return "\n".join(result_lines)
