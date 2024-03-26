"""
Renders a simple PDF document containing some simple graphics for demo.
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
        c.setLineWidth(10 * mm)
        c.setStrokeColorRGB(0, 0, 64)
        c.line(0, 0, self._page_width_pt, self._page_height_pt)

        x_centre = self._page_width_pt - 50 * mm
        y_centre_polygon = 100 * mm
        y_centre_circle = 50 * mm

        c.setLineWidth(0.5)
        c.setStrokeColorRGB(64, 0, 0)
        c.setFillColorRGB(128, 0, 0)
        c.circle(x_centre, y_centre_circle, 20, stroke=0, fill=1)

        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0, 64, 0)
        c.setFillColorRGB(0, 128, 0)
        polygon = c.beginPath()
        polygon.moveTo(x_centre - 10, y_centre_polygon + 25)
        for offset_x, offset_y in (
                (10, 25), (25, 10), (25, -10), (10, -25),
                (-10, -25), (-25, -10), (-25, 10), (-10, 25)
        ):
            polygon.lineTo(x_centre + offset_x, y_centre_polygon + offset_y)
        c.drawPath(polygon, stroke=0, fill=1)


def main():
    doc = PdfWithFiguresRenderer(
        image_file_path=pdf_storage.png_image,
        pdf_file_path=pdf_storage.figures_file_path,
        page_size=portrait(A4)
    )
    doc.render_and_save()


if __name__ == '__main__':
    main()
