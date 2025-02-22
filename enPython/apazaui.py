#!/usr/bin/python3
import pathlib
import tkinter as tk
from tkinter import messagebox
import pygubu

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "MiGUI.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class ApazaUI:
    def __init__(self, master=None):
        self.builder = pygubu.Builder()
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object(
            "toplevel1", master)
        self.builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()

    def onBtnEjecutarClicked(self):
        messagebox.showinfo("Mensaje", "Has apretado el boton ejecutar")

if __name__ == "__main__":
    app = ApazaUI()
    app.run()
