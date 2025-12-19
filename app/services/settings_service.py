from __future__ import annotations

from app.db import Database


class SettingsService:
    """Сервис для хранения пользовательских настроек в SQLite."""

    def __init__(self, db: Database) -> None:
        """Инициализация.

        Args:
            db: Экземпляр Database.
        """
        self._db = db

    def get(self, key: str, default: str) -> str:
        """Возвращает значение настройки.

        Args:
            key: Ключ настройки.
            default: Значение по умолчанию.

        Returns:
            Значение настройки или default.
        """
        rows = self._db.query("SELECT value FROM settings WHERE key = ?;", (key,))
        return rows[0]["value"] if rows else default

    def set(self, key: str, value: str) -> None:
        """Сохраняет настройку.

        Args:
            key: Ключ настройки.
            value: Значение.
        """
        self._db.execute(
            """
            INSERT INTO settings(key, value)
            VALUES(?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value;
            """,
            (key, value),
        )
