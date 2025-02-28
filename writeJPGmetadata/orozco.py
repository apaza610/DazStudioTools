#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from orozcoui import OrozcoUI


class Orozco(OrozcoUI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    app = Orozco()
    app.run()
