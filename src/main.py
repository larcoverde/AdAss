# src/main.py

# TODO: get a pdf file and extract text from it.

import sys
import pymupdf

def open_file():
    filename = input("Enter file: ")
    doc = pymupdf.open(filename)
    return doc

def get_text_from_page(doc):
    for page in doc:
        text = page.get_text()
    return text

def main():
    doc = open_file()
    text = get_text_from_page(doc)
    return

if __name__ == "__main__":
    main()

