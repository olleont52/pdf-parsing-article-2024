from pathlib import Path

PDF_STORAGE_PATH = Path(__file__).resolve().parent

png_image = str(PDF_STORAGE_PATH / 'little_lamb.png')
table_report_file_path = str(PDF_STORAGE_PATH / 'table_report.pdf')
charts_report_file_path = str(PDF_STORAGE_PATH / 'charts_report.pdf')
figures_file_path = str(PDF_STORAGE_PATH / 'figures.pdf')
