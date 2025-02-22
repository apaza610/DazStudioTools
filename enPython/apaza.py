#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from apazaui import ApazaUI


class Apaza(ApazaUI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    app = Apaza()
    app.run()
