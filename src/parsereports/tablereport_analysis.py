"""
Этот модуль не является запускаемым скриптом.
Он содержит определения для анализа страницы табличного отчёта
и пример формирования page object.
Анализ рассчитан на отчёты, которые создаются скриптом makereports/tablereport.py.
Примеры использования этих определений можно увидеть в тестах:
parsereports/tests/test_able_analysis.py.
"""
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import Optional, Iterable

from pdfquery.pdfquery import LayoutElement
from reportlab.lib.units import mm


@dataclass
class TableLegendField:
    """
    Элемент справочных сведений в левой части отчёта, включающий метку и значение.
    """
    label: Optional[LayoutElement]
    value: Optional[LayoutElement]


@dataclass
class TableReportLegend:
    """
    Распознанные элементы справочных сведений в левой части отчёта.
    """
    title: Optional[LayoutElement] = None
    fields: list[TableLegendField] = field(default_factory=list)


@dataclass
class TableReportTable:
    """
    Распознанные элементы из табличной части отчёта.
    """
    table_rect: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    vertical_lines: list[LayoutElement] = field(default_factory=list)
    vertical_lines_by_x: dict[float, list[LayoutElement]] = \
        field(default_factory=lambda: defaultdict(list))
    horizontal_lines: list[LayoutElement] = field(default_factory=list)
    horizontal_lines_by_y: dict[float, list[LayoutElement]] = \
        field(default_factory=lambda: defaultdict(list))
    # Список ячеек: первый индекс - номер строки, второй - номер столбца
    cells: list[list[Optional[LayoutElement]]] = field(default_factory=list)

    @property
    def num_rows(self) -> int:
        return len(self.cells)

    @property
    def num_cols(self) -> int:
        return len(self.cells[0]) if self.cells else 0


@dataclass
class TableReportPage:
    """
    Корневой объект page object.

    Можно делать все поля неизменяемыми, чтобы тесты случайно
    не исказили результаты анализа, но для этого нужно усложнять код.
    Для примера хватит простейшего варианта.
    """
    legend = TableReportLegend()
    table = TableReportTable()
    all_elements: list[LayoutElement] = field(default_factory=list)


class TableReportAnalyzer:
    """
    Анализатор, принимающий объекты со страницы
    и создающий page object класса TableReportPage.

    Код анализаторов может содержать сложную логику распознавания элементов,
    которая не нужна для последующей работы с элементами.
    Поэтому разумно отделять код анализатора от самого page object.
    """
    def __init__(self):
        """
        Конструктор только создаёт анализатор с пустым page object.
        """
        self.page_object = TableReportPage()

        self._all_elements: list[LayoutElement] = []
        self._all_text_elements: list[LayoutElement] = []

    def analyze(self, page_elements: Iterable[LayoutElement]) -> None:
        """
        После вызова analyze из поля page_object можно забирать результат.

        :param page_elements: Набор объектов со страницы,
            полученный от PDFQuery.
        """
        self._all_elements = list(page_elements)
        self.page_object.all_elements = self._all_elements
        self._detect_text_elements()
        self._detect_table_lines()
        self._detect_table_rectangle()
        self._detect_table_cell_contents()
        self._detect_legend_elements()

    def _detect_text_elements(self) -> None:
        self._all_text_elements = [element for element in self._all_elements
                                   if "Text" in element.tag
                                   and getattr(element, "text", None)]

    def _detect_table_lines(self) -> None:
        table = self.page_object.table
        table.horizontal_lines = [element for element in self._all_elements
                                  if element.tag == "LTLine"
                                  and element.layout.y0 == element.layout.y1]
        table.vertical_lines = [element for element in self._all_elements
                                if element.tag == "LTLine"
                                and element.layout.x0 == element.layout.x1]
        for line in table.horizontal_lines:
            table.horizontal_lines_by_y[line.layout.y0].append(line)
        for line in table.vertical_lines:
            table.vertical_lines_by_x[line.layout.x0].append(line)

    def _detect_table_rectangle(self) -> None:
        min_x, min_y, max_x, max_y = 1e5, 1e5, 0.0, 0.0
        table = self.page_object.table
        for line in chain(table.horizontal_lines, table.vertical_lines):
            min_x = min(min_x, line.layout.x0)
            max_x = max(max_x, line.layout.x1)
            min_y = min(min_y, line.layout.y0)
            max_y = max(max_y, line.layout.y1)
        table.table_rect = (min_x, min_y, max_x, max_y)

    def _detect_table_cell_contents(self) -> None:
        table = self.page_object.table
        cell_borders_x_positions = [table.table_rect[0],
                                    *sorted(table.vertical_lines_by_x.keys()),
                                    table.table_rect[2]]
        cell_borders_y_positions = [table.table_rect[3],
                                    *sorted(table.horizontal_lines_by_y.keys(), reverse=True),
                                    table.table_rect[1]]
        row_length = len(cell_borders_x_positions) - 1

        # Цикл по строкам: ищем все тексты между верхней и нижней границами строки.
        for row_top, row_bottom in zip(
                cell_borders_y_positions[:-1],
                cell_borders_y_positions[1:]
        ):
            row: list[Optional[LayoutElement]] = [None] * row_length
            table.cells.append(row)

            # Цикл по колонкам: ищем текст между левой и правой границами колонки.
            for col_index, (col_left, col_right) in enumerate(zip(
                    cell_borders_x_positions[:-1],
                    cell_borders_x_positions[1:])
            ):
                # Ищем подходящий текстовый элемент
                # (В теории можно уменьшить алгоритмическую сложность перебора
                # за счёт предварительных сортировок, но для примера мы оставляем
                # наиболее очевидный код, который легче прочитать сверху вниз)
                for element in self._all_text_elements:
                    if (
                            element.layout.x0 >= col_left and
                            element.layout.x1 <= col_right and
                            element.layout.y0 >= row_bottom and
                            element.layout.y1 <= row_top
                    ):
                        row[col_index] = element
                        break

    def _detect_legend_elements(self) -> None:
        table_left_border = self.page_object.table.table_rect[0]
        legend_elements = [element for element in self._all_text_elements
                           if element.layout.x0 < table_left_border]

        # Упорядочиваем строки текста сверху вниз
        legend_elements.sort(key=lambda element: round(-element.layout.y0))

        # Певую строку считаем заголовком
        legend = self.page_object.legend
        if legend_elements:
            legend.title = legend_elements.pop(0)

        # Находим пары меток и значений.
        # Допускается отклонение +/- 1 мм по вертикали,
        # т.к. границы текста могут зависеть от размера символов.
        max_vertical_shift = 1 * mm
        while legend_elements:
            label = legend_elements.pop(0)
            value = None
            if (
                    legend_elements and
                    (value := legend_elements[0]) is not None and
                    abs(label.layout.y0 - value.layout.y0) <= max_vertical_shift
            ):
                legend_elements.pop(0)

            if label.layout.x0 > value.layout.x0:
                label, value = value, label
            legend.fields.append(TableLegendField(label, value))
