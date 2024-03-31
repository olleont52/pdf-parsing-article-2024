import time
from typing import Any

import pdf_storage
from parsereports.basicparsing import BasicPdfParser

INPUT_FILE_PATH = pdf_storage.table_report_file_path
NUM_MEASUREMENTS = 5


def measure_opening_time(pq_params: dict[str, Any]) -> float:
    parsing_times = []
    for i in range(1, NUM_MEASUREMENTS + 1):
        parser = BasicPdfParser(INPUT_FILE_PATH, pq_params)

        start = time.monotonic()
        parser.init_pq()
        stop = time.monotonic()
        parsing_times.append(stop - start)
        print(f"{i} / {NUM_MEASUREMENTS}: {stop - start:.03f} s")

        parser.close()

    return sum(parsing_times) / len(parsing_times)


FULL_PARAMS = dict(
    merge_tags=('LTChar', 'LTAnno'),
    round_floats=True,
    round_digits=3,
    normalize_spaces=True,
    resort=True,
    # Description of "laparams" can be found in class pdfminer.layout.LAParams
    laparams=dict(
        line_overlap=0.5,
        char_margin=2.0,
        line_margin=0.5,
        word_margin=0.1,
        boxes_flow=0.5,
        detect_vertical=True,
        all_texts=True
    )
)

FAST_PARAMS = dict(
    round_floats=False,
    normalize_spaces=False,
    resort=False,
    laparams=dict(
        boxes_flow=None,
        detect_vertical=False,
        all_texts=True
    )
)


def main():
    average_time = measure_opening_time({})
    print(f"{average_time:.03f} s - with default parameters")
    average_time = measure_opening_time(FULL_PARAMS)
    print(f"{average_time:.03f} s - with full analysis")
    average_time = measure_opening_time(FAST_PARAMS)
    print(f"{average_time:.03f} s - with reduced analysis")


if __name__ == '__main__':
    main()
