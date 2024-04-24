"""
Этот скрипт распечатывает иерархию всех объектов с первой страницы документа.
Объекты извлекаются с помощью pdfminer без использования PDFQuery.
Скрипт создан как пример прямой настройки pdfminer.
По умолчанию используется файл отчёта, созданный скриптом makereports/tablereport.py,
но можно ввести путь до любого документа.
"""

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
    input_file_path = input("Введите путь к файлу PDF или нажмите Enter "
                            f"(по умолчанию будет прочитан файл \"{INPUT_FILE_PATH}\"): ") or INPUT_FILE_PATH

    with open(input_file_path, 'rb') as f:
        # парсер, который будет разбирать основную структуру файла
        parser = PDFParser(f)
        # документ, в который парсер будет складывать всю информацию
        doc = PDFDocument(parser)
        parser.set_document(doc)

        # менеджер ресурсов
        resources_mgr = PDFResourceManager()
        # "устройство" для внутреннего рендеринга объектов
        # (в pdfminer есть несколько типов устройств - например, есть такое,
        # которое сохраняет только текст без свойств графики)
        device = PDFPageAggregator(resources_mgr, laparams=LAParams())
        # интерпретатор потока данных, который будет "рисовать"
        # в контексте созданного выше устройства
        interpreter = PDFPageInterpreter(resources_mgr, device)

        # получаем первую страницу
        pages_iter = PDFPage.create_pages(doc)
        page0 = next(pages_iter)
        # запускаем на ней интерпретатор и забираем с устройства отрендеренные объекты
        interpreter.process_page(page0)
        page_layout = device.get_result()
        # распечатываем все объекты рекурсивно
        print_layout(page_layout)


if __name__ == '__main__':
    main()
