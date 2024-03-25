from parsereports.basicparsing import BasicPdfParser
from pdf_storage import table_report_file_path


def main():
    parser = BasicPdfParser(table_report_file_path)
    all_elements = parser.get_all_page_elements(0)
    for element in all_elements:
        print(element)


if __name__ == '__main__':
    main()
