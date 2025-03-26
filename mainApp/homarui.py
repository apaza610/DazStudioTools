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
            p = subprocess.run(["powershell", "-Command", powershell_command], check=True)
            # print(f"contenidos movidos successfully.")
            self.mensaje.configure(text="Contenido fue movido")
            shutil.rmtree(self.folderZIPs + "/Content")
        except subprocess.CalledProcessError as e:
            self.mensaje.configure(text="Error al mover")
            print(f"Error moviendo contenidos: {e}")
        # messagebox.showinfo("Mensaje", "mover ejecutado")
    
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

        # Open the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List all the contents of the zip file
            zip_contents = zip_ref.namelist()
            
            # Print each file/folder in the zip file
            for item in zip_contents:
                parts = item.split('/')
                if len(parts) == zip_nivel and parts[0] and  zip_ref.getinfo(item).is_dir() and not (re.search(r"/[Dd]ata/", item) or re.search(r"/[Rr]untime/", item)):
                    cadena = item.replace('Content/','')
                    print(f"{cadena}")
                    pyperclip.copy(cadena)
                # else:
                #     print(f"File: {item}")

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

if __name__ == "__main__":
    app = HomarUI()
    app.run()
