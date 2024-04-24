"""
Пример с извлечением метаданных из документа.
Используется файл отчёта, созданный скриптом makereports/tablereport.py.
"""

import pdf_storage
from parsereports.basicparsing import BasicPdfParser

INPUT_FILE_PATH = pdf_storage.table_report_file_path
PAGE_INDEX = 0


def main():
    parser = BasicPdfParser(INPUT_FILE_PATH)
    metadata = parser.pq.doc.info[0]
    print(metadata)
    parser.close()


if __name__ == '__main__':
    main()
