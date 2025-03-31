from typing import List, Optional, Dict
from Entity.ImageTask import ImageTask
from Service.Database import Database
import threading
from Entity.ImageTask import ImageTask
import sqlite3
from datetime import datetime
from Service.LoggerService import LoggerService
class ImageTaskMapper:

    def __init__(self):
        self.db = Database()
        self.logger = LoggerService().get_logger("database")

    def insert(self, task: ImageTask) -> int:
        task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.debug(f"插入图片任务: {task}")
        try:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO image_tasks (chapter_id, image_index, image_url, file_path, status, retry_count, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (task.chapter_id, task.image_index, task.image_url, task.file_path, 
                    task.status, task.retry_count, task.created_at, task.updated_at))
                return cursor.lastrowid
        except sqlite3.Error as e:
                # 捕获并记录错误
                self.logger.error(f"插入图片任务失败: {e}")
                raise RuntimeError(f"数据库插入失败: {e}")
        except Exception as e:
            # 捕获其他异常并记录
            self.logger.error(f"插入图片任务失败: {e}")
            raise RuntimeError(f"插入图片任务失败: {e}")

    def get_pending_images(self, chapter_id: int) -> List[ImageTask]:
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM image_tasks 
                WHERE chapter_id = ? AND status != 'finished'
                ORDER BY image_index
            """, (chapter_id,))
            return [ImageTask(**row) for row in cursor.fetchall()]

    def update_task(self, task: ImageTask, conn: Optional[sqlite3.Connection] = None):
        task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        """更新图片任务，支持事务"""
        if conn is not None:
            # 使用外部事务
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE image_tasks 
                SET status = ?, retry_count = ?, updated_at = ?
                WHERE id = ?
            """, (task.status, task.retry_count, task.updated_at, task.id))
        else:
            # 独立事务
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE image_tasks 
                    SET status = ?, retry_count = ?, updated_at = ?
                    WHERE id = ?
                """, (task.status, task.retry_count, task.updated_at, task.id))

    def list_by_conditions(self, condition: Optional[Dict] = None) -> List[ImageTask]:
        with self.db.connect() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM image_tasks"
            params = []
            if condition:
                where_clause = ' AND '.join([f'{key} = ?' for key in condition.keys()])
                sql += f" WHERE {where_clause}"
                params = list(condition.values())
            sql += " ORDER BY image_index"
            cursor.execute(sql, params)
            return [ImageTask(**row) for row in cursor.fetchall()]

    def list_by_chapter_id(self, chapter_id: int) -> List[ImageTask]:
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM image_tasks 
                WHERE chapter_id = ?
                ORDER BY image_index
            """, (chapter_id,))
            return [ImageTask(**row) for row in cursor.fetchall()]
    def delete_by_chapter_id(self, chapter_id: int):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM image_tasks WHERE chapter_id = ?", (chapter_id,))

