from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional

from src.models import FileInfo


class FileStore:
    """SQLite persistence for file integrity baselines."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    path TEXT PRIMARY KEY,
                    hash TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    last_modified REAL NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

    def add_file(self, file_info: FileInfo) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO files (path, hash, size, last_modified)
                VALUES (?, ?, ?, ?)
                """,
                (file_info.path, file_info.hash, file_info.size, file_info.last_modified),
            )

    def replace_baseline(self, files: Iterable[FileInfo]) -> int:
        items = list(files)
        with self.conn:
            self.conn.execute("DELETE FROM files")
            self.conn.executemany(
                """
                INSERT INTO files (path, hash, size, last_modified)
                VALUES (?, ?, ?, ?)
                """,
                [(item.path, item.hash, item.size, item.last_modified) for item in items],
            )
        return len(items)

    def get_file(self, path: str) -> Optional[FileInfo]:
        cursor = self.conn.execute(
            "SELECT path, hash, size, last_modified FROM files WHERE path = ?",
            (path,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return FileInfo(row["path"], row["hash"], row["size"], row["last_modified"])

    def get_all_files(self) -> List[FileInfo]:
        cursor = self.conn.execute("SELECT path, hash, size, last_modified FROM files ORDER BY path")
        return [
            FileInfo(row["path"], row["hash"], row["size"], row["last_modified"])
            for row in cursor.fetchall()
        ]

    def set_meta(self, key: str, value: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                (key, value),
            )

    def get_meta(self, key: str) -> Optional[str]:
        cursor = self.conn.execute("SELECT value FROM meta WHERE key = ?", (key,))
        row = cursor.fetchone()
        return None if row is None else str(row["value"])

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "FileStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
