from __future__ import annotations

from typing import List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel


class ImagePreview(QLabel):
    """Виджет предпросмотра изображения PDF-страницы с подсветкой совпадений."""

    def __init__(self) -> None:
        """Инициализирует виджет."""
        super().__init__()
        self.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setMinimumWidth(560)
        self.setObjectName("Preview")

        self._pix: QPixmap | None = None
        self._highlights: List[Tuple[float, float, float, float]] = []
        self._scale: float = 1.0

        # Локальный QSS только для превью (qt-material остаётся основой)
        self.setStyleSheet(
            """
            #Preview {
                border-radius: 10px;
                padding: 10px;
            }
            """
        )

    def set_png_bytes(
        self,
        png_bytes: bytes,
        highlights: List[Tuple[float, float, float, float]] | None = None,
        scale: float = 1.0,
    ) -> None:
        """Устанавливает PNG и подсветки.

        Args:
            png_bytes: PNG bytes.
            highlights: Прямоугольники подсветки (в оригинальных координатах страницы).
            scale: Масштаб рендеринга страницы.
        """
        img = QImage.fromData(png_bytes, "PNG")
        self._pix = QPixmap.fromImage(img)
        self._highlights = highlights or []
        self._scale = scale
        self.setPixmap(self._draw())

    def clear(self) -> None:
        """Очищает предпросмотр."""
        self._pix = None
        self._highlights = []
        self._scale = 1.0
        self.setText("Предпросмотр недоступен")

    def _draw(self) -> QPixmap:
        """Рисует подсветку поверх изображения.

        Returns:
            QPixmap с подсветкой.
        """
        if self._pix is None:
            return QPixmap()

        out = QPixmap(self._pix)
        painter = QPainter(out)

        # Желтый цвет для подчеркивания, как в PDF-ридерах
        pen = QPen(Qt.GlobalColor.yellow)
        pen.setWidth(3)
        painter.setPen(pen)

        # Масштабируем координаты и рисуем подчеркивание
        for x0, y0, x1, y1 in self._highlights:
            # Применяем масштаб к координатам
            scaled_x0 = int(x0 * self._scale)
            scaled_y1 = int(y1 * self._scale)
            scaled_x1 = int(x1 * self._scale)

            # Рисуем линию под текстом (используем y1 - нижнюю границу)
            painter.drawLine(scaled_x0, scaled_y1, scaled_x1, scaled_y1)

        painter.end()
        return out
