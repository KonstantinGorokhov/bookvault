from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import fitz  # PyMuPDF


@dataclass(frozen=True)
class PdfMatch:
    """Совпадение поиска внутри PDF."""

    page_index: int
    rects: List[Tuple[float, float, float, float]]


class PdfService:
    """Сервис работы с PDF: метаданные, превью, поиск."""

    def extract_metadata(self, path: str) -> dict:
        """Извлекает метаданные PDF.

        Args:
            path: Путь к PDF.

        Returns:
            Словарь метаданных PDF.
        """
        doc = fitz.open(path)
        meta = doc.metadata or {}
        doc.close()
        return meta

    def render_page_png_bytes(
        self, path: str, page_index: int, max_width: int = 560
    ) -> Tuple[bytes, float]:
        """Рендерит страницу PDF в PNG (bytes), масштабируя по ширине.

        Args:
            path: Путь к PDF.
            page_index: Индекс страницы (0-based).
            max_width: Максимальная ширина изображения.

        Returns:
            Кортеж (PNG bytes, масштаб).

        Raises:
            ValueError: Если индекс страницы некорректный.
        """
        doc = fitz.open(path)
        if page_index < 0 or page_index >= doc.page_count:
            doc.close()
            raise ValueError("Некорректный индекс страницы.")

        page = doc.load_page(page_index)
        rect = page.rect

        scale = (max_width / rect.width) if rect.width > 0 else 1.0
        mat = fitz.Matrix(scale, scale)

        pix = page.get_pixmap(matrix=mat, alpha=False)
        data = pix.tobytes("png")
        doc.close()
        return data, scale

    def search(self, path: str, query: str, max_hits: int = 200) -> list[PdfMatch]:
        """Ищет строку во всём PDF без учета регистра.

        В PyMuPDF поиск `page.search_for()` по умолчанию выполняется без учета регистра.
        Если в будущем будет нужна нормализация сложнее (морфология, токенизация) —
        её следует реализовывать отдельным индексом.

        Args:
            path: Путь к PDF.
            query: Искомая строка.
            max_hits: Максимальное число совпадений.

        Returns:
            Список PdfMatch (страница + прямоугольники совпадений).
        """
        q = (query or "").strip()
        if not q:
            return []

        doc = fitz.open(path)
        results: list[PdfMatch] = []
        total = 0

        for i in range(doc.page_count):
            page = doc.load_page(i)

            # Важно: без учета регистра по умолчанию.
            rects = page.search_for(q)

            if rects:
                packed = [(r.x0, r.y0, r.x1, r.y1) for r in rects]
                results.append(PdfMatch(page_index=i, rects=packed))
                total += len(packed)
                if total >= max_hits:
                    break

        doc.close()
        return results
