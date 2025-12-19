from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QWidget,
)


@dataclass
class BookEditData:
    """Данные для редактирования книги."""

    title: str
    author: str
    path: str
    note: str


class BookEditDialog(QDialog):
    """Диалог редактирования метаданных книги и заметки."""

    def __init__(self, parent: QWidget | None, data: BookEditData) -> None:
        """Создает диалог.

        Args:
            parent: Родительский виджет.
            data: Начальные данные.
        """
        super().__init__(parent)
        self.setWindowTitle("Редактирование книги")

        self.title_edit = QLineEdit(data.title)
        self.author_edit = QLineEdit(data.author)
        self.path_edit = QLineEdit(data.path)

        self.note_edit = QTextEdit()
        self.note_edit.setPlainText(data.note)

        layout = QFormLayout()
        layout.addRow("Название:", self.title_edit)
        layout.addRow("Автор:", self.author_edit)
        layout.addRow("Путь:", self.path_edit)
        layout.addRow("Заметка:", self.note_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)
        self.setLayout(layout)

    def get_data(self) -> BookEditData:
        """Возвращает данные из формы.

        Returns:
            BookEditData.
        """
        return BookEditData(
            title=self.title_edit.text().strip(),
            author=self.author_edit.text().strip(),
            path=self.path_edit.text().strip(),
            note=self.note_edit.toPlainText(),
        )
