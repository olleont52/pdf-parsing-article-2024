from typing import Optional

from pdfminer.layout import LTPage
from pdfquery import PDFQuery
from pdfquery.pdfquery import LayoutElement


class BasicPdfParser:
    def __init__(self, pdf_file_path: str):
        self._file_path = pdf_file_path
        self._pq: Optional[PDFQuery] = None

    @property
    def pq(self) -> PDFQuery:
        if self._pq is None:
            self._pq = PDFQuery(self._file_path)
            self._pq.load()
        return self._pq

    def get_page_data(self, page_index: int) -> LTPage:
        return self.pq.pq(f"LTPage[page_index=\"{page_index}\"]")

    def get_all_page_elements(self, page_index: int) -> list[LayoutElement]:
        return self.pq.pq(f"LTPage[page_index=\"{page_index}\"] *")
