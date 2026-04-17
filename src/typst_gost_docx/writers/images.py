"""Images manager for handling image insertion."""

from pathlib import Path
from docx import Document
from docx.shared import Inches
from typing import Optional


class ImagesManager:
    def __init__(self):
        self.image_counter = 0

    def add_image(self, doc: Document, image_path: str, width: Optional[Inches] = None) -> None:
        self.image_counter += 1

        path = Path(image_path)
        if not path.exists():
            return

        if width is None:
            width = Inches(5.0)

        doc.add_picture(str(path), width=width)
