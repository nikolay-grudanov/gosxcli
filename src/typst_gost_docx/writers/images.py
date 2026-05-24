"""Images manager for handling image insertion."""

import logging
from pathlib import Path
from typing import Optional

from docx.document import Document as _Document
from docx.shared import Inches


class ImagesManager:
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.image_counter = 0
        self.base_dir = base_dir

    def add_image(self, doc: _Document, image_path: str, width: Optional[Inches] = None) -> None:
        self.image_counter += 1

        path = Path(image_path)
        # Resolve relative paths against base_dir (input file's parent directory)
        if not path.is_absolute() and self.base_dir:
            path = self.base_dir / path
        if not path.exists():
            logging.getLogger("typst_gost_docx").warning(f"Image not found: {image_path} (resolved: {path})")
            return

        if width is None:
            width = Inches(5.0)

        doc.add_picture(str(path), width=width)
