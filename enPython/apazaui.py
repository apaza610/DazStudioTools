#!/usr/bin/python3
import pathlib
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import pygubu

import zipfile
import os
import shutil
from pathlib import Path

import winsound

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "MiGUI.ui"
RESOURCE_PATHS = [PROJECT_PATH]

class ApazaUI:

    def __init__(self, master=None):
        self.builder = pygubu.Builder()
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object("toplevel1", master)
        self.builder.connect_callbacks(self)

        self.v_elegido = self.builder.get_variable("v_compresion")
        self.v_elegido.set("1024>")             # opcion preDefinida

    def run(self):
        self.mainwindow.mainloop()

    # para cada zip en este folder extraerlo en este mismo folder
    def onBtnEjecutarClicked(self):
        self.folderZIPs = self.builder.get_object("entryFolderZIPs")
        self.mensaje = self.builder.get_object("labelMensaje")
        self.mensaje.configure(text="..")

        os.chdir(self.folderZIPs.get())        # cambiar a folder de trabajo
        
        # advertir a usuario si el .zip no contiene folder "Content"
        can_deCompress: bool = False
        for raiz, folders, documentos in os.walk(os.getcwd()):
            for documento in documentos:
                if documento.endswith('.zip'):
                    # messagebox.showinfo("mensaje", raiz + "...." + documento)  # E:\assets3D\main\Dog8...IM0005097-01_DazDog8.zip
                    with zipfile.ZipFile(documento) as zip_ref:
                        for item in zip_ref.namelist():
                            if item.startswith('Content'):
                                can_deCompress = True
                                break
                            else:
                                can_deCompress = False
                                messagebox.showinfo("Mensaje", f"El {documento} no contiene folder Content")
                                sys.exit()
                            
        if can_deCompress == True:
            for zip_file in Path(os.getcwd()).rglob('*.zip'):
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    print(f"desComprimiendo {zip_ref.filename}")
                    zip_ref.extractall(os.getcwd())
                self.mensaje.configure(text="desComprimido..")
                # messagebox.showinfo("Mensaje", "desComprimido")        
            # messagebox.showinfo("Mensaje", "deCompresion ejecutada")
            
            winsound.Beep(450,500)
            print("------------------unCompress terminado-------------------------")
            self.resize_images()
            winsound.Beep(550,500)
            print("------------------reSize terminado-------------------------")
            self.mover_contents()
            winsound.Beep(650,500)
            print("------------------move to destination terminado-------------------------")
        else:
            self.mensaje.configure(text="still Comprimido")

    def resize_images(self):
        folder_path = Path(self.folderZIPs.get() + "/Content")
        for unfile in folder_path.rglob('*'):
            if unfile.suffix.lower() in ['.png', '.jpg']:   # E:\assets3D\main\env_Egipto\Content\Environments\Architecture\Daz Originals.png
                # comando = f"magick convert {cadena} -resize 50% {cadena}"
                # os.system(comando)
                match self.v_elegido.get():
                    case "nada":
                        self.mensaje.configure(text="NO se reDimensionara")
                    case "1024>":
                        comando = ['magick', unfile, '-resize', '1024>', unfile ]
                        print(f"reSizing {unfile}")
                        subprocess.run(comando, check=True)
                        # self.mensaje.configure(text="reDimension 1K")
                    case "2048>":
                        comando = ['magick', unfile, '-resize', '2048>', unfile ]
                        print(f"reSizing {unfile}")
                        subprocess.run(comando, check=True)
                        # self.mensaje.configure(text="reDimension 2K")
                    case _:
                        print("ninguna opcion elegida")
        # messagebox.showinfo("Mensaje", "reSize ejecutado")
        
    # mover el contenido de carpeta Content al folder DAZ final
    def mover_contents(self):
        self.folderDAZ = self.builder.get_object("entryFolderDAZ").get()
        self.folderZIPs = self.builder.get_object("entryFolderZIPs").get()
        
        powershell_command = f'Copy-Item -Path "{self.folderZIPs}\\Content\\*" -Destination "{self.folderDAZ}" -Recurse -Force'
        try:
            subprocess.run(["powershell", "-Command", powershell_command], check=True)
            # print(f"contenidos movidos successfully.")
            self.mensaje.configure(text="Contenido fue movido")
            shutil.rmtree(self.folderZIPs + "/Content")
        except subprocess.CalledProcessError as e:
            self.mensaje.configure(text="Error al mover")
            print(f"Error moviendo contenidos: {e}")
        # messagebox.showinfo("Mensaje", "mover ejecutado")

if __name__ == "__main__":
    app = ApazaUI()
    app.run()
