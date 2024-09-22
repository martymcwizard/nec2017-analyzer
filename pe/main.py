# pe/main.py

import os
from extract_text import extract_text_from_pdf

def main():
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(base_dir, 'data', 'input', 'nec_2017.pdf')
    txt_output_path = os.path.join(base_dir, 'data', 'output', 'nec_2017.txt')

    # Ensure output directory exists
    os.makedirs(os.path.dirname(txt_output_path), exist_ok=True)

    # Extract text
    extract_text_from_pdf(pdf_path, txt_output_path)

if __name__ == "__main__":
    main()
