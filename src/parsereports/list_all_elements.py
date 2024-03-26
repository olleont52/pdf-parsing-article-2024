from pdfquery.pdfquery import LayoutElement

import pdf_storage
from parsereports.basicparsing import BasicPdfParser

# INPUT_FILE_PATH = pdf_storage.figures_file_path
INPUT_FILE_PATH = pdf_storage.table_report_file_path


def format_bbox(bbox: tuple[float, float, float, float]) -> str:
    return f"({bbox[0]:.3f}, {bbox[1]:.3f}, {bbox[2]:.3f}, {bbox[3]:.3f})"


def describe_element(element: LayoutElement) -> str:
    if not hasattr(element, "layout"):
        return repr(element)

    layout = element.layout
    text = f"{element.tag} ({format_bbox(layout.bbox)})"

    if hasattr(element, "text"):
        text += f", text: \"{element.text}\""

    for layout_property in (
            "name",
            "fill",
            "non_stroking_color",
            "stroke",
            "stroking_color",
            "linewidth",
            "pts",
            "original_path"
    ):
        if (value := getattr(layout, layout_property, None)) is not None:
            text += f", {layout_property}: {value}"
            if layout_property == "pts":
                text += f" ({len(value)} points)"

    return text


def main():
    input_file_path = input(f"PDF file path (default=\"{INPUT_FILE_PATH}\"): ") or INPUT_FILE_PATH

    parser = BasicPdfParser(input_file_path)
    all_elements = parser.get_all_page_elements(0)
    for element in all_elements:
        print(describe_element(element))


if __name__ == '__main__':
    main()
