# src/main.py

# TODO: get a pdf file and extract text from it.

import sys
import pymupdf

doc = None

def open_file():
    filename = input("Enter file: ")
    doc = pymupdf.open(filename)
    return

def main():
    open_file()
    return

if __name__ == "__main__":
    main()

