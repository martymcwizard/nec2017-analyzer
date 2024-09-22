# pe/extract_text.py

from pdfminer.high_level import extract_text
import os

def extract_text_from_pdf(pdf_path, txt_output_path):
    """
    Extracts text from a PDF file and writes it to a text file.

    :param pdf_path: Path to the input PDF file.
    :param txt_output_path: Path to the output text file.
    """
    try:
        text = extract_text(pdf_path)
        with open(txt_output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text successfully extracted to {txt_output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
