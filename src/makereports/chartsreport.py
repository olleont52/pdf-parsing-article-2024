"""
Скрипт для создания простейшего отчёта с графиками.
После запуска он создаст файл chart_report.pdf в папке pdf_storage.
На примере этого отчёта в статье показан эффект обрезки по контуру.
"""

import random
from dataclasses import dataclass, field
from math import sin, pi

from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics

import pdf_storage
from makereports.basereport import BaseReportRenderer, Rect
from makereports.fontstyles import FontStylesReportMixin, FONT_BOLD


@dataclass
class LineChartData:
    title: str = ""
    clip_chart: bool = True

    x_min: float = 0.0
    x_max: float = 1000.0

    y_min: float = 0.0
    y_max: float = 100.0

    line_color: tuple[float, float, float] = (0, 0, 0)
    line_width_pt: float = 2.0
    line_points: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class ChartReportData:
    charts: list[LineChartData] = field(default_factory=list)


class ChartsReportDataGenerator:
    def __init__(self):
        self.data = ChartReportData()

    def create_random_data(self, clip_charts: bool) -> None:
        self.data.charts.append(self.create_chart_data_1())
        self.data.charts.append(self.create_chart_data_2())
        for chart in self.data.charts:
            chart.clip_chart = clip_charts

    @staticmethod
    def create_chart_data_1() -> LineChartData:
        chart = LineChartData(
            title="Waves",
            line_color=(0.75, 0.25, 0)
        )
        num_intervals = 500
        step_x = (chart.x_max - chart.x_min) / num_intervals
        long_half_period = chart.x_max - chart.x_min
        short_half_period = long_half_period / 20

        chart.y_min = -10.0
        chart.y_max = 10.0
        max_amplitude = 20

        for i in range(num_intervals + 1):
            x = chart.x_min + i * step_x
            y = sin(x / short_half_period * pi) * sin(x / long_half_period * pi) * max_amplitude
            chart.line_points.append((x, y))

        return chart

    @staticmethod
    def create_chart_data_2() -> LineChartData:
        chart = LineChartData(
            title="Random",
            line_color=(0.25, 0.75, 0)
        )
        num_intervals = 20
        step_x = (chart.x_max - chart.x_min) / num_intervals
        for i in range(num_intervals + 1):
            chart.line_points.append((
                chart.x_min + i * step_x,
                random.uniform(chart.y_min, chart.y_max)
            ))

        return chart


class ChartsReportRenderer(BaseReportRenderer, FontStylesReportMixin):
    def __init__(
            self,
            report_data: ChartReportData,
            pdf_file_path: str,
            page_size: tuple[float, float]
    ):
        BaseReportRenderer.__init__(
            self,
            pdf_file_path=pdf_file_path,
            page_size=page_size
        )

        self._data = report_data

    def _draw_content(self) -> None:
        self._register_fonts()
        self._clip_page_margins()

        chart_margin_pt = 30 * mm
        chart_height_pt = 40 * mm
        current_chart_upper_border_y = self._page_height_pt - self._page_margin_pt - chart_margin_pt
        for chart_data in self._data.charts:
            chart_rect = Rect(
                x0=self._page_margin_pt + chart_margin_pt,
                y0=current_chart_upper_border_y - chart_height_pt,
                x1=self._page_width_pt - self._page_margin_pt - chart_margin_pt,
                y1=current_chart_upper_border_y
            )
            self._draw_line_chart(chart_data, chart_rect)
            current_chart_upper_border_y -= chart_height_pt + chart_margin_pt

    def _draw_line_chart(self, chart_data: LineChartData, chart_rect: Rect) -> None:
        c = self._canvas

        if chart_data.title:
            self._draw_chart_title(
                text=chart_data.title,
                x_centre_pt=(chart_rect.x0 + chart_rect.x1) / 2,
                y_baseline_pt=chart_rect.y1 + 2.0 * mm
            )

        # Save state before clipping the chart
        c.saveState()
        if chart_data.clip_chart:
            self._add_clipping_rectangle(chart_rect)
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(0.5)

        # Draw border
        c.rect(
            x=chart_rect.x0,
            y=chart_rect.y0,
            width=chart_rect.x1 - chart_rect.x0,
            height=chart_rect.y1 - chart_rect.y0,
            stroke=1, fill=0
        )

        # Draw line
        if pts := chart_data.line_points:
            x_scale = (chart_rect.x1 - chart_rect.x0) / (chart_data.x_max - chart_data.x_min)
            x_zero_pt = (0 - chart_data.x_min) * x_scale + chart_rect.x0
            y_scale = (chart_rect.y1 - chart_rect.y0) / (chart_data.y_max - chart_data.y_min)
            y_zero_pt = (0 - chart_data.y_min) * y_scale + chart_rect.y0

            def _scale(point: tuple[float, float]) -> tuple[float, float]:
                x, y = point
                return (x * x_scale + x_zero_pt,
                        y * y_scale + y_zero_pt)

            c.setStrokeColorRGB(*chart_data.line_color)
            c.setLineWidth(chart_data.line_width_pt)
            path = c.beginPath()
            path.moveTo(*_scale(pts[0]))
            for pt in pts[1:]:
                path.lineTo(*_scale(pt))
            c.drawPath(path, stroke=1, fill=0)

        # Restore graphic state without clipping
        c.restoreState()

    def _draw_chart_title(self, text: str, x_centre_pt: float, y_baseline_pt: float) -> None:
        c = self._canvas
        c.setFont(FONT_BOLD, 16)
        title_width = pdfmetrics.stringWidth(text, FONT_BOLD, 16)
        c.drawString(
            x=x_centre_pt - title_width / 2,
            y=y_baseline_pt,
            text=text
        )


def main():
    answer = input("Обрезать графики по границам координатной сетки? (y/n, default=y): ") or "y"
    data_generator = ChartsReportDataGenerator()
    data_generator.create_random_data(clip_charts=(answer.lower() == "y"))
    doc = ChartsReportRenderer(
        report_data=data_generator.data,
        pdf_file_path=pdf_storage.charts_report_file_path,
        page_size=portrait(A4),
    )
    doc.render_and_save()


if __name__ == '__main__':
    main()
