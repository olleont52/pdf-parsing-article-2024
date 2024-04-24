"""
Пример с извлечением растрового изображения из документа.
Используется файл отчёта, созданный скриптом makereports/figures.py.
Полученное изображение будет показано с помощью программы просмотра,
настроенной по умолчанию в системе.
"""

from PIL import Image
from pdfminer.pdftypes import PDFStream
from pdfquery import PDFQuery
from pdfquery.pdfquery import LayoutElement

import pdf_storage
from parsereports.basicparsing import BasicPdfParser

INPUT_FILE_PATH = pdf_storage.figures_file_path
PAGE_INDEX = 0


def find_first_image_element(pq: PDFQuery, page_index: int) -> LayoutElement:
    # Ищем первый элемент LTImage с помощью запроса к PDFQuery.
    # В используемом отчёте figures.pdf такой элемент только один.
    return pq.pq(f"LTPage[page_index=\"{page_index}\"] LTImage")[0]


def decode_image(image_element: LayoutElement, image_data: PDFStream) -> Image.Image:
    # В этом примере показан только пример работы с изображением,
    # сохранённым в режиме RGB, по 8 бит на каждый компонент цвета.
    # Режим сохранения изображений в ваших документах может отличаться.
    # Все варианты можно найти в спецификации PDF (https://pdfa.org/).
    # Соответствующие варианты для библиотеки PIL можно подобрать из списка:
    # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
    color_spaces = [str(literal.name) for literal in image_element.layout.colorspace]
    if color_spaces == ["DeviceRGB"] and image_element.layout.bits == 8:
        PIL_color_mode = "RGB"
    else:
        raise ValueError("Цветовой режим не поддерживается этим скриптом")

    width, height = image_data.attrs["Width"], image_data.attrs["Height"]
    return Image.frombytes(PIL_color_mode, (width, height), image_data.get_data())


def main():
    parser = BasicPdfParser(INPUT_FILE_PATH)

    image_element = find_first_image_element(parser.pq, PAGE_INDEX)
    image_data = image_element.layout.stream
    width, height = image_data.attrs["Width"], image_data.attrs["Height"]
    print(f"Получены данные изображения размером {len(image_data.get_data())} байт, "
          f"размер в пикселях: {width}x{height}")

    image = decode_image(image_element, image_data)
    parser.close()
    image.show()


if __name__ == '__main__':
    main()
