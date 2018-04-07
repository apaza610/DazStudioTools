# FixZIPparaDAZ
Batch Delete unnecessary stuff from DAZ zip files.

while some DAZ studio zip files contain:

      -Manifest.dsx             Inutil  solo util para DIM  DazInstallManager.

      -Supplement.dsx           Inutil  solo util para DIM. 

      -Content/                 Inutil  solo util para DIM.

            -data/              Util para MI.    

            -People/            Util para MI.

            -Runtime/           Util. 

            -.....etc.

other DAZ zip files have just the Useful folders.

This program deletes useless files & move remaining folders to root folder (Content folder is deleted), 
this makes all my DAZ zip files have same structure, therefore easy to install manually in my library
