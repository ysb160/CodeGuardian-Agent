from __future__ import annotations

from pathlib import Path
from typing import Optional


def read_text_file(path: str | Path, encoding: str = "utf-8") -> str:
    file_path = Path(path)
    return file_path.read_text(encoding=encoding)


def read_optional_text_file(path: Optional[str | Path], encoding: str = "utf-8") -> str:
    if path is None:
        return ""
    return read_text_file(path, encoding=encoding)
