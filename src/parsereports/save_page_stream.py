"""
Этот скрипт демонстрирует, как можно получить доступ к потоку данных (content stream)
страницы. Раскодированный поток данных будет сохранён в текстовый файл.
"""
import pdf_storage
from parsereports.basicparsing import BasicPdfParser

INPUT_FILE_PATH = pdf_storage.table_report_file_path
PAGE_INDEX = 0
SAVED_FILE_PATH = "stream.txt"


def main():
    input_file_path = input("Введите путь к файлу PDF или нажмите Enter "
                            f"(по умолчанию будет прочитан файл \"{INPUT_FILE_PATH}\"): ") or INPUT_FILE_PATH
    page_index_str = input("Введите номер страницы, начиная с 0 "
                           f"(по умолчанию - {PAGE_INDEX}): ") or str(PAGE_INDEX)
    saved_file_path = input("Путь к файлу для сохранения потока данных "
                            f"(по умолчанию \"{SAVED_FILE_PATH}\"): ") or SAVED_FILE_PATH
    page_index = int(page_index_str)

    parser = BasicPdfParser(input_file_path)
    pdf_doc = parser.pq.doc
    page_dict = pdf_doc.catalog["Pages"].resolve()["Kids"][page_index].resolve()
    page_content_stream = page_dict["Contents"].resolve()
    parser.close()

    with open(saved_file_path, 'wb') as f:
        f.write(page_content_stream.data)
        f.flush()

    print("Сохранено в файл " + saved_file_path)


if __name__ == '__main__':
    main()
