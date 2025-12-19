from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXT = {".pdf"}


@dataclass(frozen=True)
class ScannedFile:
    """Результат сканирования файла книги."""

    path: str
    size_bytes: int
    format: str


class Scanner:
    """Сканер папок для поиска поддерживаемых файлов книг."""

    def scan_file(self, path: str) -> ScannedFile | None:
        """Проверяет один файл и возвращает описание, если формат поддерживается.

        Args:
            path: Путь к файлу.

        Returns:
            ScannedFile или None.
        """
        p = Path(path)
        if not p.exists() or not p.is_file():
            return None

        ext = p.suffix.lower()
        if ext not in SUPPORTED_EXT:
            return None

        try:
            size = p.stat().st_size
        except OSError:
            return None

        return ScannedFile(path=str(p), size_bytes=size, format=ext.lstrip("."))

    def scan_folder(self, folder: str) -> list[ScannedFile]:
        """Сканирует папку рекурсивно и возвращает поддерживаемые файлы.

        Args:
            folder: Путь к папке.

        Returns:
            Список ScannedFile.
        """
        root = Path(folder)
        if not root.exists() or not root.is_dir():
            return []

        out: list[ScannedFile] = []
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXT:
                sf = self.scan_file(str(p))
                if sf:
                    out.append(sf)
        return out
