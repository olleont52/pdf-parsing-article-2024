from typing import Optional, Type, Iterable

import pdfminer.layout
from pdfminer.layout import LTPage, LTItem
from pdfquery import PDFQuery
from pdfquery.pdfquery import LayoutElement


def get_layout_types() -> list[Type[LTItem]]:
    all_classes = []
    for attr_name in dir(pdfminer.layout):
        if attr_name.startswith("LT") \
                and isinstance(element_class := getattr(pdfminer.layout, attr_name), type) \
                and issubclass(element_class, LTItem):
            all_classes.append(element_class)
    return all_classes


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

    def get_page_data(
            self,
            page_index: int
    ) -> LTPage:
        return self.pq.pq(f"LTPage[page_index=\"{page_index}\"]")

    def get_page_elements(
            self,
            page_index: int,
            element_class_names: Iterable[str]
    ) -> list[LayoutElement]:
        elements = []
        for class_name in element_class_names:
            elements.extend(self.pq.pq(f"LTPage[page_index=\"{page_index}\"] {class_name}"))
        return elements

    def get_all_page_elements(self, page_index: int) -> list[LayoutElement]:
        return self.get_page_elements(
            page_index=page_index,
            element_class_names=(t.__name__ for t in get_layout_types())
        )
