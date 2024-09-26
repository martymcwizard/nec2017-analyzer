# pe/extract_text_pymupdf.py
# extract-text = "pe.extract_text_pymupdf:main"

'''
extracting text block by block since I have invested in using the start of the block method. Later I may need to switch to the page method and work line by line

#added to pyproject.toml
[tool.poetry.scripts]
extract-ref = "pe.extract_ref_by_page:main"
extract-text = "pe.extract_text_pymupdf:main"

poetry run extract-text data/input/nec_2017r.pdf data/output/latest_text_extract.txt --start-page 32 --end-page 50
'''

import fitz  # PyMuPDF
from itertools import islice
import re
from pathlib import Path
from collections import OrderedDict

# Compile the regex patterns with re.VERBOSE for readability
# removed 'chapter' because many sentences in the beginning start with that

# Consolidated regex patterns using named groups for clarity
pattern = re.compile(r'''
    ^(?P<full>(ARTICLE|FIGURE|TABLE))             # Full line keywords
    |
    ^(?P<exception>Exception)                     # Exception keyword
    |
    ^(?P<part_header>Part\s+[IVX]+\.?\s*)         # Part header with Roman numerals containing IVX
    |
    ^(?P<section>\d{2,3}\.\d{1,3}\b)              # Section numbers like xx.x, xx.xx, xx.xxx
    |
    ^\((?P<subsection>[A-Z])\)                    # Parentheses with capital letter (e.g., (A))
    |
    ^\((?P<parens_number>\d{1,2})\)               # Parentheses with one or two digits (e.g., (3), (12))
    |
    ^\((?P<subparagraph>[a-z])\)                  # Parentheses with lowercase letter (e.g., (a))
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

'''
The 2017 NEC does not have a consistent hierarchy scheme so building the paragraph references takes a bit of work. Level 4 is sometimes not used.
'''

# Initialize the reference
ref = OrderedDict()
# Define level hierarchy for comparison
level_hierarchy = ['section', 'subsection', 'paragraph', 'subparagraph', 'clause']


# Function to update the reference based on new levels
def update_reference(ref, level_key, level_type):
    """
    Update the reference structure and maintain the hierarchy (section, subsection, etc.).
    Clear all levels below the current one being updated based on level_type.
    """
    # print("\n--- Updating reference ---")
    # print(f"Current reference keys before update: {list(ref.keys())}")
    # print(f"Trying to update with: {level_key}, Level type: {level_type}")

    # If it's a new section, clear everything and start fresh
    if level_type == "section":
        ref.clear()

    # Find the index of the current level in the hierarchy
    current_level_idx = level_hierarchy.index(level_type)

    # Gather keys to delete if they belong to a lower level in the hierarchy
    keys_to_delete = []
    for key in ref.keys():
        key_level_idx = level_hierarchy.index(ref[key])
        # print(f"Comparing: '{key}' (level: {ref[key]}) with '{level_key}' (level: {level_type})")
        
        # If the current level is higher in the hierarchy, mark keys to delete
        if key_level_idx >= current_level_idx:
            keys_to_delete.append(key)

    # print(f"Keys to delete: {keys_to_delete}")

    # Now delete all keys that should be removed
    for key in keys_to_delete:
        del ref[key]

    # Add or update the current level with a unique key by appending the level type
    ref[f"{level_key}-{level_type}"] = level_type  # Store the key with level type for uniqueness

    # Construct the reference string with parentheses for all levels except the section level
    ref_str = ''.join(f"({key.split('-')[0]})" if idx != 0 else key.split('-')[0] for idx, key in enumerate(ref.keys()))
    #print("Assembled reference string:", reference_str)

    return ref, ref_str


'''
# Example usage:
ref = OrderedDict()
ref = update_reference(ref, "516.5", "section")
ref = update_reference(ref, "(D)", "subsection")
ref = update_reference(ref, "(5)", "paragraph")
ref = update_reference(ref, "(b)", "subparagraph")
ref = update_reference(ref, "(1)", "clause")  # Update for new clause
ref = update_reference(ref, "(E)", "subsection")  # New subsection, clearing the lower levels

'''


def extract_text(pdf_path, start_page=32, end_page=None):

    end_page = 681

    text_content = []
    reference = OrderedDict()

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count

    # Adjust end_page if necessary
    if end_page is None or end_page > total_pages:
        end_page = total_pages

    #for page_num, page in enumerate(islice(doc, 31, 900), start=32):

        

    # Process each page
    for page_num in range(start_page - 1, end_page):
        page_text = ''
        page = doc.load_page(page_num)

        blocks = page.get_text("blocks")

        for b in blocks[1:]:
            # Correctly unpack the block tuple
            x0, y0, x1, y1, text, block_no, block_type = b


            text = text.strip()  # Removes leading/trailing whitespace
            text = re.sub(r'^N\s+', '', text)  # Removes 'N ' at the start

            # Apply logic only to block 1
            if block_no == 1:
                # Normalize the en dash to a hyphen and remove leading/trailing whitespace
                text = text.replace('\u2013', '-').replace('\u2014', '-')  # Replace en and em dash with hyphen

                # Now check for the page number with the normalized hyphen
                page_number_match = re.search(r'70 -\d{2,3}', text)

                #print(f"what matched: {page_number_match}")
                if page_number_match:
                    # Append the formatted page number
                    page_text += "PAGE NUMBER " + page_number_match.group(0).replace(' ', '') + "\n"
                    #print(f"\n" + "PAGE NUMBER " + page_number_match.group(0))
                # Skip adding the redundant footer
                continue


            # Safely handle the case where match_patterns returns None
            group_name, result = match_patterns(text) or (None, None)
    
            if group_name == "full":
                #print(f"Full line match: {text}")
                # Replace newlines with spaces for these specific matches
                text = text.replace('\n', ' ').replace('\r', ' ')  # Replace both types of line breaks
                text = ' '.join(text.split())  # Remove any extra spaces caused by multiple line breaks
                print(f"result match returned: {result}")
                print(f"Full line match: {text}")
                page_text += text + "\n"

            elif group_name =="part_header":
                page_text += '.'.join(text.split('.')[:2]) + ".\n"

            elif group_name == "section":
                #print(f"Section match: {result}")
                reference, reference_str = update_reference(reference, result, group_name)
                
                #Do I actually have sections that cross two lines?  Shouldn't this be in full line match? or even up at the top before we do a group name? 
                text = text.replace('\n', ' ').replace('\r', ' ')  # Replace both types of line breaks
                text = ' '.join(text.split())  # Remove any extra spaces caused by multiple line breaks
                page_text += '.'.join(text.split('.')[:2]) + ".\n"

            elif group_name == "subsection":
                #print(f"subsection match: {result}")
                reference, reference_str = update_reference(reference, result, group_name)
                page_text += reference_str + "\n"
                text = text.replace('\n', ' ').replace('\r', ' ')  # Replace both types of line breaks
                text = ' '.join(text.split())  # Remove any extra spaces caused by multiple line breaks
                page_text += '.'.join(text.split('.')[:1]).strip() + ".\n" #these don't have a first period

            elif group_name == "subparagraph":
                #print(f"subparagraph match: {result}")
                reference, reference_str = update_reference(reference, result, group_name)
                page_text += reference_str + "\n"
                page_text += text

            elif group_name == "parens_number":
                
                period_count = text.count('.')
                colon_count = text.count(':')

                if period_count <= 1 and colon_count == 0:
                    #this is the second of (1)(1)
                    #print(f"clause match: {result}")
                    reference, reference_str = update_reference(reference, result, "clause")
                    page_text += reference_str + "\n"

                    # Remove the first weird line break (this is fine as-is)
                    text = text.replace('\n', '', 1)

                    # Ensure there is exactly one space after closing parentheses, removing any newlines or extra spaces
                    text = re.sub(r'\)\s*', ') ', text)

                    # Ensure that there is no newline immediately after the closing parenthesis
                    text = re.sub(r'\)\n+', ') ', text)

                    # Replace any remaining newlines and carriage returns with spaces
                    text = text.replace('\n', ' ').replace('\r', ' ')

                    # Remove any extra spaces caused by multiple line breaks or consecutive spaces
                    text = ' '.join(text.split()) + "\n"

                    # Remove the '!' artifact from the text
                    text = text.replace('! ', '')  # This will remove any occurrences of "! " in the text

                    page_text += text
                else:
                    #this is the first of (1)(1)
                    #print(f"paragraph match: {result}")
                    reference, reference_str = update_reference(reference, result, "paragraph")
                    page_text += reference_str + "\n"
                    # Ensure that there is no newline immediately after the closing parenthesis
                    text = re.sub(r'\)\n+', ') ', text)
                    page_text += '.'.join(text.split('.')[:1]) + ".\n" #these don't have a first period

            elif group_name == "exception":
                text = text.replace('\n', ' ').replace('\r', ' ')  # Replace both types of line breaks
                text = ' '.join(text.split())  # Remove any extra spaces caused by multiple line breaks
                text = text.replace('- ', '')  # This will remove any occurrences of "! " in the text
                page_text += text + "\n"

        # Clean page_text before appending to text_content
        page_text = page_text.rstrip("\n")  # Remove any trailing newlines
        text_content.append(page_text)  # Append without adding a newline

    return '\n'.join(text_content)

def main():
    # Define paths
    print(f"pe/extract_text_pymupdf.py program started")
    ## the letter r indicates that is my mac preview reprint
    pdf_path =  Path('data/input/nec_2017r.pdf')
    output_path = Path('data/output/nec_2017_extracted_.txt')

    # Extract text
    extracted_text = extract_text(pdf_path)

    # Write extracted text to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(extracted_text)

    print(f"Text successfully extracted to {output_path}")

if __name__ == "__main__":
    main()

'''
#as a block
from pathlib import Path
output_file = Path(output_path)
output_file.write_text(extracted_text, encoding='utf-8')

#multiple lines using a generator expression
with open(args.pdf_out_path, 'w', encoding='utf-8') as f:
    f.writelines(f'{match}\n' for match in matches)


'''