#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from homarui import HomarUI


class Homar(HomarUI):
    def __init__(self, master=None):
        super().__init__(master)


if __name__ == "__main__":
    app = Homar()
    app.run()
