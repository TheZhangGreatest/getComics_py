from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ImageTask:
    id: Optional[int] = None
    chapter_id: int = -1
    image_index: int = 0
    image_url: str = ""
    file_path: Optional[str] = None
    status: str = 'downloading'   # downloading / success
    retry_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
