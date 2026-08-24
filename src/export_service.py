from __future__ import annotations

from pathlib import Path

import pandas as pd


def ensure_output_dirs(root: str | Path = "outputs") -> dict[str, Path]:
    root = Path(root)
    paths = {
        name: root / name
        for name in ["charts", "articles", "scripts", "storyboards", "powerbi", "videos"]
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def save_text(text: str, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def save_csv(df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path
