#!/usr/bin/python3
import pathlib
import subprocess
import tkinter as tk
from tkinter import messagebox
import pygubu

import zipfile
import os
import shutil
from pathlib import Path

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "MiGUI.ui"
RESOURCE_PATHS = [PROJECT_PATH]

class ApazaUI:
    listaZIPs = []

    def __init__(self, master=None):
        self.builder = pygubu.Builder()
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object(
            "toplevel1", master)
        self.builder.connect_callbacks(self)

        self.folderZIPs = self.builder.get_object("entryFolderZIPs")

    def run(self):
        self.mainwindow.mainloop()

    # para cada zip en este folder extraerlo en este mismo folder

    def onBtnEjecutarClicked(self):
        os.chdir(self.folderZIPs.get())        # cambiar a folder de trabajo
        
        # fijate si el zip contiene folder "Content", de lo contrario advertir a usuario
        for raiz, folders, documentos in os.walk(os.getcwd()):
            for documento in documentos:
                if documento.endswith('.zip'):
                    # messagebox.showinfo("mensaje", raiz + "...." + documento)  # E:\assets3D\main\Dog8...IM0005097-01_DazDog8.zip
                    with zipfile.ZipFile(documento) as zip_ref:
                        for item in zip_ref.namelist():
                            if item.startswith('Content'):
                                # messagebox.showinfo("Mensaje", "El .zip contiene folder Content")
                                with zipfile.ZipFile(raiz + "\\" + documento, 'r') as zip_ref2:
                                    zip_ref2.extractall(raiz)
                                break;
                            else:
                                messagebox.showinfo("Mensaje", f"El {documento} no contiene folder Content")
                                break;
        messagebox.showinfo("Mensaje", "deCompresion ejecutada")
        # self.resize_images()
        self.mover_contents()

    def resize_images(self):
        folder_path = Path(self.folderZIPs.get() + "/Content")
        for unfile in folder_path.rglob('*'):
            if unfile.suffix.lower() in ['.png', '.jpg']:   # E:\assets3D\main\env_Egipto\Content\Environments\Architecture\Daz Originals.png
                # comando = f"magick convert {cadena} -resize 50% {cadena}"
                # os.system(comando)
                comando = ['magick', unfile, '-resize', '1024>', unfile ]
                subprocess.run(comando, check=True)
        messagebox.showinfo("Mensaje", "texturas fueron redimensionadas")

    # mover el contenido de carpeta Content al folder DAZ final
    def mover_contents(self):
        self.folderDAZ = self.builder.get_object("entryFolderDAZ").get()
        self.folderZIPs = self.builder.get_object("entryFolderZIPs").get()
        # os.chdir(self.folderZIPs.get())

        # for item in os.listdir(self.folderZIPs.get()+"Content"):
        #     src_item = os.path.join(self.folderZIPs.get()+"Content", item)
        #     dst_item = os.path.join(self.folderDAZ.get())
        #     shutil.move(src_item, dst_item)
            # shutil.rmtree(src_item)
            # messagebox.showinfo("Mensaje", "desde: " + src_item + " hasta: " + dst_item)
        powershell_command = f'Move-Item -Path "{self.folderZIPs}\\Content" -Destination "{self.folderDAZ}" -Force'

        # Run the PowerShell command
        try:
            subprocess.run(["powershell", "-Command", powershell_command], check=True)
            print(f"contenidos movidos successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error moviendo contenidos: {e}")
        

if __name__ == "__main__":
    app = ApazaUI()
    app.run()
