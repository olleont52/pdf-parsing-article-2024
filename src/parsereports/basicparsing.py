"""
Этот модуль содержит общие определения для парсинга PDF,
которые используются в разных примерах.
"""

from typing import Optional, Any, Dict

from pdfquery import PDFQuery
from pdfquery.pdfquery import LayoutElement


class BasicPdfParser:
    """
    Класс-обёртка для парсера PDF с помощью PDFQuery.
    """

    def __init__(
            self,
            pdf_file_path: str,
            pq_params: Optional[Dict[str, Any]] = None
    ):
        """

        :param pdf_file_path: Путь к документу.
        :param pq_params: Параметры конструктора PDFQuery,
            см. возможные параметры в документации класса PDFQuery.
        """
        self._file_path = pdf_file_path
        self._pq: Optional[PDFQuery] = None
        self._pq_params = pq_params or {}

    @property
    def pq(self) -> PDFQuery:
        """
        :return: Объект PDFQuery, готовый к работе.
            После завершения работы необходимо вызвать close().
        """
        self.init_pq()
        return self._pq

    def init_pq(self) -> None:
        if self._pq is None:
            self._pq = PDFQuery(self._file_path, **self._pq_params)
            self._pq.load()

    def close(self) -> None:
        """
        Закрывает документ.
        Необходимо делать это явно, т.к. PDFQuery всегда держит файл открытым для чтения.
        """
        pq = self._pq
        if pq is not None and pq.file is not None:
            pq.file.close()

    def get_all_page_elements(self, page_index: int) -> list[LayoutElement]:
        """
        :param page_index: Номер страницы, начиная с 0.
        :return: Список всех объектов, отрендеренных на странице.
        """
        return self.pq.pq(f"LTPage[page_index=\"{page_index}\"] *")
