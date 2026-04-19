"""Extract and resolve labels and references."""

import re
import uuid
from ..ir.model import (
    BaseNode,
    CrossRefMap,
    CrossReference,
    Bookmark,
    SourceLocation,
)


class LabelExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.cross_ref_map = CrossRefMap()

    def extract_labels_and_refs(self, text: str) -> list[BaseNode]:
        nodes = []

        label_pattern = r"<([\w:_-]+)>"
        ref_pattern = r"@([\w:]+)"

        for match in re.finditer(label_pattern, text):
            label = match.group(1)
            bookmark = Bookmark(
                id=str(uuid.uuid4()),
                name=label,
                label=label,
source_location=SourceLocation(file_path=self.file_path, line=0, column=0),
            )
            nodes.append(bookmark)

        for match in re.finditer(ref_pattern, text):
            target = match.group(1)
            ref = CrossReference(
                id=str(uuid.uuid4()),
                target_label=target,
                source_location=SourceLocation(file_path=self.file_path, line=0, column=0),
            )
            nodes.append(ref)

        return nodes

    def get_cross_ref_map(self) -> CrossRefMap:
        return self.cross_ref_map
