"""Модуль для управления темами приложения."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def apply_light_palette(app: QApplication) -> None:
    """Применяет светлую тему (macOS Light).

    Args:
        app: Экземпляр QApplication.
    """
    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))

    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F2F2F7"))

    palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#F2F2F7"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))

    palette.setColor(QPalette.ColorRole.Highlight, QColor("#007AFF"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    app.setPalette(palette)


def apply_dark_palette(app: QApplication) -> None:
    """Применяет тёмную тему (macOS Dark).

    Args:
        app: Экземпляр QApplication.
    """
    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window, QColor("#1C1C1E"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#FFFFFF"))

    palette.setColor(QPalette.ColorRole.Base, QColor("#2C2C2E"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#3A3A3C"))

    palette.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#2C2C2E"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))

    palette.setColor(QPalette.ColorRole.Highlight, QColor("#0A84FF"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    app.setPalette(palette)


def get_theme_stylesheet(theme: str) -> str:
    """Возвращает QSS стили для указанной темы.

    Args:
        theme: Название темы ("light" или "dark").

    Returns:
        Строка со стилями QSS.
    """
    if theme == "light":
        return """
QWidget {
    font-size: 13px;
}

QLabel {
    color: #000000;
}

QPushButton {
    padding: 6px 12px;
    border-radius: 6px;
    border: 1px solid #D1D1D6;
    background-color: #F2F2F7;
}

QPushButton:hover {
    background-color: #E5E5EA;
    border: 1px solid #C7C7CC;
}

QPushButton:pressed {
    background-color: #D1D1D6;
}

QLineEdit, QComboBox {
    padding: 6px 8px;
    border-radius: 6px;
    border: 1px solid #D1D1D6;
    background-color: #FFFFFF;
}

QLineEdit:focus {
    border: 2px solid #007AFF;
}

QComboBox {
    background-color: #F2F2F7;
}

QComboBox:hover {
    border: 1px solid #C7C7CC;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}

QComboBox QAbstractItemView {
    border: 1px solid #D1D1D6;
    background-color: #FFFFFF;
    selection-background-color: #007AFF;
    selection-color: #FFFFFF;
    outline: none;
}

QListView {
    outline: none;
    border: 1px solid #D1D1D6;
    border-radius: 6px;
    background-color: #F9F9F9;
}

QListWidget {
    outline: none;
    border: 1px solid #D1D1D6;
    border-radius: 6px;
    background-color: #F9F9F9;
}

#Sidebar {
    background-color: #F2F2F7;
    border-right: 1px solid #D1D1D6;
}

QLabel[styleSheet*="font-weight: bold"] {
    color: #1C1C1E;
    font-size: 12px;
}

#Preview {
    border: 1px solid #D1D1D6;
    border-radius: 10px;
    padding: 10px;
    background-color: #FAFAFA;
}

/* Скроллбары для светлой темы */
QScrollBar:vertical {
    border: none;
    background: #F2F2F7;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #C7C7CC;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #AEAEB2;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #F2F2F7;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #C7C7CC;
    min-width: 20px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background: #AEAEB2;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""
    else:  # dark theme
        return """
QWidget {
    font-size: 13px;
}

QLabel {
    color: #FFFFFF;
}

QPushButton {
    padding: 6px 12px;
    border-radius: 6px;
    border: 1px solid #48484A;
    background-color: #2C2C2E;
}

QPushButton:hover {
    background-color: #3A3A3C;
    border: 1px solid #5A5A5C;
}

QPushButton:pressed {
    background-color: #48484A;
}

QLineEdit, QComboBox {
    padding: 6px 8px;
    border-radius: 6px;
    border: 1px solid #48484A;
    background-color: #2C2C2E;
}

QLineEdit:focus {
    border: 2px solid #0A84FF;
}

QComboBox {
    background-color: #2C2C2E;
}

QComboBox:hover {
    border: 1px solid #5A5A5C;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}

QComboBox QAbstractItemView {
    border: 1px solid #48484A;
    background-color: #2C2C2E;
    selection-background-color: #0A84FF;
    selection-color: #FFFFFF;
    outline: none;
}

QListView {
    outline: none;
    border: 1px solid #48484A;
    border-radius: 6px;
    background-color: #2C2C2E;
}

QListWidget {
    outline: none;
    border: 1px solid #48484A;
    border-radius: 6px;
    background-color: #2C2C2E;
}

#Sidebar {
    background-color: #1C1C1E;
    border-right: 1px solid #48484A;
}

QLabel[styleSheet*="font-weight: bold"] {
    color: #FFFFFF;
    font-size: 12px;
}

#Preview {
    border: 1px solid #48484A;
    border-radius: 10px;
    padding: 10px;
    background-color: #1C1C1E;
}

/* Скроллбары для тёмной темы */
QScrollBar:vertical {
    border: none;
    background: #1C1C1E;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #48484A;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #5A5A5C;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #1C1C1E;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #48484A;
    min-width: 20px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background: #5A5A5C;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""
