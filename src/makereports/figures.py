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
        c.setStrokeColorRGB(0, 192, 0)
        c.line(0, 0, self._page_width_pt, self._page_height_pt)


def main():
    doc = PdfWithFiguresRenderer(
        image_file_path=pdf_storage.png_image,
        pdf_file_path=pdf_storage.figures_file_path,
        page_size=portrait(A4)
    )
    doc.render_and_save()


if __name__ == '__main__':
    main()
