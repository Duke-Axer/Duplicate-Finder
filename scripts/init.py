"""Przygotowuje środowisko do pracy"""
import os
import settings

print(__name__)

folderList:list[str] = []
folderList.append(settings.FolderName.data)
folderList.extend([getattr(settings.PathFile, attr) for attr in dir(settings.PathFile)
                   if not callable(getattr(settings.PathFile, attr)) and not attr.startswith("__")])


for i in folderList:
    if not os.path.exists(i):
        os.makedirs(i)
if not os.path.isfile(settings.PathFile.config_p):
            with open(settings.PathFile.config_p, "w") as file:
                file.write("path: \nsimilarity: 0.85")
print('wykonano init')
