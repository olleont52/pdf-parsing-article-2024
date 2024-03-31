from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTPage, LTItem, LTContainer
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

import pdf_storage

INPUT_FILE_PATH = pdf_storage.table_report_file_path


def print_item(indent: str, layout_item: LTItem) -> None:
    line_start = indent + " "
    if hasattr(layout_item, "get_text"):
        line_start += f"\"{layout_item.get_text().rstrip()}\" "
    print(f"{line_start}{layout_item}")

    if isinstance(layout_item, LTContainer):
        for child in layout_item:
            print_item(indent + "--", child)


def print_layout(page_layout: LTPage) -> None:
    print_item('', page_layout)


def main():
    input_file_path = input(f"PDF file path (default=\"{INPUT_FILE_PATH}\"): ") or INPUT_FILE_PATH
    with open(input_file_path, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        parser.set_document(doc)

        resources_mgr = PDFResourceManager()
        device = PDFPageAggregator(resources_mgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(resources_mgr, device)

        pages_iter = PDFPage.create_pages(doc)
        page0 = next(pages_iter)
        interpreter.process_page(page0)
        page_layout = device.get_result()
        print_layout(page_layout)


if __name__ == '__main__':
    main()
