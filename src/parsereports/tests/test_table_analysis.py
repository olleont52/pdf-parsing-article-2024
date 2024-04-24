"""
Тесты для демонстрации работы с page object.
Для работы тестов необходимо заранее создать файл table_report.pdf,
запустив скрипт makereports/tablereport.py.
Чтобы выполнить тесты, достаточно запустить команду pytest в папке проекта.
"""

from itertools import chain
from typing import Generator

import pytest

import pdf_storage
from parsereports.basicparsing import BasicPdfParser
from parsereports.tablereport_analysis import TableReportAnalyzer, TableReportPage

INPUT_FILE_PATH = pdf_storage.table_report_file_path


@pytest.fixture(scope="session")
def table_page() -> Generator[TableReportPage, None, None]:
    analyzer = TableReportAnalyzer()
    parser = BasicPdfParser(INPUT_FILE_PATH)
    analyzer.analyze(parser.get_all_page_elements(0))
    yield analyzer.page_object
    parser.close()


def test_legend_labels(table_page):
    label_texts = [field.label.text.rstrip() for field in table_page.legend.fields]
    assert label_texts == ["Дата", "Ф.И.О. пациента", "Возраст", "Ф.И.О. врача"]


def test_table_cells_are_not_empty(table_page):
    assert table_page.table.num_rows > 1, "Таблица не должна быть пустой"
    assert table_page.table.num_cols > 1, "Таблица не должна быть пустой"
    cells = table_page.table.cells
    assert cells[0][0] is None, "В верхней левой ячейке не должно быть текста"
    assert all((element is not None) for element in cells[0][1:]), \
        "Заголовки колонок должны быть заполнены"
    assert all((element is not None) for element in chain(*cells[1:])), \
        "Все ячейки в строках с данными должны быть заполнены"
