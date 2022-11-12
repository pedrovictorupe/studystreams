#!/usr/bin/env python3

from io import TextIOWrapper
import os, sys, random
from string import ascii_letters
from typing import OrderedDict
from PyPDF4 import PdfFileReader
import curses

# Curses window
_win = None

def main():
    _win = curses.initscr()

    inputPath: str = sys.argv[1] + '/'
    dirs: list = None
    if os.path.basename(sys.argv[0]) == "studystreams.py":
        dirs = [inputPath + file for file in os.listdir(inputPath) if os.path.isdir(inputPath + file)]
    else:
        __win.addstr("Error: Either this script wasn't executed as a standalone exe or this was renamed", file=sys.stderr)

    pages_by_file: OrderedDict = OrderedDict()
    for path in dirs:
        for pdf_file in [file for file in os.listdir(path) if file.endswith('.pdf')]:
            if f"{pdf_file}.sav" not in os.listdir(path):
                with open(f"{path}/{pdf_file}", 'rb') as fstream:
                    initialize_sav_files(fstream)
            else:
                with open(f"{path}/{pdf_file}.sav", 'r') as sav:
                    pages_by_file[f"{os.path.basename(path)}/{pdf_file}.sav"] = FileInfo(f"{os.path.basename(path)}/{pdf_file}.sav", sav.readlines())

    # Activate/inactivate subjects
    subjects = [SubjectItem(subject_name) for subject_name in set([os.path.basename(dirname).capitalize() for dirname in dirs])]
    subjects[0].isCursorOn = True
    while(True):
        for subject in subjects:
            _win.addstr(str(subject) + '\n')

        _win.addstr("\nUse WASD and the spacebar to select which subjects to interate over then press C to confirm selection (please, make sure Caps Lock is off)")
        ch = _win.getch()
        match(ch):
            case ' ':
                current = [subject for subject in subjects if subject.isCursorOn][0]
                current.isSelected = not current.isSelected
            case curses.KEY_UP:
                current: SubjectItem = [subject for subject in subjects if subject.isCursorOn][0]
                current.isCursorOn = False
                # Get the item above while checking for bounds
                above: SubjectItem = subjects[subjects.index(current) - 1 if subjects.index(current) else 0]
                above.isCursorOn = True
            case curses.KEY_DOWN:
                current: SubjectItem = [subject for subject in subjects if subject.isCursorOn][0]
                current.isCursorOn = False
                # Get the item below while checking for bounds
                below: SubjectItem = subjects[subjects.index(current) + 1 if not subjects.index(current) + 1 == len() else subjects.index(current)]
                below.isCursorOn = True
            case curses.KEY_ENTER:
                break
            case _:
                _win.addstr("Invalid keypress (make sure that Caps Lock is disabled)")

    # Change the amount of pages retrieved for each file
    userinput: str = ""
    while (not (userinput.startswith("C") or userinput.startswith("c"))):
        for file, index in zip(pages_by_file.keys(), range(0, len(pages_by_file))):
            print("[{0}] {1}".format(index, file))

        userinput = input("Change the number of pages selected for any of these? [Enter the index or [C]onfirm to continue]\n>> ")
        try:
            page_amount = input(f"Enter the amount of pages to be selected for {get_filename_by_index(pages_by_file, int(userinput))}" + '\n>> ')
            pages_by_file[get_filename_by_index(pages_by_file, int(userinput))].page_amount = page_amount
        except(ValueError):
            print("\nERROR: NOT A NUMBER\n", file=sys.stderr)
        except(IndexError):
            print("\nERROR: NOT A VALID INDEX\n", file=sys.stderr)

def initialize_sav_files(pdfstream: TextIOWrapper):
    pdfReader = PdfFileReader(pdfstream)
    pagesNumbers: list = [str(pageNum) for pageNum in range(1, pdfReader.numPages + 1)]
    random.shuffle(pagesNumbers)
    with open(f"{pdfstream.name}.sav", 'w') as saveFile:
        print(f"Writing {pdfstream.name}.sav")
        for pageNumber in pagesNumbers:
            saveFile.write(f"{pageNumber}\n")

def get_filename_by_index(pages_by_file: OrderedDict, index: int) -> str:
    return pages_by_file[list(pages_by_file.keys())[int(index)]].filename

def getch(curses_window):
    ch = curses_window.getch()
    if ch == 27:
        # Arrow key
        

# def set_page_amount_by_index(pages_by_file: OrderedDict, index: int, page)

class FileInfo():
    def __init__(self, filename: str, pages: list[int], page_amount: int = 1) -> None:
    #     self.index = index
        self.filename = filename
        self.pages = pages
        self.page_amount = page_amount

class SubjectItem:
    def __init__(self, name: str, isSelected: bool = False, isCursorOn: bool = False) -> None:
        self.name = name
        self.isSelected = isSelected
        self.isCursorOn = isCursorOn
    def __str__(self) -> str:
        return f"[{'*' if self.isSelected else ' '}] {self.name} {'<--' if self.isCursorOn else ''}"

if __name__ == "__main__":
    main()