# Проверка содержимого PDF-файлов средствами Python и pdfminer

Этот проект создан как набор примеров кода для иллюстрации статьи
на [habr.com](https://habr.com).

*(Ссылки будут добавлены после публикации)*

## Настройка проекта

Настройка проекта необходима, только если вы хотите самостоятельно запускать примеры.

Проект проверялся с Python 3.12, однако должен быть совместим с версиями, начиная с 3.9.

Рекомендуется создать виртуальную среду для Python (в командной строке или с помощью IDE)
и в ней установить необходимые пакеты:

    python -m venv .venv
    source .venv/bin/activate
    # Для Windows: .venv\Scripts\activate.bat или .venv\Scripts\activate.ps1
    pip install -r requirements.txt

## Запуск скриптов

Все скрипты, в конце которых есть раздел ``__main__``, можно запускать по-отдельности.

Для создания отчётов **могут потребоваться шрифты из пакета Liberation**.
В Ubuntu они могут быть предустановлены из дистрибутива.
В других системах (включая Windows) они обычно устанавливаются вместе с LibreOffice.
Но их можно установить отдельно, или можно заменить их на любые другие доступные в системе
шрифты - для этого потребуется отредактировать пути в файле *makereports/fontstyles.py*.

Для запуска скриптов из командной строки без IDE потребуется вручную добавить
папку с кодом проекта в PYTHONPATH:

    export PYTHONPATH=$PYTHONPATH:(путь к папке src)
    # В Windows: SET PYTHONPATH=%PYTHONPATH%;(путь к папке src)

В случае, если скрипт зависит от результатов работы другого скрипта, это указывается
в описании в шапке файла. 

## Запуск тестов

Образцы тестов добавлены для демонстрации работы с page object.

Для их запуска:

- нужно сформировать отчёт, который будет тестироваться, используя скрипт
  *makereports/tablereport.py*,
- запустить команду *pytest* из папки проекта
- разумеется, также можно запускать тесты, используя функциональность IDE

## Состав проекта

*(Здесь перечислены только запускаемые скрипты и тесты)*

### pdf_storage

Не содержит запускаемых скриптов.
Сюда будут сохраняться создаваемые скриптами PDF-файлы.

### makereports

- *chartsreport.py* - создаёт отчёт с графиками, нужный для демонстрации обрезки объектов
- *figures.py* - создаёт PDF-файл с картинкой, который нужен в примерах с извлечением картинки
- *tablereport.py* - создаёт отчёт с табличными данными, нужный для многих примеров в проекте

### parsereports

- *tests* - папка с примерами тестов, запускаемыми через pytest
- *extract_metadata.py* - пример извлечения метаданных из документа
- *extract_picture.py* - пример извлечения растровой картинки
- *extract_picture_xobject.py* - пример извлечения растровой картинки для более старых версий pdfminer,
  и также скрипт демонстрирует доступ к ресурсам страницы
- *list_all_elements.py* - получение и вывод на консоль всех элементов страницы при помощи PDFQuery
- *list_all_elements_raw_pdfminer.py* - получение и вывод на консоль всех элементов страницы
  при помощи pdfminer без использования PDFQuery
- *save_page_stream.py* - сохраняет раскодированный поток данных страницы в виде текстового файла
- *time_measurement.py* - измеряет производительность парсинга для разных настроек парсера
