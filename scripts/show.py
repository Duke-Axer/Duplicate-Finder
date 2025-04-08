"""Plik zawiera metody i klasy, które będę odpowiedzialne za
przedstawienie użytkownikowi podobnych do siebie obrazów"""

import os
import settings
import numpy as np
import shutil
## Wszystko do poprawy, inne dane wejściowe
class Show():
    input_info:list[list] = []
    """Wejściowe informacje o duplikatach, zawiera 
    [
    [file1, file2, [img0, (img1, sim)]], ...
    ]"""
    @staticmethod
    def add_duplicates(new_list):
        """Funkcja do dopisywania do listy duplikatów"""
        Show.input_info.append(new_list)
    @staticmethod
    def remove_duplicates(delete):
        """Funkcja do usuwania z listy duplikatów"""
        del Show.input_info[delete]
    @staticmethod
    def return_path(list_dup):
        """Zwraca listę ścieżek powiązanych z listą"""
        list_path = []
        for row in np.load(list_dup[0]+"p.npy"):
            print(list_dup)
            print(list_dup[2])
            print(row['no'])
            if row['no'] == np.uint8(list_dup[2]):
                list_path.append(row['path'])
                break
        for index, _ in list_dup[3:]:
            for row in np.load(list_dup[1]+"p.npy"):
                if np.uint8(index) == row['no']:
                    list_path.append(row['path'])
                    break
        return list_path

    @staticmethod
    def create_filetxt(path, list_dup, list_path_dup):
        """Tworzy plik tekstowy z informacjami"""
        with open(os.path.join(path,"info.txt"), "w") as f:
            f.write(str(os.path.basename(list_dup[0]))+ str(list_dup[2]) + ": "+list_path_dup[0]+"\n")
        Show.add_to_filetxt(path, list_dup, list_path_dup)
    @staticmethod
    def add_to_filetxt(path, list_dup, list_path_dup):
        """Dopisuje do pliku tekstowego"""
        with open(os.path.join(path,"info.txt"), "a") as f:
            var = 1
            for index, sim in list_dup[3:]:
                f.write("{}: {} = {} \n".format(
                    str(os.path.basename(list_dup[1]))+str(index), list_path_dup[var], sim))
                var +=1
    @staticmethod
    def create_catalog(file, index):
        """Tworzy katalog związany z danym obrazem, który posiada duplikaty"""
        name = os.path.basename(file)
        path_dup = os.path.join(settings.PathFile.duplicates, name+ "x"+ str(index))
        if os.path.exists(path_dup):
            for filename in os.listdir(path_dup):
                file_path = os.path.join(path_dup, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except:
                    print(path_dup)
        else:
            os.mkdir(path_dup)
        return path_dup
    
    @staticmethod
    def copy_images(path_to_save, list_dup, list_paths_dup):
        """Zopiuje obrazy do folderu"""
        print(str(os.path.basename(list_dup[0]))+str(list_dup[2]))
        _, type_f = os.path.splitext(list_paths_dup[0])
        shutil.copy(list_paths_dup[0], os.path.join(path_to_save, 
                    str(os.path.basename(list_dup[0]))+str(list_dup[2]))+type_f)
        var = 1
        for index, _ in list_dup[3:]:
            _, type_f = os.path.splitext(list_paths_dup[var])
            shutil.copy(list_paths_dup[var], os.path.join(path_to_save, 
                        str(os.path.basename(list_dup[1]))+str(index))+type_f)

    @staticmethod
    def loop__all_dup():
        """wykonyje dla wszystkich plików zapisanych w input_info"""
        for list_dup in Show.input_info:
            list_paths_dup = Show.return_path(list_dup)
            path_to_save = Show.create_catalog(os.path.basename(list_dup[0]), list_dup[2])
            print(path_to_save)
            Show.create_filetxt(path_to_save, list_dup, list_paths_dup)
            Show.copy_images(path_to_save, list_dup, list_paths_dup)

