import sys

from PySide6.QtWidgets import QApplication

from app.db import Database
from app.services.settings_service import SettingsService
from app.ui.main_window import MainWindow
from app.ui.theme import apply_dark_palette, apply_light_palette, get_theme_stylesheet

# ----------------------------------------------------------------------
# Точка входа
# ----------------------------------------------------------------------


def main() -> int:
    app = QApplication(sys.argv)

    # База данных
    db = Database()
    db.initialize()

    settings = SettingsService(db)
    theme = settings.get("theme", "dark")

    # Применяем тему (палитра + стили)
    if theme == "light":
        apply_light_palette(app)
    else:
        apply_dark_palette(app)

    app.setStyleSheet(get_theme_stylesheet(theme))

    # Главное окно
    window = MainWindow(db=db)
    window.resize(1200, 720)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
