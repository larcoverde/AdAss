# src/main.py

# TODO: Implement a chunk_text() function that splits extracted PDF text into overlapping chunks.

import pymupdf

def open_file():
    """Request a PDF file from user and open it."""
    filename = input("Enter file: ")
    doc = pymupdf.open(filename)
    return doc

def get_text_from_page(doc):
    """Extract text from provided PDF file."""
    for page in doc:
        text = page.get_text()
    return text

def main():
    doc = open_file()
    text = get_text_from_page(doc)
    return

if __name__ == "__main__":
    main()

