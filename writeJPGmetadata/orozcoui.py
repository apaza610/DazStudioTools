#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from tkinter import filedialog

import zipfile
from iptcinfo3 import IPTCInfo
import pyperclip

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "interfaz.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class OrozcoUI:
    def __init__(self, master=None):
        self.builder = pygubu.Builder()
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object(
            "toplevel1", master)
        self.builder.connect_callbacks(self)

        self.pathchooserinput1 = self.builder.get_object("pathchooserinput1")
        file_tipos = [("solo ZIP", ".zip")]
        self.pathchooserinput1.configure(filetypes=file_tipos)

        self.spinboxNivel = self.builder.get_object("spinboxNivel")
        self.entryMetadata = self.builder.get_object("entryMetadata")

    def run(self):
        self.mainwindow.mainloop()

    def onClickGrabaMetadata(self):
        jpg_path = filedialog.askopenfilename(
            title="Elegi el JPG", filetypes=[("solo JPG", ".jpg")]
        )
        print(jpg_path)

        info = IPTCInfo(jpg_path, force=True)
        info["caption/abstract"] = self.entryMetadata.get()
        info.save()
        print("IPTC caption added successfully!")

    def onClickLeerZip(self):
        zip_path = self.pathchooserinput1.entry.get()
        zip_nivel = int(self.spinboxNivel.get())
        print(f"\033[92m ------{zip_path} nivel: {zip_nivel}------ \033[0m")

        # Open the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List all the contents of the zip file
            zip_contents = zip_ref.namelist()
            
            # Print each file/folder in the zip file
            for item in zip_contents:
                parts = item.split('/')
                if len(parts) == zip_nivel and parts[0] and  zip_ref.getinfo(item).is_dir():
                    print(f"Directory: {item}")
                # else:
                #     print(f"File: {item}")

if __name__ == "__main__":
    app = OrozcoUI()
    app.run()
