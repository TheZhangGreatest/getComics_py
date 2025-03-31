from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ChapterTask:
    id: Optional[int] = None
    comic_title: str = ""
    chapter_title: str = ""
    total_images: int = 0
    downloaded_images: int = 0
    status: str = 'downloading'
    save_path: Optional[str] = None
    save_format: Optional[str] = None # pdf / cbz
    created_at: Optional[str] = None
    updated_at: Optional[str] = None