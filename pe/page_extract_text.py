'''
a new approach from o1-preview that focuse on extracting the page not block by block. I will use this to find all the hierarchical string references, unique and sort them.
"PDF Outline Parsing" is the name of the chat
'''
import fitz  # PyMuPDF
import re
import argparse
import configparser
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract text from PDF with hierarchical structure.')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--start-page', type=int, help='Start page number (1-based index)')
    parser.add_argument('--end-page', type=int, help='End page number (inclusive)')
    parser.add_argument('--config', help='Path to the config file', default='config.ini')
    return parser.parse_args()

def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    start_page = None
    end_page = None
    if 'PDF' in config:
        start_page = config['PDF'].getint('start_page', fallback=None)
        end_page = config['PDF'].getint('end_page', fallback=None)
    return start_page, end_page


def extract_text(pdf_path, start_page=None, end_page=None):
    doc = fitz.open(pdf_path)
    total_pages = doc.page_count

    # Set defaults if start_page or end_page is None
    if start_page is None:
        start_page = 1  # Pages are 1-based index
    if end_page is None or end_page > total_pages:
        end_page = total_pages

    # Adjust for zero-based index in PyMuPDF
    start_page_index = start_page - 1
    end_page_index = end_page

    text_content = []

    for page_num, page in enumerate(doc[start_page_index:end_page_index], start=start_page):
        page_text_full = page.get_text()
        page_text_full = page_text_full.replace('\u2013', '-').replace('\u2014', '-').strip()
        page_text = process_page_text(page_text_full)
        text_content.append(page_text)

    return '\n'.join(text_content)

def process_page_text(page_text_full):
    page_text = ''
    lines = page_text_full.split('\n')
    hierarchy = []
    section_text = ''
    previous_marker_type = None

    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            # If you want to preserve paragraph breaks, add an empty line
            section_text += '\n'
            continue
        # Find all pattern matches in the line
        matches = match_patterns(line)
        if matches:
            # If there's accumulated text from the previous section, add it
            if section_text.strip():
                page_text += section_text.rstrip() + "\n"
                section_text = ''
            for group_name, result, position in matches:
                current_marker_type = group_name
                current_marker_value = result

                # Update hierarchy based on the current marker
                hierarchy = update_hierarchy(hierarchy, current_marker_type, current_marker_value)

                # Build the numbering string
                numbering = '.'.join(hierarchy)

                # Append the numbering to the page text
                page_text += numbering + "\n"

                # Reset section text since we've moved to a new section
                section_text = ''
                # Update the previous marker type
                previous_marker_type = current_marker_type
        else:
            # Accumulate text within the current section, preserving line breaks
            section_text += line + '\n'

    # After processing all lines, add any remaining text
    if section_text.strip():
        page_text += section_text.rstrip() + "\n"
    return page_text
