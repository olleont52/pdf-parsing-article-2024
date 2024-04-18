from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import Optional, Iterable

from pdfquery.pdfquery import LayoutElement
from reportlab.lib.units import mm


@dataclass
class TableLegendField:
    label: Optional[LayoutElement]
    value: Optional[LayoutElement]


@dataclass
class TableReportLegend:
    title: Optional[LayoutElement] = None
    fields: list[TableLegendField] = field(default_factory=list)


@dataclass
class TableReportTable:
    table_rect: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    vertical_lines: list[LayoutElement] = field(default_factory=list)
    vertical_lines_by_x: dict[float, list[LayoutElement]] = \
        field(default_factory=lambda: defaultdict(list))
    horizontal_lines: list[LayoutElement] = field(default_factory=list)
    horizontal_lines_by_y: dict[float, list[LayoutElement]] = \
        field(default_factory=lambda: defaultdict(list))
    # Cells are organized: first index - by rows, second index - by columns
    cells: list[list[Optional[LayoutElement]]] = field(default_factory=list)

    @property
    def num_rows(self) -> int:
        return len(self.cells)

    @property
    def num_cols(self) -> int:
        return len(self.cells[0]) if self.cells else 0


@dataclass
class TableReportPage:
    legend = TableReportLegend()
    table = TableReportTable()
    all_elements: list[LayoutElement] = field(default_factory=list)


class TableReportAnalyzer:
    def __init__(self):
        self.page_object = TableReportPage()

        self._all_elements: list[LayoutElement] = []
        self._all_text_elements: list[LayoutElement] = []

    def analyze(self, page_elements: Iterable[LayoutElement]) -> None:
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

        # Loop by rows: find texts between the upper and the lower border in the row
        for row_top, row_bottom in zip(
                cell_borders_y_positions[:-1],
                cell_borders_y_positions[1:]
        ):
            row: list[Optional[LayoutElement]] = [None] * row_length
            table.cells.append(row)

            # Loop by columns: find texts between the left and the right border in the column
            for col_index, (col_left, col_right) in enumerate(zip(
                    cell_borders_x_positions[:-1],
                    cell_borders_x_positions[1:])
            ):
                # Search for a fitting text element
                # (This algorithm should be re-written with lower complexity,
                # but here we keep it as simple as possible to make it more obvious when reading)
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

        # Sort text lines vertically from top to bottom
        legend_elements.sort(key=lambda element: round(-element.layout.y0))

        # Take the first text as title
        legend = self.page_object.legend
        if legend_elements:
            legend.title = legend_elements.pop(0)

        # Find pairs of label and value, allowing a discrepancy +/- 1 mm for the text vertical position
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
