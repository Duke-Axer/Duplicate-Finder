"""Przygotowuje środowisko do pracy"""
import os
import settings
import numpy as np


folderList:list[str] = [settings.FolderName.data, 
                        os.path.join(settings.FolderName.data, settings.FolderName.batchs),
                        os.path.join(settings.FolderName.data, settings.FolderName.batchs),
                        os.path.join(settings.FolderName.data, settings.FolderName.archives_batch),
                        os.path.join(settings.FolderName.data, settings.FolderName.paths),
                        os.path.join(settings.FolderName.data, settings.FolderName.tmp),
                        os.path.join(settings.FolderName.data, settings.FolderName.duplicates)]


for i in folderList:
    if not os.path.exists(i):
        os.makedirs(i)
if not os.path.isfile(settings.PathFile.config_p):
            with open(settings.PathFile.config_p, "w") as file:
                file.write("path: \nsimilarity: 0.85")

if not os.path.isfile(settings.PathFile.p_good+".npy"):
    data = np.array([], dtype=settings.dtype_good)
    np.save(settings.PathFile.p_good+".npy", data)
if not os.path.isfile(settings.PathFile.p_bad+".npy"):
    data = np.array([], dtype=settings.dtype_bad)
    np.save(settings.PathFile.p_bad+".npy", data)
print('wykonano init')
