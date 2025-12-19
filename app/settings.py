from pathlib import Path


def get_app_dir() -> Path:
    """Возвращает директорию приложения в профиле пользователя.

    Returns:
        Путь к директории данных приложения.
    """
    base = Path.home() / ".bookvault"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_db_path() -> Path:
    """Возвращает путь к SQLite базе данных.

    Returns:
        Путь к файлу БД.
    """
    return get_app_dir() / "bookvault.sqlite3"
