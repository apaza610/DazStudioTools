#################################################################################################################
# Programa que limpia los ZIP de DAZ de basura inutil:
# los ZIP en DAZ contienen:
# -Manifest.dsx             Inutil  solo util para DIM  DazInstallManager
# -Supplement.dsx           Inutil  solo util para DIM 
# -Content/                 Inutil  solo util para DIM
#       -data/              Util para MI    
#       -People/            Util para MI
#       -Runtime/           Util 
#       -.....etc
#################################################################################################################

import zipfile
import os
import shutil
from pathlib import Path

def arreglarZIP(folder, documento):
    miFolderBASE = Path(folder)               #Path(os.getcwd())                            # folder actual
    folderTEMP = 'temporal'
    miFileOLD = documento
    miFileNEW = miFileOLD.split('.')[0] + 'FIX' + '.zip'
    NecesitaArreglo = False

    miZipOLD = zipfile.ZipFile(miFolderBASE/miFileOLD)             # objeto ZIP viejo sucio .duf , Content, etc

    if not os.path.exists(miFolderBASE/folderTEMP):         
        os.makedirs(miFolderBASE/folderTEMP)                # crear folder si no existe

    # si hay folder: Content --> extraer contenidos en temporal
    for unFile in miZipOLD.namelist():
        if unFile.startswith('Content'):
            miZipOLD.extract(unFile,miFolderBASE/folderTEMP)
            NecesitaArreglo = True
        else:
            print("----------------------ZIP sin folder llamado: CONTENT------------------------")

    if NecesitaArreglo:
        miZipNEW = zipfile.ZipFile(miFolderBASE/miFileNEW,'w')         # objeto ZIP nuevo limpio 
        os.chdir(miFolderBASE/folderTEMP/'Content')                 # entrando 1 nivel 
    
        # Compresion de archivos uno por uno al ZIP
        for raiz, dirs, files in os.walk('.', topdown=False):
            for unFile in files:
                miZipNEW.write(os.path.join(raiz,unFile), compress_type=zipfile.ZIP_DEFLATED)

        print("estoy aqui  !!!!:     " + os.getcwd())
        os.chdir(miFolderBASE)           
        print("quiero ir aqui: .....: " + str(miFolderBASE))                   # saliendo al nivel base
        print("Aora estoy aqui  !!!!:     " + os.getcwd())
        miZipNEW.close()
 
    shutil.rmtree(miFolderBASE/folderTEMP)              # TODO borrar material temporal ya inutil

    miZipOLD.close()   
    
    return miFileNEW,NecesitaArreglo            #,NecesitaArreglo


def main():

    for raiz, folders, dcmntos in os.walk(os.getcwd()):
        for dcmnto in dcmntos:
            if dcmnto.endswith('.zip'):
                print(raiz + "...." + dcmnto)
                nombreNewZIP,NecesitaArreglo = arreglarZIP(raiz, dcmnto)

                if NecesitaArreglo:
                    os.remove(os.path.join(raiz,dcmnto))
                    os.rename(nombreNewZIP, os.path.join(raiz,dcmnto))
                

if __name__ == "__main__": main()

