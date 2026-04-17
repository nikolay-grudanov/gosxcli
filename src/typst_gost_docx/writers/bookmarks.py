"""Bookmarks manager for internal references."""

from typing import Optional
from docx.text.paragraph import Paragraph


class BookmarksManager:
    def __init__(self):
        self.bookmarks = {}

    def add_bookmark_if_needed(self, paragraph: Paragraph, label: Optional[str]) -> None:
        if label:
            self.bookmarks[label] = paragraph

    def get_bookmark(self, label: str) -> Optional[Paragraph]:
        return self.bookmarks.get(label)
