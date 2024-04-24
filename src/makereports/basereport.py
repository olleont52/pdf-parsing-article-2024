"""
Этот модуль содержит определения, общие для отчётов разных типов.
"""

from abc import ABC, abstractmethod
from collections import namedtuple

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

Rect = namedtuple("Rect", "x0 y0 x1 y1")


class BaseReportRenderer(ABC):
    """
    Базовый класс для создания отчётов с помощью reportlab.
    """

    def __init__(
            self,
            pdf_file_path: str,
            page_size: tuple[float, float]
    ):
        self._canvas = Canvas(
            filename=pdf_file_path,
            pagesize=page_size
        )
        self._page_width_pt, self._page_height_pt = page_size
        self._page_margin_pt = 10 * mm

    def render_and_save(self) -> None:
        """
        Шаблонный метод для создания одностраничного отчёта.

        Все операции по наполнению страницы в подклассах
        добавляются в метод _draw_content.
        """
        self._draw_content()
        c = self._canvas
        c.showPage()
        c.save()

    @abstractmethod
    def _draw_content(self) -> None:
        raise NotImplementedError()

    def _add_clipping_rectangle(self, rect: Rect):
        c = self._canvas
        clip_rect = c.beginPath()
        clip_rect.rect(
            x=rect.x0,
            y=rect.y0,
            width=rect.x1 - rect.x0,
            height=rect.y1 - rect.y0
        )
        c.clipPath(aPath=clip_rect, stroke=0, fill=0)

    def _calculate_page_view_box(self) -> Rect:
        margin = self._page_margin_pt
        return Rect(
            x0=margin,
            y0=margin,
            x1=self._page_width_pt - margin,
            y1=self._page_height_pt - margin
        )

    def _clip_page_margins(self):
        view_box = self._calculate_page_view_box()
        self._add_clipping_rectangle(view_box)
