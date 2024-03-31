from typing import Optional, Any, Dict

from pdfminer.layout import LTPage
from pdfquery import PDFQuery
from pdfquery.pdfquery import LayoutElement


class BasicPdfParser:
    def __init__(
            self,
            pdf_file_path: str,
            pq_params: Optional[Dict[str, Any]] = None
    ):
        self._file_path = pdf_file_path
        self._pq: Optional[PDFQuery] = None
        self._pq_params = pq_params or {}

    @property
    def pq(self) -> PDFQuery:
        self.init_pq()
        return self._pq

    def init_pq(self) -> None:
        if self._pq is None:
            self._pq = PDFQuery(self._file_path, **self._pq_params)
            self._pq.load()

    def close(self) -> None:
        pq = self._pq
        if pq is not None and pq.file is not None:
            pq.file.close()

    def get_page_data(self, page_index: int) -> LTPage:
        return self.pq.pq(f"LTPage[page_index=\"{page_index}\"]")

    def get_all_page_elements(self, page_index: int) -> list[LayoutElement]:
        return self.pq.pq(f"LTPage[page_index=\"{page_index}\"] *")
