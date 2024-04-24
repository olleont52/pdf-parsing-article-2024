"""
Скрипт для создания простейшего отчёта с рисунком.
После запуска он создаст файл figures.pdf в папке pdf_storage.
На примере этого отчёта в статье показано извлечение картинки.

Кроме того, в отчёт добавлены многоугольник и окружность.
При анализе с помощью pdfminer можно увидеть, что и многоугольник, и окружность
представляют собой кривые, нарисованные по набору точек, и отличаются только
типами фрагментов кривой: прямая или Безье.
"""

from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm

import pdf_storage
from makereports.basereport import BaseReportRenderer


class PdfWithFiguresRenderer(BaseReportRenderer):
    def __init__(
            self,
            image_file_path: str,
            pdf_file_path: str,
            page_size: tuple[float, float]
    ):
        BaseReportRenderer.__init__(
            self,
            pdf_file_path=pdf_file_path,
            page_size=page_size
        )
        self._image_file_path = image_file_path

    def _draw_content(self) -> None:
        c = self._canvas
        c.drawImage(
            image=self._image_file_path,
            x=50 * mm,
            y=self._page_height_pt - 100 * mm,
            height=50 * mm,
            preserveAspectRatio=True
        )

        x_centre = self._page_width_pt - 50 * mm
        y_centre_polygon = self._page_height_pt - 100 * mm
        y_centre_circle = self._page_height_pt - 50 * mm

        c.setLineWidth(2)
        c.setStrokeColorRGB(0.5, 0, 0)
        c.setFillColorRGB(1.0, 0, 0)
        c.circle(x_centre, y_centre_circle, 25, stroke=1, fill=1)

        c.setLineWidth(2)
        c.setStrokeColorRGB(0, 0.5, 0)
        c.setFillColorRGB(0, 1.0, 0)
        polygon = c.beginPath()
        polygon.moveTo(x_centre - 10, y_centre_polygon + 25)
        for offset_x, offset_y in (
                (10, 25), (25, 10), (25, -10), (10, -25),
                (-10, -25), (-25, -10), (-25, 10), (-10, 25)
        ):
            polygon.lineTo(x_centre + offset_x, y_centre_polygon + offset_y)
        c.drawPath(polygon, stroke=1, fill=1)


def main():
    doc = PdfWithFiguresRenderer(
        image_file_path=pdf_storage.png_image,
        pdf_file_path=pdf_storage.figures_file_path,
        page_size=portrait(A4)
    )
    doc.render_and_save()


if __name__ == '__main__':
    main()
