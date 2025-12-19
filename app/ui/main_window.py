from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.db import Database
from app.models import Book
from app.services.library_service import LibraryService
from app.services.pdf_service import PdfService
from app.services.scanner import Scanner
from app.services.settings_service import SettingsService
from app.ui.book_item_delegate import BookItemDelegate
from app.ui.book_list_model import BookListModel
from app.ui.dialogs import BookEditData, BookEditDialog
from app.ui.theme import apply_dark_palette, apply_light_palette, get_theme_stylesheet
from app.ui.widgets import ImagePreview


@dataclass
class SearchHitItem:
    """Результат поиска по тексту книги."""

    book_id: int
    page_index: int


class MainWindow(QMainWindow):
    """Главное окно приложения BookVault."""

    def __init__(self, db: Database) -> None:
        super().__init__()
        self.setWindowTitle("BookVault")

        self._db = db
        self._library = LibraryService(db)
        self._scanner = Scanner()
        self._pdf = PdfService()
        self._settings = SettingsService(db)

        self._current_book: Optional[Book] = None

        self._build_ui()
        self._restore_theme()
        self._refresh_books()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        """Создаёт интерфейс и компоновку окна."""
        root = QWidget(self)
        self.setCentralWidget(root)

        # -------------------- Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(320)

        self.title_search = QLineEdit()
        self.title_search.setPlaceholderText("Поиск по названию…")
        self.title_search.textChanged.connect(self._refresh_books)

        self.content_search = QLineEdit()
        self.content_search.setPlaceholderText("Поиск по содержимому…")
        self.content_search.returnPressed.connect(self._search_by_content)

        self.content_search_btn = QPushButton("Искать в текстах")
        self.content_search_btn.clicked.connect(self._search_by_content)

        self.books_count_label = QLabel("Всего книг: 0")
        self.books_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("По названию", "title_asc")
        self.sort_combo.addItem("По дате (новые)", "added_desc")
        self.sort_combo.addItem("По дате (старые)", "added_asc")
        self.sort_combo.currentIndexChanged.connect(self._refresh_books)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Светлая", "light")
        self.theme_combo.addItem("Тёмная", "dark")
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

        self.books_view = QListView()
        self.books_view.setItemDelegate(BookItemDelegate())
        self.books_view.setUniformItemSizes(True)
        self.books_view.setMouseTracking(True)
        self.books_view.clicked.connect(self._on_book_clicked)
        self.books_view.doubleClicked.connect(self._on_book_double_clicked)

        self.book_model = BookListModel()
        self.books_view.setModel(self.book_model)

        self.add_file_btn = QPushButton("Добавить файл")
        self.add_file_btn.clicked.connect(self._add_book_file)

        self.add_folder_btn = QPushButton("Добавить папку")
        self.add_folder_btn.clicked.connect(self._add_books_folder)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)

        # Секция поиска
        search_title_label = QLabel("Поиск по названию:")
        search_title_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        left_layout.addWidget(search_title_label)
        left_layout.addWidget(self.title_search)

        search_content_label = QLabel("Поиск по содержимому:")
        search_content_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        left_layout.addWidget(search_content_label)
        left_layout.addWidget(self.content_search)
        left_layout.addWidget(self.content_search_btn)

        # Секция настроек
        sort_label = QLabel("Сортировка:")
        sort_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        left_layout.addWidget(sort_label)
        left_layout.addWidget(self.sort_combo)

        theme_label = QLabel("Тема оформления:")
        theme_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        left_layout.addWidget(theme_label)
        left_layout.addWidget(self.theme_combo)

        # Счётчик книг
        self.books_count_label.setStyleSheet("margin-top: 15px; padding: 5px;")
        left_layout.addWidget(self.books_count_label)

        # Список книг
        left_layout.addWidget(self.books_view, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addWidget(self.add_file_btn)
        btn_row.addWidget(self.add_folder_btn)
        left_layout.addLayout(btn_row)

        sidebar.setLayout(left_layout)

        # -------------------- Content
        content = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(10)

        self.meta_label = QLabel("Выберите книгу слева.")
        self.meta_label.setWordWrap(True)
        self.meta_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.clicked.connect(self._edit_current_book)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self._delete_current_book)

        top_buttons = QHBoxLayout()
        top_buttons.setSpacing(10)
        top_buttons.addWidget(self.edit_btn)
        top_buttons.addWidget(self.delete_btn)

        self.preview = ImagePreview()
        self.preview.setText("Предпросмотр недоступен")

        self.keyword_search = QLineEdit()
        self.keyword_search.setPlaceholderText("Введите текст для поиска…")
        self.keyword_search.returnPressed.connect(self._run_keyword_search)

        self.search_btn = QPushButton("Найти")
        self.search_btn.clicked.connect(self._run_keyword_search)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        search_row.addWidget(QLabel("Поиск по тексту:"))
        search_row.addWidget(self.keyword_search, 1)
        search_row.addWidget(self.search_btn)

        self.hits_list = QListWidget()
        self.hits_list.itemClicked.connect(self._on_hit_clicked)

        right_layout.addLayout(top_buttons)
        right_layout.addWidget(self.meta_label)
        right_layout.addWidget(self.preview, 1)
        right_layout.addLayout(search_row)
        right_layout.addWidget(QLabel("Результаты поиска:"))
        right_layout.addWidget(self.hits_list, 1)

        content.setLayout(right_layout)

        # -------------------- Splitter
        splitter = QSplitter()
        splitter.addWidget(sidebar)
        splitter.addWidget(content)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        root.setLayout(layout)

    # ------------------------------------------------------------------ Theme

    def _restore_theme(self) -> None:
        """Восстанавливает выбранную тему."""
        theme_key = self._settings.get("theme", "pastel_dark")
        idx = self.theme_combo.findData(theme_key)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

    def _on_theme_changed(self) -> None:
        """Сохраняет и применяет выбранную тему."""
        theme = self.theme_combo.currentData()
        self._settings.set("theme", theme)

        print(f"[DEBUG] Смена темы на: {theme}")

        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return

        if theme == "light":
            print("[DEBUG] Применяем светлую палитру")
            apply_light_palette(app)
        else:
            print("[DEBUG] Применяем тёмную палитру")
            apply_dark_palette(app)

        # Применяем стили для выбранной темы
        app.setStyleSheet(get_theme_stylesheet(theme))
        print("[DEBUG] Стили обновлены")

        # Перерисовываем список книг с новыми цветами
        self.books_view.viewport().update()
        print("[DEBUG] Список книг обновлен")

    # ------------------------------------------------------------------ Books

    def _refresh_books(self) -> None:
        """Обновляет список книг."""
        # Сбрасываем поиск по содержимому при изменении названия
        self.content_search.clear()

        books = self._library.list_books(
            sort=self.sort_combo.currentData(),
            title_filter=self.title_search.text(),
        )
        self.book_model.set_books(books)
        self.books_count_label.setText(f"Найдено книг: {len(books)}")

        if self._current_book and self._current_book.id not in {b.id for b in books}:
            self._set_current_book(None)

    def _search_by_content(self) -> None:
        """Поиск книг по содержимому."""
        keyword = self.content_search.text().strip()

        if not keyword:
            # Если поле пустое, показываем все книги
            self._refresh_books()
            return

        # Сбрасываем поиск по названию
        self.title_search.clear()

        # Показываем индикатор загрузки
        self.content_search_btn.setEnabled(False)
        self.content_search_btn.setText("Поиск...")

        try:
            # Ищем книги по содержимому
            books = self._library.search_books_by_content(
                keyword=keyword,
                sort=self.sort_combo.currentData(),
            )
            self.book_model.set_books(books)
            self.books_count_label.setText(f"Найдено книг с '{keyword}': {len(books)}")

            if self._current_book and self._current_book.id not in {
                b.id for b in books
            }:
                self._set_current_book(None)

            # Показываем сообщение, если ничего не найдено
            if not books:
                QMessageBox.information(
                    self,
                    "Поиск завершён",
                    f"Книги, содержащие слово '{keyword}', не найдены.",
                )

        finally:
            # Восстанавливаем кнопку
            self.content_search_btn.setEnabled(True)
            self.content_search_btn.setText("Искать в текстах")

    def _on_book_clicked(self, index) -> None:
        """Обработчик выбора книги."""
        book: Book = index.data(Qt.ItemDataRole.UserRole)
        self._set_current_book(book)

    def _on_book_double_clicked(self, index) -> None:
        """Обработчик двойного клика - открывает файл книги."""
        book: Book = index.data(Qt.ItemDataRole.UserRole)
        if not book or not book.path:
            return

        if not os.path.exists(book.path):
            QMessageBox.warning(
                self,
                "Файл не найден",
                f"Файл не найден:\n{book.path}",
            )
            return

        # Открываем файл стандартным приложением ОС
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", book.path], check=True)
            elif platform.system() == "Windows":
                os.startfile(book.path)
            else:  # Linux и другие Unix-подобные системы
                subprocess.run(["xdg-open", book.path], check=True)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка открытия",
                f"Не удалось открыть файл:\n{str(e)}",
            )

    def _set_current_book(self, book: Optional[Book]) -> None:
        """Устанавливает текущую книгу."""
        self._current_book = book
        self.hits_list.clear()
        self.keyword_search.clear()

        if not book:
            self.meta_label.setText("Выберите книгу слева.")
            self.preview.clear()
            return

        self.meta_label.setText(self._format_book_meta(book))
        self._render_preview_page(0, [])

    def _format_book_meta(self, book: Book) -> str:
        """Формирует описание книги."""
        size_mb = book.size_bytes / (1024 * 1024) if book.size_bytes else 0.0
        return (
            f"Название: {book.title}\n"
            f"Автор: {book.author or '-'}\n"
            f"Формат: {book.format.upper()}\n"
            f"Размер: {size_mb:.2f} MB\n"
            f"Добавлено: {book.added_at}\n\n"
            f"Заметка:\n{book.note or ''}"
        )

    # ------------------------------------------------------------------ Import

    def _add_book_file(self) -> None:
        """Добавляет одну книгу."""
        path, _ = QFileDialog.getOpenFileName(self, "Выберите PDF", "", "PDF (*.pdf)")
        if not path:
            return

        sf = self._scanner.scan_file(path)
        if not sf:
            QMessageBox.warning(self, "Ошибка", "Файл не поддерживается.")
            return

        self._library.add_book_from_scanned(sf)
        self._refresh_books()

    def _add_books_folder(self) -> None:
        """Добавляет книги из папки."""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if not folder:
            return

        for sf in self._scanner.scan_folder(folder):
            self._library.add_book_from_scanned(sf)

        self._refresh_books()

    # ------------------------------------------------------------------ Edit / Delete

    def _edit_current_book(self) -> None:
        """Редактирует текущую книгу."""
        if not self._current_book:
            return

        dlg = BookEditDialog(
            self,
            BookEditData(
                title=self._current_book.title,
                author=self._current_book.author,
                path=self._current_book.path,
                note=self._current_book.note,
            ),
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        data = dlg.get_data()
        book_id = self._current_book.id
        if book_id is None:
            return

        self._library.update_book(
            book_id,
            data.title,
            data.author,
            data.path,
            data.note,
        )

        self._refresh_books()

    def _delete_current_book(self) -> None:
        """Удаляет книгу из базы."""
        if not self._current_book:
            return

        if (
            QMessageBox.question(self, "Удалить", "Удалить книгу из базы?")
            != QMessageBox.StandardButton.Yes
        ):
            return

        book_id = self._current_book.id
        if book_id is None:
            return

        self._library.delete_book(book_id)

        self._set_current_book(None)
        self._refresh_books()

    # ------------------------------------------------------------------ Search / Preview

    def _render_preview_page(self, page_index: int, highlights) -> None:
        """Отображает страницу PDF."""
        if not self._current_book or not os.path.exists(self._current_book.path):
            self.preview.clear()
            return

        png, scale = self._pdf.render_page_png_bytes(
            self._current_book.path, page_index
        )
        self.preview.set_png_bytes(png, highlights, scale)

    def _run_keyword_search(self) -> None:
        """Поиск по тексту PDF."""
        if not self._current_book:
            return

        hits = self._pdf.search(self._current_book.path, self.keyword_search.text())
        self.hits_list.clear()

        if not self._current_book:
            return

        book_id = self._current_book.id
        if book_id is None:
            return

        for hit in hits:
            item = QListWidgetItem(f"Страница {hit.page_index + 1}")
            item.setData(
                Qt.ItemDataRole.UserRole,
                SearchHitItem(book_id, hit.page_index),
            )
            item.setData(Qt.ItemDataRole.UserRole + 1, hit.rects)
            self.hits_list.addItem(item)

    def _on_hit_clicked(self, item: QListWidgetItem) -> None:
        """Переход к найденной странице."""
        data = item.data(Qt.ItemDataRole.UserRole)
        rects = item.data(Qt.ItemDataRole.UserRole + 1)
        self._render_preview_page(data.page_index, rects)
