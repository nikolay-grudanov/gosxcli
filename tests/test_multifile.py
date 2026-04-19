"""Тесты для многофайловой загрузки Typst проектов."""

from pathlib import Path
import tempfile
import pytest
from typst_gost_docx.ingest.project_loader import TypstProjectLoader


def test_single_file_load() -> None:
    """Тест загрузки одиночного файла без include директив."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"
        main_file.write_text("= Heading\n\nParagraph.\n", encoding="utf-8")

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        assert len(files) == 1
        assert str(main_file) in files
        assert "= Heading" in files[str(main_file)]


def test_recursive_include_basic() -> None:
    """Тест базовой рекурсивной загрузки с #include."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"
        chapter_file = tmpdir_path / "chapter.typ"

        main_file.write_text(
            '#include "chapter.typ"\n\n= Main\n\nContent.\n',
            encoding="utf-8"
        )
        chapter_file.write_text(
            "== Chapter\n\nChapter content.\n",
            encoding="utf-8"
        )

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        assert len(files) == 2
        assert str(main_file) in files
        assert str(chapter_file) in files
        assert "== Chapter" in files[str(chapter_file)]


def test_multiple_includes() -> None:
    """Тест загрузки нескольких включённых файлов."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"
        ch1 = tmpdir_path / "ch1.typ"
        ch2 = tmpdir_path / "ch2.typ"
        ch3 = tmpdir_path / "ch3.typ"

        main_file.write_text(
            '#include "ch1.typ"\n#include "ch2.typ"\n#include "ch3.typ"\n',
            encoding="utf-8"
        )
        ch1.write_text("= Chapter 1\n", encoding="utf-8")
        ch2.write_text("= Chapter 2\n", encoding="utf-8")
        ch3.write_text("= Chapter 3\n", encoding="utf-8")

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        assert len(files) == 4
        assert all(str(f) in files for f in [main_file, ch1, ch2, ch3])


def test_nested_includes() -> None:
    """Тест вложенных #include директив."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"
        section_file = tmpdir_path / "section.typ"
        subsection_file = tmpdir_path / "subsection.typ"

        main_file.write_text('#include "section.typ"\n', encoding="utf-8")
        section_file.write_text('#include "subsection.typ"\n', encoding="utf-8")
        subsection_file.write_text("= Subsection\n", encoding="utf-8")

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        assert len(files) == 3
        assert str(subsection_file) in files
        assert "= Subsection" in files[str(subsection_file)]


def test_relative_paths() -> None:
    """Тест разрешения относительных путей."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        chapters_dir = tmpdir_path / "chapters"
        chapters_dir.mkdir()

        main_file = tmpdir_path / "main.typ"
        chapter_file = chapters_dir / "00-intro.typ"

        main_file.write_text('#include "chapters/00-intro.typ"\n', encoding="utf-8")
        chapter_file.write_text("= Introduction\n", encoding="utf-8")

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        assert len(files) == 2
        assert str(chapter_file) in files


def test_cyclic_reference_protection() -> None:
    """Тест защиты от циклических ссылок."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        file_a = tmpdir_path / "a.typ"
        file_b = tmpdir_path / "b.typ"

        # A включает B, B включает A
        file_a.write_text('#include "b.typ"\n', encoding="utf-8")
        file_b.write_text('#include "a.typ"\n', encoding="utf-8")

        loader = TypstProjectLoader(file_a)
        files = loader.load()

        # Оба файла должны быть загружены, но без бесконечной рекурсии
        assert len(files) == 2
        assert str(file_a) in files
        assert str(file_b) in files


def test_max_depth_protection() -> None:
    """Тест защиты от превышения максимальной глубины."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Создаём цепочку файлов глубиной больше MAX_INCLUDE_DEPTH
        files = []
        for i in range(TypstProjectLoader.MAX_INCLUDE_DEPTH + 2):
            file_path = tmpdir_path / f"file{i}.typ"
            if i > 0:
                # Каждый файл включает предыдущий
                file_path.write_text(f'#include "file{i-1}.typ"\n', encoding="utf-8")
            else:
                file_path.write_text("= End\n", encoding="utf-8")
            files.append(file_path)

        loader = TypstProjectLoader(files[-1])  # Начинаем с последнего файла

        with pytest.raises(RecursionError) as exc_info:
            loader.load()

        assert "Maximum include depth" in str(exc_info.value)


def test_include_in_comment() -> None:
    """Тест что #include в комментариях игнорируется."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"
        other_file = tmpdir_path / "other.typ"

        main_file.write_text(
            '// #include "other.typ"\n\n= Main\n',
            encoding="utf-8"
        )
        other_file.write_text("= Other\n", encoding="utf-8")

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        # other.typ не должен быть загружен, так как #include в комментарии
        assert len(files) == 1
        assert str(main_file) in files
        assert str(other_file) not in files


def test_strict_mode_missing_file() -> None:
    """Тест strict_mode при отсутствии включённого файла."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"

        main_file.write_text('#include "missing.typ"\n', encoding="utf-8")

        # non-strict mode - не должно выбрасывать исключение
        loader = TypstProjectLoader(main_file, strict_mode=False)
        files = loader.load()
        assert len(files) == 1  # только main файл

        # strict mode - должно выбрасывать исключение
        loader_strict = TypstProjectLoader(main_file, strict_mode=True)
        with pytest.raises(FileNotFoundError) as exc_info:
            loader_strict.load()

        assert "missing.typ" in str(exc_info.value)


def test_non_typ_files_ignored() -> None:
    """Тест что файлы с расширением, отличным от .typ, игнорируются."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"
        data_file = tmpdir_path / "data.csv"

        main_file.write_text('#include "data.csv"\n', encoding="utf-8")
        data_file.write_text("data,values\n", encoding="utf-8")

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        assert len(files) == 1
        assert str(main_file) in files
        assert str(data_file) not in files


def test_real_vkr_structure() -> None:
    """Тест загрузки реальной структуры VKR документа."""
    vkr_dir = Path("fixtures/real_vkr/main_doc").resolve()
    if not vkr_dir.exists():
        pytest.skip("Real VKR fixtures not found")

    thesis_file = vkr_dir / "thesis.typ"

    loader = TypstProjectLoader(thesis_file)
    files = loader.load()

    # Должны быть загружены thesis.typ и все включённые главы
    assert len(files) >= 2  # thesis.typ + хотя бы одна глава
    assert str(thesis_file) in files

    # Проверяем что главы загружены (используем абсолютные пути)
    expected_chapters = [
        vkr_dir / "chapters/00-vvedenie.typ",
        vkr_dir / "chapters/01-literature-review.typ",
    ]

    for chapter in expected_chapters:
        if chapter.exists():
            # Используем resolve() для получения абсолютного пути
            chapter_abs = chapter.resolve()
            assert str(chapter_abs) in files, f"Chapter {chapter_abs} should be loaded"


def test_include_with_quotes() -> None:
    """Тест #include с одинарными и двойными кавычками."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"
        file1 = tmpdir_path / "file1.typ"
        file2 = tmpdir_path / "file2.typ"

        main_file.write_text(
            '#include "file1.typ"\n#include \'file2.typ\'\n',
            encoding="utf-8"
        )
        file1.write_text("= File 1\n", encoding="utf-8")
        file2.write_text("= File 2\n", encoding="utf-8")

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        assert len(files) == 3
        assert str(file1) in files
        assert str(file2) in files


def test_empty_includes() -> None:
    """Тест что файлы без #include корректно обрабатываются."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"

        main_file.write_text("= Heading\n\nParagraph.\n", encoding="utf-8")

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        assert len(files) == 1
        assert "= Heading" in files[str(main_file)]


def test_duplicate_includes() -> None:
    """Тест что повторные #include одного и того же файла не загружают его дважды."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        main_file = tmpdir_path / "main.typ"
        shared_file = tmpdir_path / "shared.typ"

        main_file.write_text(
            '#include "shared.typ"\n#include "shared.typ"\n',
            encoding="utf-8"
        )
        shared_file.write_text("= Shared\n", encoding="utf-8")

        loader = TypstProjectLoader(main_file)
        files = loader.load()

        assert len(files) == 2  # main + shared (не 3)
        assert str(shared_file) in files
