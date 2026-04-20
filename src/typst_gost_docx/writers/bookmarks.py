"""Bookmarks manager for internal references."""

from typing import Optional

from docx.text.paragraph import Paragraph


class BookmarksManager:
    def __init__(self) -> None:
        self.bookmarks: dict[str, Paragraph] = {}
        self._bookmark_id = 0

    def add_bookmark_if_needed(self, paragraph: Paragraph, label: Optional[str]) -> None:
        if label:
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn

            self._bookmark_id += 1

            bookmark_start = OxmlElement("w:bookmarkStart")
            bookmark_start.set(qn("w:id"), str(self._bookmark_id))
            bookmark_start.set(qn("w:name"), label)

            bookmark_end = OxmlElement("w:bookmarkEnd")
            bookmark_end.set(qn("w:id"), str(self._bookmark_id))

            paragraph._element.insert(0, bookmark_start)
            paragraph._element.append(bookmark_end)

            self.bookmarks[label] = paragraph

    def add_hyperlink_to_bookmark(self, para: Paragraph, target_label: str, text: str) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        hyperlink = OxmlElement("w:hyperlink")
        hyperlink.set(qn("w:anchor"), target_label)

        run = OxmlElement("w:r")
        rPr = OxmlElement("w:rPr")

        wcolor = OxmlElement("w:color")
        wcolor.set(qn("w:val"), "0000FF")
        rPr.append(wcolor)

        wu = OxmlElement("w:u")
        wu.set(qn("w:val"), "single")
        rPr.append(wu)

        run.append(rPr)

        wt = OxmlElement("w:t")
        wt.text = text
        run.append(wt)

        hyperlink.append(run)
        para._element.append(hyperlink)

    def get_bookmark(self, label: str) -> Optional[Paragraph]:
        return self.bookmarks.get(label)
