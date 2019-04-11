from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from diesis import FileScanner
import os


class GUIHelper:
    @staticmethod
    def open_source_picker():
        path = askopenfilename()
        if path is not None and path != '':
            if not os.path.isdir(path):
                messagebox.showwarning('Invalid directory',
                                       'You must pick a directory containing the audio file to process.')
            FileScanner.FileScanner.set_source(path)

    @staticmethod
    def start():
        scanner = FileScanner.FileScanner()
        scanner.set_source('test/source')
        scanner.set_destination('test/dest')
        scanner.scan()
