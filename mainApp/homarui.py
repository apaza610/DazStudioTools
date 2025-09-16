#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from tkinter import filedialog
from tkinter import messagebox

import zipfile
from iptcinfo3 import IPTCInfo
import os
import pyperclip
import re

import subprocess
import sys
import shutil
from pathlib import Path
import winsound

from PIL import Image

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "interfaz.ui"
RESOURCE_PATHS = [PROJECT_PATH]

class HomarUI:
    def __init__(self, master=None):
        self.builder = pygubu.Builder()
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object("toplevel2", master)
        self.builder.connect_callbacks(self)

        self.v_elegido = self.builder.get_variable("v_compresion")
        self.v_elegido.set("1024>")             # opcion preDefinida

        self.pathchooserinput1 = self.builder.get_object("pathchooserinput1")
        file_tipos = [("solo ZIP", ".zip")]
        self.pathchooserinput1.configure(filetypes=file_tipos)

        self.spinboxNivel = self.builder.get_object("spinboxNivel")
        self.entryMetadata = self.builder.get_object("entryMetadata")

    def run(self):
        self.mainwindow.mainloop()
    
    #----------------- Tab1: Populate Daz library from ZIPs -----------------------

    def onBtnEjecutarClicked(self):
        self.folderZIPs = self.builder.get_object("entryFolderZIPs")
        self.mensaje = self.builder.get_object("labelMensaje")
        self.mensaje.configure(text="..")
        
        zip_path = Path(self.folderZIPs.get())          # E:\assetsDAZ\main\aaa1\GCC20240125-01_GCCFF7Sephiroth.zip
        parent_path = ""                                # E:\assetsDAZ\main\aaa1

        if zip_path.suffix.lower() == ".zip":                    # si usuario da un zip
            self.desCompresor(zip_path, zip_path.parent)
            parent_path = zip_path.parent
        else:                                                   # si usuario da un folder
            zip_files = [f for f in os.listdir(zip_path) if f.lower().endswith('.zip')]
            for zip_file in zip_files:
                self.desCompresor(zip_path / zip_file, zip_path)
                # print(str(zip_path) + "----------------------" + zip_file)
            parent_path = zip_path

        self.moveContentToMain(parent_path)

    def desCompresor(self, zip_path, parent_path):
        print(f"\033[93mEstoy descomprimiendo {zip_path} \033[0m")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(parent_path)
                print(f"✅ Extracted to: {parent_path}")
        except zipfile.BadZipFile:
            print("❌ The file is not a valid ZIP archive.")

    def moveContentToMain(self, source_dir):            # mover el contenido de carpeta Content al folder DAZ final
        print("moviendo desde 📁: " + str(source_dir / "Content"))

        source_dir = source_dir / "Content"
        target_dir = r"E:\assetsDAZ\mainDAZ"

        powershell_command = f'Copy-Item -Path "{source_dir}\\*" -Destination "{target_dir}" -Recurse -Force'
        try:
            p = subprocess.run(["powershell", "-Command", powershell_command], check=True)
            # print(f"contenidos movidos successfully.")
            self.mensaje.configure(text="Contenido fue movido")
            shutil.rmtree(source_dir)
        except subprocess.CalledProcessError as e:
            self.mensaje.configure(text="Error al mover")
            print(f"Error moviendo contenidos: {e}")

        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)       # Play a sound to alert the user (default Windows beep)

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
    
    #----------------- Tab2: grabar metadata on JPGs ------------------------------
    def arreglarElPath(self, event=None):
        cadena = self.pathchooserinput1.entry.get()
        if ".zip" in cadena:
            self.pathchooserinput1.configure(path=os.path.dirname(cadena))
            print("mouse ha entrado al area del widget")

    def onMouseAdentro(self, event=None):
        self.entryMetadata.delete(0, tk.END)
        self.entryMetadata.insert(0, pyperclip.paste())

    def onClickLeerZip(self):
        zip_path = self.pathchooserinput1.entry.get()
        zip_nivel = int(self.spinboxNivel.get())
        print(f"\033[92m ------{zip_path} nivel: {zip_nivel}------ \033[0m")
        folders = set()

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for entry in zip_ref.namelist():
                # Normalize and split the path
                parts = entry.strip('/').split('/')
                if entry.endswith('/'):
                    folders.add('/'.join(parts))
                elif len(parts) > 1:
                    # Infer folder from file path
                    folders.add('/'.join(parts[:-1]))

        for folder in folders:
            if len(folder.split('/')) == zip_nivel and not (re.search(r"/[Dd]ata/", folder) or re.search(r"/[Rr]untime/", folder)):
                # print("***" + folder)
                cadena = folder.replace('Content/','')
                print(f"{cadena}")
                pyperclip.copy(cadena)

    def onClickGrabaMetadata(self):
        jpg_path = filedialog.askopenfilename(
            title="Elegi el JPG", filetypes=[("solo JPG", ".jpg")]
        )
        print(jpg_path)

        info = IPTCInfo(jpg_path, force=True)
        cadena = self.entryMetadata.get()
        info["caption/abstract"] = re.sub("\n+","",cadena)
        info.save()
        print("IPTC caption added successfully!")
        self.entryMetadata.delete(0, tk.END)
        basura = jpg_path + "~"
        if os.path.exists(basura):
            os.remove(basura)
            print("se ha quitado la basura")

    #----------------- Tab3: reName JPGs for my website -----------------------
    def pegarPathJPG(self, event=None):
        self.entryPathJPG = self.builder.get_object("entryPathJPG")
        self.entryPathJPG.delete(0, tk.END)
        self.pathOldDelJPG = Path(pyperclip.paste())
        self.entryPathJPG.insert(0, self.pathOldDelJPG)

    def capitalizar(self, hallado):         # primera letra a Mayuscula
        return hallado.group(1).upper()

    def buildNameJPG(self):
        self.entryNewNameJPG = self.builder.get_object("entryNewNameJPG")
        # folderDelJPG = self.pathOldDelJPG.parent
        nombreDelJPG = self.pathOldDelJPG.stem      # nombre sin extension

        nombreDelJPGsinEspacios = re.sub(r'[\s-](\b\w)', self.capitalizar, nombreDelJPG)    # remover white spaces y capitalizar

        self.v_tipoAsset = self.builder.get_variable("v_tipoAsset")
        self.v_generacion = self.builder.get_variable("v_generacion")
        self.v_genero = self.builder.get_variable("v_genero")
        nombreFinal = f"{self.v_tipoAsset.get()}_{self.v_generacion.get()}{self.v_genero.get()}{nombreDelJPGsinEspacios}"

        self.entryNewNameJPG.delete(0, tk.END)
        # self.entryNewNameJPG.insert(0, folderDelJPG / (nombreDelJPG.replace(" ", "_")))
        self.entryNewNameJPG.insert(0, nombreFinal)

    def singleRenameJPG(self):
        self.pathNewDelJPG = self.pathOldDelJPG.parent / (self.entryNewNameJPG.get() + ".jpg")
        self.convert_resize_rename_jpg(self.pathOldDelJPG, self.pathNewDelJPG)

    def batchRenameJPGs(self):
        self.pathNewDelJPG = self.pathOldDelJPG.parent / (self.entryNewNameJPG.get() + ".jpg")

        jpg_paths = filedialog.askopenfilenames(title="seleccionar Imagenes",initialdir=self.pathOldDelJPG.parent , filetypes=[("imagenes","*.jpg *.png *.webp")])
        for index, jpg_path in enumerate(jpg_paths, start=1):
            print(f"{index}: {jpg_path}")
            self.pathNewDelJPG = self.pathNewDelJPG.with_name(f"{self.entryNewNameJPG.get()}{index}.jpg")
            self.convert_resize_rename_jpg(Path(jpg_path), self.pathNewDelJPG)
            # self.convert_resize_rename_jpg(Path("c:/folder/foto.jpg"), Path("c:/folder/libro.jpg"))
        pass

    def convert_resize_rename_jpg(self, viejo_path: Path, nuevo_path: Path):
        # print(f"de: {viejo_path.stem} a: {nuevo_path.parent}")
        if viejo_path.suffix.lower() != ".jpg":                     # convertir a JPG si es necesario
            imagen = Image.open(viejo_path)
            imagen.convert("RGB").save(nuevo_path, "JPEG")
            os.remove(viejo_path)
        else:                                                       # o simplemente renombrar
            os.rename(viejo_path, nuevo_path)

        # reSize if one side of the image is more than 400px
        subprocess.run(["magick","convert",nuevo_path,"-resize","400x400>",nuevo_path])

    def cambio_de_tab(self, evento):
        self.entryPathJPG = self.builder.get_object("entryPathJPG")
        partes = self.entryPathJPG.get().split("\\")
        folder = "\\".join(partes[:-1])
        
        self.folderZIPs = self.builder.get_object("entryFolderZIPs")
        self.folderZIPs.delete(0, tk.END)
        self.folderZIPs.insert(0, folder)

        self.pathchooserinput1 = self.builder.get_object("pathchooserinput1")
        self.pathchooserinput1.configure(path=folder)


if __name__ == "__main__":
    app = HomarUI()
    app.run()
