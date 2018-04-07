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

    miZipOLD = zipfile.ZipFile(miFolderBASE/miFileOLD)             # objeto ZIP viejo sucio .duf , readmes, etc
    miZipNEW = zipfile.ZipFile(miFolderBASE/miFileNEW,'w')                      # objeto ZIP nuevo limpio 

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
        os.chdir(miFolderBASE/folderTEMP/'Content')                 # entrando 1 nivel 
    
        # Compresion de archivos uno por uno al ZIP
        for raiz, dirs, files in os.walk('.', topdown=False):
            for unFile in files:
                miZipNEW.write(os.path.join(raiz,unFile), compress_type=zipfile.ZIP_DEFLATED)

        print("estoy aqui  !!!!:     " + os.getcwd())
        os.chdir(miFolderBASE)           
        print("quiero ir aqui: .....: " + str(miFolderBASE))                   # saliendo al nivel base
        print("Aora estoy aqui  !!!!:     " + os.getcwd())
    
    shutil.rmtree(miFolderBASE/folderTEMP)              # TODO borrar material temporal ya inutil

    miZipOLD.close()
    miZipNEW.close()
    
    return miFileNEW            #,NecesitaArreglo


def main():

    for raiz, folders, dcmntos in os.walk(os.getcwd()):
        for dcmnto in dcmntos:
            if dcmnto.endswith('.zip'):
                print(raiz + "...." + dcmnto)
                resultado = arreglarZIP(raiz, dcmnto)
                os.remove(os.path.join(raiz,dcmnto))
                os.rename(resultado, os.path.join(raiz,dcmnto))
                
    """ for nombreFile in os.listdir('.'):
        if nombreFile.endswith('.zip'):
            resultado = arreglarZIP(nombreFile)
            #if resultado[1]:
            os.remove(nombreFile)
            os.rename(resultado,nombreFile) """

if __name__ == "__main__": main()

