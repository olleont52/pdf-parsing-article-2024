from PIL import Image
from pdfminer.pdftypes import PDFStream
from pdfquery import PDFQuery
from pdfquery.pdfquery import LayoutElement

import pdf_storage
from parsereports.basicparsing import BasicPdfParser

INPUT_FILE_PATH = pdf_storage.figures_file_path
PAGE_INDEX = 0
SAVED_FILE_PATH = "image.png"


def find_first_image_element(pq: PDFQuery, page_index: int) -> LayoutElement:
    return pq.pq(f"LTPage[page_index=\"{page_index}\"] LTImage")[0]


def extract_image_data(pq: PDFQuery, page_index: int, image_element: LayoutElement) -> PDFStream:
    # Extract the whole PDF page object with resources
    page = pq.doc.catalog["Pages"].resolve()["Kids"][page_index].resolve()
    # Find the attached resource object by the image name
    return page["Resources"]["XObject"][image_element.layout.name].resolve()


def decode_image(image_element: LayoutElement, image_data: PDFStream) -> Image.Image:
    # An image may be saved inside the document in various color modes, see the PDF specification.
    # Only a simple 8-bit RGB color space for displays is demonstrated in this example.
    color_spaces = [str(literal.name) for literal in image_element.layout.colorspace]
    if color_spaces == ["DeviceRGB"] and image_element.layout.bits == 8:
        PIL_color_mode = "RGB"
    else:
        raise ValueError("Unexpected image color mode")

    width, height = image_data.attrs["Width"], image_data.attrs["Height"]
    return Image.frombytes(PIL_color_mode, (width, height), image_data.get_data())


def main():
    parser = BasicPdfParser(INPUT_FILE_PATH)

    image_element = find_first_image_element(parser.pq, PAGE_INDEX)
    print("Found an image with the resource name:", image_element.layout.name)

    image_data = extract_image_data(parser.pq, PAGE_INDEX, image_element)
    width, height = image_data.attrs["Width"], image_data.attrs["Height"]
    print(f"Resolved a byte stream with data length {len(image_data.get_data())}, "
          f"image size in pixels: {width}x{height}")

    image = decode_image(image_element, image_data)
    parser.close()
    image.show()


if __name__ == '__main__':
    main()
