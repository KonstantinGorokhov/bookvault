from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

from app.settings import get_db_path


class Database:
    """Низкоуровневый доступ к SQLite (соединение + выполнение запросов)."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Инициализирует объект БД.

        Args:
            db_path: Путь к файлу SQLite. Если не задан, используется путь по умолчанию.
        """
        self._db_path = str(db_path or get_db_path())
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        """Возвращает активное соединение.

        Returns:
            sqlite3.Connection.

        Raises:
            RuntimeError: Если соединение не инициализировано.
        """
        if self._conn is None:
            raise RuntimeError(
                "Соединение с БД не инициализировано. Вызовите initialize()."
            )
        return self._conn

    def initialize(self) -> None:
        """Открывает соединение и создаёт схему БД, если её нет."""
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._create_schema()

    def _create_schema(self) -> None:
        """Создаёт таблицы приложения."""
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL DEFAULT '',
                path TEXT NOT NULL UNIQUE,
                size_bytes INTEGER NOT NULL DEFAULT 0,
                format TEXT NOT NULL DEFAULT 'pdf',
                added_at TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
            CREATE INDEX IF NOT EXISTS idx_books_added_at ON books(added_at);

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

    def execute(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        """Выполняет SQL запрос (INSERT/UPDATE/DELETE) и фиксирует транзакцию.

        Args:
            sql: SQL строка.
            params: Параметры запроса.

        Returns:
            sqlite3.Cursor.
        """
        cur = self.conn.execute(sql, tuple(params))
        self.conn.commit()
        return cur

    def query(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        """Выполняет SELECT и возвращает строки результата.

        Args:
            sql: SQL строка.
            params: Параметры запроса.

        Returns:
            Список sqlite3.Row.
        """
        cur = self.conn.execute(sql, tuple(params))
        return cur.fetchall()

    @staticmethod
    def now_iso() -> str:
        """Возвращает текущую дату/время в ISO формате.

        Returns:
            ISO строка вида YYYY-MM-DDTHH:MM:SS.
        """
        return datetime.now().isoformat(timespec="seconds")
