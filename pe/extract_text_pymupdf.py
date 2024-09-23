# pe/extract_text_pymupdf.py

import fitz  # PyMuPDF
from itertools import islice
import re

# Compile the regex patterns with re.VERBOSE for readability
# removed 'chapter' because many sentences in the beginning start with that
# Consolidated regex patterns using named groups for clarity
pattern = re.compile(r'''
    ^(?P<full>(ARTICLE|FIGURE|TABLE))            # Full line keywords
    |
    ^(?P<exception>Exception)                    # Exception keyword
    |
    ^(?P<part_header>Part [IVXLCDM]+\.\s)        # Part header with Roman numerals
    |
    ^(?P<section>\d{2,3}\.\d{1,3}\b)             # Section numbers like xx.x, xx.xx, xx.xxx
    |
    ^\((?P<parens_upper>[A-Z])\)                       # Parentheses with capital letter (e.g., (A))
    |
    ^\((?P<parens_number>\d{1,2})\)              # Parentheses with one or two digits (e.g., (3), (12))
    |
    ^\((?P<parens_lower>[a-z])\)                 # Parentheses with lowercase letter (e.g., (a))
''', re.VERBOSE)


#for use later for 2,3.2 'Definitions'
#pattern_definitions
#parens_isolated

'''
There's a more concise way to return the matched group without repeating yourself. Since you only want to return the first matched group (if any), you can use Python’s groupdict() method, which returns a dictionary of all named groups and their matches. You can then iterate over this dictionary and return the first non-None match.
* match.groupdict(): This method returns a dictionary where the keys are the names of the groups and the values are the matched content (or None if the group didn’t match).
* Looping through groupdict(): You loop over the dictionary, and as soon as you find a non-None value, you return it.
* This way, you avoid manually checking each group and repeating the logic.
'''
def match_patterns(text):
    match = pattern.search(text)
    
    if match:
        # Iterate through all named groups and return the first match
        for group_name, group_value in match.groupdict().items():
            if group_value:
                return group_name, group_value
    
    # Return None if no match is found
    return None

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text_content = []

    for page_num, page in enumerate(islice(doc, 31, 100), start=32):

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

            # Safely handle the case where match_patterns returns None
            group_name, result = match_patterns(text) or (None, None)
    
            if group_name == "full":
                print(f"Full line match: {result}")
                # Replace newlines with spaces for these specific matches
                text = text.replace('\n', ' ').replace('\r', ' ')  # Replace both types of line breaks
                text = ' '.join(text.split())  # Remove any extra spaces caused by multiple line breaks
                page_text += text + "\n"

            elif group_name =="part_header":
                page_text += '.'.join(text.split('.')[:2]) + ".\n"

            elif group_name == "section":
                print(f"Section match: {result}")
                text = text.replace('\n', ' ').replace('\r', ' ')  # Replace both types of line breaks
                text = ' '.join(text.split())  # Remove any extra spaces caused by multiple line breaks
                page_text += '.'.join(text.split('.')[:2]) + ".\n"

            elif group_name == "parens_upper":
                print(f"Part line match: {result}")
                page_text += '.'.join(text.split('.')[:1]) + ".\n" #these don't have a first period

            elif group_name == "parens_lower":
                print(f"Part line match: {result}")
                #page_text += '.'.join(text.split('.')[:1]) + ".\n" #these don't have a first period
                page_text += text

            elif group_name == "parens_number":
                print(f"Part line match: {result}")
                period_count = text.count('.')
                colon_count = text.count(':')

                if period_count <= 1 and colon_count == 0:
                    text = text.replace('\n', '', 1)
                    #print(text)
                    page_text += text
                else:
                    page_text += '.'.join(text.split('.')[:1]) + ".\n" #these don't have a first period

            elif group_name == "exception":
                page_text += text
                

        text_content.append(page_text)

    return '\n'.join(text_content)
