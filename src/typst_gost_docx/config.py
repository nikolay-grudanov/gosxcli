"""Configuration for the converter."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from enum import StrEnum


class MathMode(StrEnum):
    NATIVE = "native"
    FALLBACK = "fallback"


@dataclass
class Config:
    input_file: Path
    output_file: Path
    reference_doc: Optional[Path] = None
    assets_dir: Optional[Path] = None
    debug: bool = False
    dump_ir: bool = False
    dump_json: bool = False
    strict: bool = False
    math_mode: MathMode = MathMode.FALLBACK
    log_level: str = "INFO"

    def __post_init__(self):
        if self.assets_dir is None:
            self.assets_dir = self.input_file.parent
