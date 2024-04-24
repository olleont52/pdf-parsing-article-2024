"""
Этот модуль содержит общие определения для добавления шрифтов в отчёты.
Для успешного создания отчётов должен быть установлен шрифт TTF LiberationSans
(обычно входит в дистрибутив LibreOffice).
Если у вас нет таких шрифтов, или отличается системный путь к ним,
можно добавить собственные варианты в словарь в этом модуле.
"""

import os
from itertools import chain

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_REGULAR = "Regular"
FONT_BOLD = "Bold"

_FONT_PATHS = {
    FONT_BOLD: [
        # TODO: Add Linux paths, too, and test
        r"C:\Windows\Fonts\LiberationSans-Bold.ttf",
    ],
    FONT_REGULAR: [
        r"C:\Windows\Fonts\LiberationSans-Regular.ttf",
    ]
}


class FontStylesReportMixin:
    @staticmethod
    def _find_font_files() -> dict[str, str]:
        font_file_paths = _FONT_PATHS
        verified_fonts = {}
        for font_type, font_locations in font_file_paths.items():
            for file_path in font_locations:
                if os.path.isfile(file_path):
                    verified_fonts[font_type] = file_path

        if set(font_file_paths.keys()) != set(verified_fonts.keys()):
            raise EnvironmentError(
                "Необходимые шрифты для создания отчёта не были обнаружены в системе. "
                f"Поиск производился по пути: {list(chain(*font_file_paths.values()))}. "
                f"Вы можете добавить собственные пути к шрифтам в модуль {os.path.abspath(__file__)}"
            )
        return verified_fonts

    def _register_fonts(self) -> None:
        fonts = self._find_font_files()
        for font_type, file_path in fonts.items():
            pdfmetrics.registerFont(TTFont(font_type, file_path))
