"""
Скрипт для создания табличного отчёта.
После запуска он создаст файл table_report.pdf в папке pdf_storage.
На примере этого отчёта в статье показано начало работы с pdfminer
и создание page object.
Также на примере этого отчёта работает образец тестов в parsereports/tests.py.
"""

import datetime as dt
import random
import string
from collections import OrderedDict, namedtuple
from dataclasses import dataclass, field

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics

import pdf_storage
from makereports.basereport import BaseReportRenderer, Rect
from makereports.fontstyles import FontStylesReportMixin, FONT_BOLD, FONT_REGULAR

_CellBorders = namedtuple("_CellBorders", "left right bottom top")


@dataclass
class TableData:
    num_cols: int
    num_rows: int
    row_headers: list[str] = field(default_factory=list)
    col_headers: list[str] = field(default_factory=list)
    data: list[list[str]] = field(default_factory=list)

    def get_full_table(self) -> list[list[str]]:
        table = [["", *self.col_headers]]
        table.extend([row_header, *row]
                     for row_header, row in zip(self.row_headers, self.data))
        return table


@dataclass
class TableReportData:
    title: str = ""
    patient_name: str = ""
    patient_age: str = ""
    clinician_name: str = ""
    table_data: TableData | None = None
    date_created: dt.datetime = field(default_factory=dt.datetime.now)


class TableReportDataGenerator:
    def __init__(self):
        self.data = TableReportData()

    def create_random_data(
            self,
            num_cols: int | None = None,
            num_rows: int | None = None
    ) -> None:
        data = self.data
        data.title = "Данные наблюдений"
        data.patient_name = "Иванов И.И."
        data.patient_age = f"{random.randint(18, 120)} лет"
        data.clinician_name = "Петров П.П."

        num_cols = num_cols or 8
        num_rows = num_rows or 24
        data.table_data = TableData(
            num_cols=num_cols,
            num_rows=num_rows,
            row_headers=[f"{h:02d}:00" for h in range(num_rows)]
        )
        data.table_data.col_headers = ["".join(random.choices(string.ascii_uppercase, k=3))
                                       for _ in range(num_cols)]
        data.table_data.data = [[("%02.2f" % random.uniform(-999.99, 999.99))
                                 for _ in range(num_cols)] for _ in range(num_rows)]


class TableReportRenderer(BaseReportRenderer, FontStylesReportMixin):
    def __init__(
            self,
            report_data: TableReportData,
            pdf_file_path: str,
            page_size: tuple[float, float]
    ):
        BaseReportRenderer.__init__(
            self,
            pdf_file_path=pdf_file_path,
            page_size=page_size
        )

        self._data = report_data
        if report_data.table_data is None:
            raise ValueError("Table data must be initialized")

        self._side_panel_width_ratio = 0.3
        self._table_cell_width_pt = 20 * mm
        self._table_cell_height_pt = 7 * mm

    def _draw_content(self) -> None:
        self._register_fonts()
        self._clip_page_margins()
        self._draw_side_panel()
        table_position = self._calculate_table_position()
        self._draw_data_table(table_position)

    def _draw_side_panel(self) -> None:
        title_base_line_distance_pt = 20 * mm
        title_font_size = 18
        data_line_distance_pt = 10 * mm
        data_column_width_pt = 40 * mm
        data_font_size = 11

        displayed_data = OrderedDict()
        displayed_data["Дата"] = self._data.date_created.strftime("%d/%m/%Y %H:%M")
        displayed_data["Ф.И.О. пациента"] = str(self._data.patient_name)
        displayed_data["Возраст"] = str(self._data.patient_age)
        displayed_data["Ф.И.О. врача"] = str(self._data.clinician_name)

        c = self._canvas
        # Draw title
        c.setFont(FONT_BOLD, title_font_size)
        y_baseline = self._page_height_pt - self._page_margin_pt - title_base_line_distance_pt
        c.drawString(x=self._page_margin_pt, y=y_baseline, text=self._data.title)

        # Draw data headers
        y = y_baseline
        c.setFont(FONT_BOLD, data_font_size)
        for text in displayed_data.keys():
            y -= data_line_distance_pt
            c.drawString(x=self._page_margin_pt, y=y, text=text)

        # Draw data values
        y = y_baseline
        c.setFont(FONT_REGULAR, data_font_size)
        for text in displayed_data.values():
            y -= data_line_distance_pt
            c.drawString(x=self._page_margin_pt + data_column_width_pt, y=y, text=text)

    def _calculate_table_position(self) -> Rect:
        view_box = self._calculate_page_view_box()
        side_panel_width_pt = self._side_panel_width_ratio * (view_box.x1 - view_box.x0)
        table_x0 = view_box.x0 + side_panel_width_pt

        table_height_pt = self._table_cell_height_pt * (len(self._data.table_data.data) + 1)
        table_vdistance_from_margin_pt = (view_box.y1 - view_box.y0 - table_height_pt) / 2

        return Rect(
            x0=table_x0,
            y0=view_box.y0 + table_vdistance_from_margin_pt,
            x1=view_box.x1,
            y1=view_box.y1 - table_vdistance_from_margin_pt
        )

    def _draw_data_table(
            self,
            table_position: Rect
    ) -> None:
        self._add_clipping_rectangle(table_position)

        # border style for all cells
        self._canvas.setStrokeColorRGB(0, 0, 0)
        self._canvas.setLineWidth(0.1)

        full_table_data = self._data.table_data.get_full_table()
        for row_index, row in enumerate(full_table_data):
            cell_top = table_position.y1 - self._table_cell_height_pt * row_index

            for col_index, value in enumerate(row):
                cell_left = table_position.x0 + self._table_cell_width_pt * col_index

                self._draw_cell(
                    position=Rect(
                        x0=cell_left,
                        y0=cell_top - self._table_cell_height_pt,
                        x1=cell_left + self._table_cell_width_pt,
                        y1=cell_top
                    ),
                    text=str(value),
                    font=FONT_BOLD if 0 in (row_index, col_index) else FONT_REGULAR,
                    borders=_CellBorders(
                        left=(col_index != 0),
                        right=False,
                        bottom=False,
                        top=(row_index != 0)
                    )
                )

    @staticmethod
    def _calculate_centered_text_position(
            rect: Rect,
            font: str,
            font_size: int,
            text: str
    ) -> float:
        rect_width = rect.x1 - rect.x0
        text_width = pdfmetrics.stringWidth(text, font, font_size)
        return rect.x0 + (rect_width - text_width) / 2

    def _draw_cell(
            self,
            position: Rect,
            text: str,
            font: str,
            borders: _CellBorders
    ) -> None:
        c = self._canvas
        # Draw text
        font_size = 10
        c.setFont(font, font_size)
        c.drawString(
            x=self._calculate_centered_text_position(
                rect=position,
                font=font,
                font_size=font_size,
                text=text
            ),
            y=position.y0 + 2 * mm,
            text=text
        )
        # Draw borders: only actually used cases are added
        if borders.top:
            c.line(position.x0, position.y1, position.x1, position.y1)
        if borders.left:
            c.line(position.x0, position.y0, position.x0, position.y1)


def main():
    data_generator = TableReportDataGenerator()
    data_generator.create_random_data()
    doc = TableReportRenderer(
        report_data=data_generator.data,
        pdf_file_path=pdf_storage.table_report_file_path,
        page_size=landscape(A4)
    )
    doc.render_and_save()


if __name__ == '__main__':
    main()
