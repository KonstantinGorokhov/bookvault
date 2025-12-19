from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from app.models import Book


class BookListModel(QAbstractListModel):
    """Модель данных для списка книг (QListView)."""

    def __init__(self, books: list[Book] | None = None) -> None:
        """Инициализация.

        Args:
            books: Начальный список книг.
        """
        super().__init__()
        self._books: list[Book] = books or []

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        """Возвращает количество строк.

        Returns:
            Количество книг.
        """
        return len(self._books)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Возвращает данные для отображения/использования.

        Args:
            index: QModelIndex.
            role: Роль данных.

        Returns:
            Данные по роли или None.
        """
        if not index.isValid():
            return None

        book = self._books[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return book.title

        if role == Qt.ItemDataRole.UserRole:
            return book

        if role == Qt.ItemDataRole.ToolTipRole:
            return f"Двойной клик для открытия\n{book.path}"

        return None

    def set_books(self, books: list[Book]) -> None:
        """Заменяет список книг в модели.

        Args:
            books: Новый список книг.
        """
        self.beginResetModel()
        self._books = books
        self.endResetModel()
