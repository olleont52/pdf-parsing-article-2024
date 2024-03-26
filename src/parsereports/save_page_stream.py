import pdf_storage
from parsereports.basicparsing import BasicPdfParser

INPUT_FILE_PATH = pdf_storage.table_report_file_path
PAGE_INDEX = 0
SAVED_FILE_PATH = "stream.txt"


def main():
    input_file_path = input(f"PDF file path (default=\"{INPUT_FILE_PATH}\"): ") or INPUT_FILE_PATH
    page_index_str = input(f"Page number, starting from 0 (default={PAGE_INDEX}): ") or str(PAGE_INDEX)
    page_index = int(page_index_str)
    saved_file_path = input(f"File name/path to save the page (default=\"{SAVED_FILE_PATH}\"): ") or SAVED_FILE_PATH

    parser = BasicPdfParser(input_file_path)
    pdf_doc = parser.pq.doc
    page_dict = pdf_doc.catalog["Pages"].resolve()["Kids"][page_index].resolve()
    page_content_stream = page_dict["Contents"].resolve()

    with open(saved_file_path, 'wb') as f:
        f.write(page_content_stream.data)
        f.flush()

    print("Saved " + saved_file_path)


if __name__ == '__main__':
    main()
