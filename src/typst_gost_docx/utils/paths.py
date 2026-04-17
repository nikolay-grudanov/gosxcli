"""Path utilities."""

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_relative_path(from_path: Path, to_path: Path) -> Path:
    return to_path.relative_to(from_path.parent)
