import sqlite3
from contextlib import contextmanager
import threading

class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path="DB/comic_downloader.db"):
        if not hasattr(self, 'initialized'):
            self.db_path = db_path
            self.initialized = True
            self._init_tables()
            self._lock = threading.Lock()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapter_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comic_title TEXT NOT NULL,
                chapter_title TEXT NOT NULL,
                total_images INTEGER DEFAULT 0,
                downloaded_images INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                save_path TEXT,
                save_format TEXT DEFAULT 'images',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER NOT NULL,
                image_index INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                file_path TEXT,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chapter_id) REFERENCES chapter_tasks(id) ON DELETE CASCADE
            )""")
