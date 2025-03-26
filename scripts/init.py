"""Przygotowuje środowisko do pracy"""
import os
import settings
import numpy as np


folderList:list[str] = []
folderList.append(settings.FolderName.data)
folderList.extend([getattr(settings.PathFile, attr) for attr in dir(settings.PathFile)
                   if not callable(getattr(settings.PathFile, attr)) and not attr.startswith("__")])


for i in folderList:
    if not os.path.exists(i) and i is not settings.PathFile.p_bad and i is not settings.PathFile.p_good:
        os.makedirs(i)
if not os.path.isfile(settings.PathFile.config_p):
            with open(settings.PathFile.config_p, "w") as file:
                file.write("path: \nsimilarity: 0.85")

if not os.path.isfile(settings.PathFile.p_good):
    data = np.array([], dtype=np.dtype([('path', 'U256'), ('check', np.uint8), ('batch', np.uint8), ('no', np.uint8)]))
    np.save(settings.PathFile.p_good, data)
if not os.path.isfile(settings.PathFile.p_bad):
    data = np.array([], dtype=np.dtype([('path', 'U256')]))
    np.save(settings.PathFile.p_bad, data)
print('wykonano init')
