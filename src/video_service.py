from __future__ import annotations

from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}


def find_local_videos(folder: str | Path) -> list[Path]:
    """Streamlit에서 재생할 수 있는 로컬 영상 파일을 이름순으로 찾는다."""
    folder = Path(folder)
    if not folder.exists():
        return []
    return sorted(
        path for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    )
