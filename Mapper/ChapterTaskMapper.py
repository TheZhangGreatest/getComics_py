from typing import Optional, List
from Entity.ChapterTask import ChapterTask
from Service.Database import Database
import threading
import sqlite3
from datetime import datetime
from Enum.DownloadStatus import DownloadStatus
class ChapterTaskMapper:
    _lock = threading.Lock()

    def __init__(self):
        self.db = Database()

    def insert(self, task: ChapterTask) -> int:
        task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._lock, self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chapter_tasks (comic_title, chapter_title, total_images, downloaded_images, status, save_path, save_format, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (task.comic_title, task.chapter_title, task.total_images, task.downloaded_images,
                  task.status, task.save_path, task.save_format, task.created_at, task.updated_at))
            return cursor.lastrowid

    def update_task(self, task: ChapterTask,conn: Optional[sqlite3.Connection] = None):
        task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if conn is not None:
            with self._lock:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE chapter_tasks 
                    SET status = ?, downloaded_images = ?, updated_at = ?
                    WHERE id = ?
                """, (task.status, task.downloaded_images, task.updated_at, task.id))
        else:
            with self._lock, self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE chapter_tasks 
                    SET status = ?, downloaded_images = ?, updated_at = ?
                    WHERE id = ?
                """, (task.status, task.downloaded_images, task.updated_at, task.id))

    def get_by_id(self, chapter_id: int) -> Optional[ChapterTask]:
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chapter_tasks WHERE id = ?", (chapter_id,))
            row = cursor.fetchone()
            return ChapterTask(**row) if row else None

    def list_all(self) -> List[ChapterTask]:
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chapter_tasks")
            return [ChapterTask(**row) for row in cursor.fetchall()]
        
    def list_not_success(self) -> List[ChapterTask]:
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chapter_tasks WHERE status != ?", (DownloadStatus.SUCCESS.value,))
            return [ChapterTask(**row) for row in cursor.fetchall()]
    def delete_by_id(self, ids: List[int]):
        if not ids:
            return  # 防止空删除
        placeholders = ','.join(['?'] * len(ids))  # 生成 ?,?,? 占位
        sql = f"DELETE FROM chapter_tasks WHERE id IN ({placeholders})"
        with self._lock, self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, ids)
