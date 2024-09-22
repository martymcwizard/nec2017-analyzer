# pe/extract_nec_text.py

import os
from .extract_text_pymupdf import extract_text_excluding_headers_footers

def main():
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(base_dir, 'data', 'input', 'nec_2017.pdf')
    output_path = os.path.join(base_dir, 'data', 'output', 'nec_2017_extracted_pymupdf.txt')

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Extract text
    extracted_text = extract_text_excluding_headers_footers(pdf_path)

    # Write extracted text to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(extracted_text)

    print(f"Text successfully extracted to {output_path}")

if __name__ == "__main__":
    main()
