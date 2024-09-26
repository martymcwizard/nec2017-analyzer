#pe/extract_ref_by_page.py

'''
a new approach from o1-preview that focuse on extracting the page not block by block. I will use this to find all the hierarchical string references, unique and sort them.
"PDF Outline Parsing" is the name of the chat

Running the Script with Command-Line Arguments:

python extract_ref_by_page.py data/input/nec_2017r.pdf data/output/reference_strings.txt --start-page 32 --end-page 50

or, since I'm using poetry

poetry run python -m extract_ref_by_page data/input/nec_2017r.pdf data/output/reference_strings.txt --start-page 32 --end-page 50

or, since I didn't really understand the -m flag or Poetry :(

#added to pyproject.toml
[tool.poetry.scripts]
extract-ref = "pe.extract_ref_by_page:main"

poetry run extract-ref data/input/nec_2017r.pdf data/output/reference_strings.txt --start-page 32 --end-page 50


Using a Config File:

config.ini

[PDF]
start_page = 10
end_page = 50

#no, don't follow these instructions
Run the script 
python extract_references.py path/to/pdf.pdf --config config.ini

Processing All Pages:
python extract_references.py path/to/pdf.pdf
'''

import fitz  # PyMuPDF
import re
import argparse
import configparser

# Compile the regex pattern
pattern = re.compile(r'''
    (?:9[0-9]|[1-8][0-9]{2})   # Match numbers between 90 and 899
    \.\d{1,3}                  # Require a period followed by 1 to 3 digits (e.g., .118)
    [A-Z]?                     # Optionally match a single uppercase letter (e.g., A, D)
    (?:-[IVX]+)?               # Optionally match a hyphen followed by Roman numerals (e.g., -IV)
    (?:\([A-Za-z0-9]+\))+      # Require one or more groups of parentheses (e.g., (L), (D)(2))
    [a-z]?                     # Optionally match a single lowercase letter at the end
    (?:[:.])?                  # Optionally match a colon or period at the end
    ''', re.VERBOSE)



#my new boilerplate should be moved to another file and imported
def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract reference strings from a PDF.')
    parser.add_argument('pdf_in_path', help='Path and filename to to the PDF input file',default='data/input/nec_2017r.pdf')
    parser.add_argument('pdf_out_path', help='Path and filename to to the PDF output file',default='data/output/reference_strings.txt')
    parser.add_argument('--start-page', type=int, help='Start page number (1-based index)', default=1)
    parser.add_argument('--end-page', type=int, help='End page number (inclusive)')
    parser.add_argument('--config', help='Path to the config file', default='config.ini')
    return parser.parse_args()

def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    start_page = None
    end_page = None
    if 'PDF' in config:
        start_page = config['PDF'].getint('start_page', fallback=1)
        end_page = config['PDF'].getint('end_page', fallback=None)
    return start_page, end_page

def extract_references(pdf_path, start_page=1, end_page=None):
    # Open the PDF
    doc = fitz.open(pdf_path)
    total_pages = doc.page_count

    # Adjust end_page if necessary
    if end_page is None or end_page > total_pages:
        end_page = total_pages

    matches = set()  # Use a set to store unique matches

    # Process each page
    for page_num in range(start_page - 1, end_page):
        page = doc.load_page(page_num)
        text = page.get_text()

        # Find all matches on the current page
        page_matches = pattern.findall(text)
        matches.update(page_matches)

    # Close the document
    doc.close()

    # Remove any trailing periods or colons from each match and ensure uniqueness
    trimmed_matches = {match.rstrip('.:') for match in matches}

    # Sort the unique matches
    sorted_matches = sorted(trimmed_matches)

    return sorted_matches

def main():
    args = parse_arguments()

    # Read start_page and end_page from command-line arguments or config file
    start_page = args.start_page
    end_page = args.end_page

    if end_page is None:
        # Try to read from config file
        config_start_page, config_end_page = read_config(args.config)
        if config_end_page is not None:
            end_page = config_end_page

    # Extract and process matches
    matches = extract_references(args.pdf_in_path, start_page, end_page)

    # Write to the output file
    with open(args.pdf_out_path, 'w') as f:
        for match in matches:
            f.write(match + '\n')

if __name__ == '__main__':
    main()
