from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPalette
from PySide6.QtWidgets import QApplication, QStyle, QStyledItemDelegate


class BookItemDelegate(QStyledItemDelegate):
    """Delegate для отрисовки карточки книги в списке."""

    def sizeHint(self, option, index) -> QSize:
        """Возвращает предпочтительный размер элемента списка."""
        return QSize(option.rect.width(), 66)

    def paint(self, painter: QPainter, option, index) -> None:
        """Отрисовывает одну карточку книги."""
        painter.save()

        # Область карточки с внутренними отступами
        rect = option.rect.adjusted(8, 6, -8, -6)

        # Состояние элемента (выделен / под курсором)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)

        # Получаем палитру приложения для определения темы
        app = QApplication.instance()
        if isinstance(app, QApplication):
            palette = app.palette()
        else:
            palette = QPalette()
        is_dark = palette.color(QPalette.ColorRole.Window).lightness() < 128

        # Фон карточки в зависимости от состояния и темы
        if selected:
            if is_dark:
                bg_color = QColor(140, 170, 165, 90)
            else:
                bg_color = QColor(0, 122, 255, 50)  # Синий для светлой темы
        elif hovered:
            if is_dark:
                bg_color = QColor(140, 170, 165, 55)
            else:
                bg_color = QColor(0, 122, 255, 25)  # Светло-синий для светлой темы
        else:
            if is_dark:
                bg_color = QColor(255, 255, 255, 20)
            else:
                bg_color = QColor(242, 242, 247, 255)  # Светло-серый для светлой темы

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, 10, 10)

        # Получаем объект книги из модели
        book = index.data(Qt.ItemDataRole.UserRole)

        # Шрифт названия
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)

        # Шрифт метаданных
        meta_font = QFont()
        meta_font.setPointSize(9)

        # Цвета текста в зависимости от темы
        if is_dark:
            title_color = QColor(245, 245, 245)
            meta_color = QColor(200, 200, 200)
        else:
            title_color = QColor(0, 0, 0)
            meta_color = QColor(100, 100, 100)

        # Название книги
        painter.setFont(title_font)
        painter.setPen(title_color)
        painter.drawText(
            QRect(rect.left() + 12, rect.top() + 8, rect.width() - 24, 20),
            Qt.TextFlag.TextSingleLine,
            book.title,
        )

        # Автор и формат
        painter.setFont(meta_font)
        painter.setPen(meta_color)
        author = book.author or "—"
        painter.drawText(
            QRect(rect.left() + 12, rect.top() + 32, rect.width() - 24, 18),
            Qt.TextFlag.TextSingleLine,
            f"{author} • {book.format.upper()}",
        )

        painter.restore()
