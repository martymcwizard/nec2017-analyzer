# pe/extract_text_pymupdf.py

import fitz  # PyMuPDF
from itertools import islice
import re

# Compile the regex patterns with re.VERBOSE for readability
# removed 'chapter' because many sentences in the beginning start with that
pattern_full_line = re.compile(r'''
    ^(ARTICLE|FIGURE|TABLE)            # Match keywords at the start of the block
    |                                       # OR
    ^(Exception)
''', re.VERBOSE)

pattern_exception = re.compile(r'''
    ^Exception
''', re.VERBOSE))

pattern_part_header = re.compile(r'^Part [IVXLCDM]+\.\s', re.VERBOSE)

pattern_section = re.compile(r'''
    ^\d{2,3}\.\d{1,3}\b                    # Match xx.x, xx.xx, xx.xxx (e.g., 12.1, 12.34, 12.345)
''', re.VERBOSE)

pattern_parens_line = re.compile(r'''                                   
    ^\([A-Z]\)                            # Match (letter), single letter (e.g., (A))
    |
    ^\(\d{1,2}\)                          # Match (number), one or two digits (e.g., (3), (12))
    |
    ^\([a-z]\)                            # Match (letter), single letter (e.g., (a))                          
''', re.VERBOSE)

#for use later for 2,3.2 'Definitions'
#pattern_definitions



def extract_text_excluding_headers_footers(pdf_path):
    doc = fitz.open(pdf_path)
    text_content = []

    for page_num, page in enumerate(islice(doc, 32, 50), start=33):

        page_text = ''
        blocks = page.get_text("blocks")

        for b in blocks[1:]:
            # Correctly unpack the block tuple
            x0, y0, x1, y1, text, block_no, block_type = b

            # Apply logic only to block 1
            if block_no == 1:
                # Normalize the en dash to a hyphen and remove leading/trailing whitespace
                text = text.replace('\u2013', '-').replace('\u2014', '-')  # Replace en and em dash with hyphen
                text = text.strip()  # Remove leading/trailing whitespace

                # Now check for the page number with the normalized hyphen
                page_number_match = re.search(r'70 -\d{2,3}', text)

                #print(f"what matched: {page_number_match}")
                if page_number_match:
                    # Append the formatted page number
                    page_text += "PAGE NUMBER " + page_number_match.group(0) + "\n"
                    print(f"\n" + "PAGE NUMBER " + page_number_match.group(0))
                # Skip adding the redundant footer
                continue
    
            match_full = pattern_full_line.search(text)
            match_exception = pattern_exception.search(text)
            match_part_header = pattern_section.search(text)
            match_section = pattern_section.search(text)
            match_parens = pattern_parens_line.search(text)

            if match_full:
                print(f"Full line match: {match_full.group(0)}")
                # Replace newlines with spaces for these specific matches
                text = text.replace('\n', ' ').replace('\r', ' ')  # Replace both types of line breaks
                text = ' '.join(text.split())  # Remove any extra spaces caused by multiple line breaks
                page_text += text + "\n"

            if match_section:
                print(f"Section match: {match_section.group(0)}")
                text = text.replace('\n', ' ').replace('\r', ' ')  # Replace both types of line breaks
                text = ' '.join(text.split())  # Remove any extra spaces caused by multiple line breaks
                page_text += '.'.join(text.split('.')[:2]) + ".\n"

            elif match_parens:
                print(f"Part line match: {match_parens.group(0)}")
                #page_text += '.'.join(text.split('.')[:1]) + ".\n" #these don't have a first period
                page_text += text + "\n"

            #Let's see if we missed any small letter esctions because they are not at beginning of text block


            # we are no longer adding text unless we are looking for it specifically
            # page_text += text

        text_content.append(page_text)

    return '\n'.join(text_content)
