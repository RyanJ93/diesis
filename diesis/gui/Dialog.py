from tkinter import *
from tkinter import ttk
from diesis import GUIHelper


class Dialog:
    dialog: Tk = None
    content: ttk.Frame = None

    def __build_dialog(self) -> None:
        """
        Builds the main dialog and then save the generate object within the class instance allowing widgets to be added.
        """
        self.dialog = Tk()
        self.dialog.geometry('320x160')
        self.dialog.title('iTunes Exporter')
        self.content = ttk.Frame(self.dialog)
        self.content.grid(column=0, row=0)

    def __build_pickers(self) -> None:
        """
        Generates and adds to the dialog the buttons that allow the user to pick the source and the destination folders.
        """
        button: Button = Button(
            self.dialog,
            text='Source dir',
            command=GUIHelper.GUIHelper.open_source_picker,
            relief=RIDGE
        )
        button.pack(side=LEFT)
        button = Button(
            self.dialog,
            text='Destination dir',
            command=GUIHelper.GUIHelper.open_source_picker,
            relief=RIDGE
        )
        #button.pack(side=LEFT)
        button.grid(column=4, row=3)

    def __build_ui(self):
        if self.dialog is None:
            return
        label: Label = Label(self.dialog, text='Welcome to iTunes Exporter.')
        label.pack(pady=20, padx=50)
        button: Button = Button(
            self.dialog,
            text='OK',
            command=GUIHelper.GUIHelper.start,
            relief=RIDGE
        )
        button.pack()
        self.__build_pickers()

    def __init__(self):
        self.__build_dialog()
        self.__build_ui()
        mainloop()
