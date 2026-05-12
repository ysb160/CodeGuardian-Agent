from __future__ import annotations

from pathlib import Path


def save_report(markdown_report: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown_report, encoding="utf-8")
    return path
