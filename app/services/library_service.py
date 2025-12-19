from __future__ import annotations

import os
from datetime import datetime
from typing import Literal, Optional

from app.db import Database
from app.models import Book
from app.services.pdf_service import PdfService
from app.services.scanner import ScannedFile

SortKey = Literal["title_asc", "added_desc", "added_asc"]


class LibraryService:
    """Бизнес-логика библиотеки: добавление, обновление, удаление, список."""

    def __init__(self, db: Database) -> None:
        """Инициализация.

        Args:
            db: Экземпляр Database.
        """
        self._db = db
        self._pdf = PdfService()

    def _row_to_book(self, row) -> Book:
        """Преобразует sqlite3.Row в Book.

        Args:
            row: sqlite3.Row.

        Returns:
            Book.
        """
        return Book(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            path=row["path"],
            size_bytes=row["size_bytes"],
            format=row["format"],
            added_at=datetime.fromisoformat(row["added_at"]),
            note=row["note"],
        )

    def list_books(
        self, sort: SortKey = "title_asc", title_filter: str = ""
    ) -> list[Book]:
        """Возвращает список книг с сортировкой и фильтром по названию.

        Args:
            sort: Ключ сортировки.
            title_filter: Фильтр по названию (LIKE).

        Returns:
            Список Book.
        """
        where = ""
        params = []
        if title_filter.strip():
            where = "WHERE lower(title) LIKE lower(?)"
            params.append(f"%{title_filter.strip()}%")

        order_by = "ORDER BY title COLLATE NOCASE ASC"
        if sort == "added_desc":
            order_by = "ORDER BY added_at DESC"
        elif sort == "added_asc":
            order_by = "ORDER BY added_at ASC"

        rows = self._db.query(f"SELECT * FROM books {where} {order_by};", params)
        return [self._row_to_book(r) for r in rows]

    def search_books_by_content(
        self, keyword: str, sort: SortKey = "title_asc"
    ) -> list[Book]:
        """Возвращает список книг, содержащих ключевое слово в тексте.

        Args:
            keyword: Ключевое слово для поиска.
            sort: Ключ сортировки.

        Returns:
            Список Book, содержащих ключевое слово.
        """
        keyword = keyword.strip()
        if not keyword:
            return []

        # Получаем все книги
        all_books = self.list_books(sort=sort)

        # Фильтруем книги, содержащие ключевое слово
        matching_books = []
        for book in all_books:
            if not os.path.exists(book.path):
                continue

            try:
                # Ищем ключевое слово в PDF
                matches = self._pdf.search(book.path, keyword, max_hits=1)
                if matches:  # Если найдено хотя бы одно совпадение
                    matching_books.append(book)
            except Exception:
                # Пропускаем книги с ошибками
                continue

        return matching_books

    def get_book(self, book_id: int) -> Optional[Book]:
        """Возвращает книгу по id.

        Args:
            book_id: ID книги.

        Returns:
            Book или None.
        """
        rows = self._db.query("SELECT * FROM books WHERE id = ?;", (book_id,))
        return self._row_to_book(rows[0]) if rows else None

    def add_book_from_scanned(self, sf: ScannedFile) -> Optional[int]:
        """Добавляет книгу в БД по результату сканирования.

        Args:
            sf: ScannedFile.

        Returns:
            ID книги или None (если уже есть/ошибка).
        """
        title = ""
        author = ""

        if sf.format == "pdf":
            try:
                meta = self._pdf.extract_metadata(sf.path)
                title = (meta.get("title") or "").strip()
                author = (meta.get("author") or "").strip()
            except Exception:
                title = ""
                author = ""

        if not title:
            title = os.path.splitext(os.path.basename(sf.path))[0]

        try:
            cur = self._db.execute(
                """
                INSERT INTO books(title, author, path, size_bytes, format, added_at, note)
                VALUES(?, ?, ?, ?, ?, ?, '');
                """,
                (title, author, sf.path, sf.size_bytes, sf.format, self._db.now_iso()),
            )
            return int(cur.lastrowid) if cur.lastrowid else None
        except Exception:
            return None

    def update_book(
        self, book_id: int, title: str, author: str, path: str, note: str
    ) -> bool:
        """Обновляет редактируемые поля книги.

        Args:
            book_id: ID книги.
            title: Название.
            author: Автор.
            path: Путь к файлу.
            note: Заметка.

        Returns:
            True, если успешно.
        """
        try:
            self._db.execute(
                """
                UPDATE books
                SET title = ?, author = ?, path = ?, note = ?
                WHERE id = ?;
                """,
                (title.strip(), author.strip(), path.strip(), note, book_id),
            )
            return True
        except Exception:
            return False

    def delete_book(self, book_id: int) -> bool:
        """Удаляет книгу из БД (файл на диске не удаляется).

        Args:
            book_id: ID книги.

        Returns:
            True, если успешно.
        """
        try:
            self._db.execute("DELETE FROM books WHERE id = ?;", (book_id,))
            return True
        except Exception:
            return False
