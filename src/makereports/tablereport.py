"""
An example of a table report created with ReportLab.
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas

from src.makereports import PDF_STORAGE_PATH


def create_pdf(pdf_path) -> None:
    c = Canvas(
        filename=str(pdf_path),
        pagesize=A4,
    )

    c.drawString(200, 200, "Hello!")

    c.showPage()
    c.save()


if __name__ == '__main__':
    create_pdf(PDF_STORAGE_PATH / 'table_report.pdf')
    f = open(2)
