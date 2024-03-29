import random
from dataclasses import dataclass, field
from math import sin, pi

from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm

import pdf_storage
from makereports.basereport import BaseReportRenderer
from makereports.fontstyles import FontStylesReportMixin

_GRAPHS_MARGIN = 40 * mm


@dataclass
class LineGraphData:
    width_pt: float
    height_pt: float
    clip_graph: bool = True

    x_min: float = 0.0
    x_max: float = 1000.0

    y_min: float = 0.0
    y_max: float = 100.0

    line_color: tuple[int, int, int] = (0, 0, 0)
    line_width_pt: float = 2.0
    line_points: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class GraphReportData:
    graphs: list[LineGraphData] = field(default_factory=list)


class GraphReportDataGenerator:
    def __init__(self):
        self.data = GraphReportData()

    def create_random_data(
            self,
            page_size: tuple[float, float],
            clip_graphs: bool
    ) -> None:
        self.data.graphs.append(self.create_graph_1(
            width_pt=page_size[0] - 2 * _GRAPHS_MARGIN,
            height_pt=30 * mm,
            clip_graph=clip_graphs
        ))
        self.data.graphs.append(self.create_graph_2(
            width_pt=page_size[0] - 2 * _GRAPHS_MARGIN,
            height_pt=40 * mm,
            clip_graph=clip_graphs
        ))

    @staticmethod
    def create_graph_1(
            width_pt: float,
            height_pt: float,
            clip_graph: bool
    ) -> LineGraphData:
        graph = LineGraphData(
            width_pt=width_pt,
            height_pt=height_pt,
            clip_graph=clip_graph,
            line_color=(160, 0, 0)
        )
        num_intervals = 500
        step_x = (graph.x_max - graph.x_min) / num_intervals
        long_half_period = graph.x_max - graph.x_min
        short_half_period = long_half_period / 20

        graph.y_min = -10.0
        graph.y_max = 10.0
        max_amplitude = 30

        for i in range(num_intervals + 1):
            x = graph.x_min + i * step_x
            y = sin(x / short_half_period * pi) * sin(x / long_half_period * pi) * max_amplitude
            graph.line_points.append((x, y))

        return graph

    @staticmethod
    def create_graph_2(
            width_pt: float,
            height_pt: float,
            clip_graph: bool
    ) -> LineGraphData:
        graph = LineGraphData(
            width_pt=width_pt,
            height_pt=height_pt,
            clip_graph=clip_graph,
            line_color=(0, 160, 0)
        )
        num_intervals = 20
        step_x = (graph.x_max - graph.x_min) / num_intervals
        for i in range(num_intervals + 1):
            graph.line_points.append((
                graph.x_min + i * step_x,
                random.uniform(graph.y_min, graph.y_max)
            ))

        return graph


class GraphReportRenderer(BaseReportRenderer, FontStylesReportMixin):
    def __init__(
            self,
            report_data: GraphReportData,
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
        # TODO
        pass


def main():
    page_size = A4
    data_generator = GraphReportDataGenerator()
    data_generator.create_random_data(page_size, clip_graphs=True)
    doc = GraphReportRenderer(
        report_data=data_generator.data,
        pdf_file_path=pdf_storage.table_report_file_path,
        page_size=portrait(page_size),
    )
    doc.render_and_save()


if __name__ == '__main__':
    main()
