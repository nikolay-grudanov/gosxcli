"""Typst project loader."""

from pathlib import Path
from typing import Optional


class TypstProjectLoader:
    def __init__(self, main_file: Path):
        self.main_file = main_file
        self.project_root = main_file.parent

    def load(self) -> dict[str, str]:
        files = {}

        if not self.main_file.exists():
            raise FileNotFoundError(f"Main file not found: {self.main_file}")

        files[str(self.main_file)] = self.main_file.read_text(encoding="utf-8")

        return files

    def get_asset_path(self, asset_name: str) -> Optional[Path]:
        path = self.project_root / asset_name
        return path if path.exists() else None
