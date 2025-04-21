"""Plik zawiera metody i klasy, które będę odpowiedzialne za
przedstawienie użytkownikowi podobnych do siebie obrazów"""

import os
from scripts.batch import Batch
from scripts import settings
import numpy as np
import shutil

class Duplicat():
    """Przechowuje informacje o duplikatach określonego zdjęcia"""
    def __init__(self, batch_name, number):
        self.batch_name = batch_name
        self.number = number
        self.list_dup = []
        """[(nazwa serii, numer obrazu, sim), ...]"""

    def exist(self, batch_name, number):
        """Zwraca informacje czy dane zdjecie istnieje już w liście lub jest z tego obiektu"""
        if self.batch_name == batch_name and self.number == number:
            return True
        
        if any(elem[:2] == (batch_name, number) for elem in self.list_dup if len(elem) >= 2):
            return True
        return False
    
    def add(self, name, number, sim):
        """Dodaje nazwę serii i numer obrazu, który jest podobny do tego z obiektu"""
        if not self.exist(name, number):
            self.list_dup.append((name, number, sim))


class Show():
    """Biblioteka wyświetlająca informacje o duplikatach"""
    list_dup_obj: list[Duplicat] | None = None
    """Lista obiektów, gdzie każdy obiekt zawiera listę duplikatów"""

    @classmethod
    def add_duplicates(cls, new_list):
        """Funkcja do dopisywania do listy duplikatów, dodatkowo sprawdza, czy już istnieją"""
        if not cls.list_dup_obj:
            cls.list_dup_obj = []
            cls.list_dup_obj.append(cls.create_dup_obj(new_list))
            return
        
        for el in cls.list_dup_obj:
            if el.batch_name == new_list[0] and el.number == new_list[1]:
                if not el.exist(new_list[2], new_list[3]):
                    el.add(new_list[2], new_list[3], new_list[4])
                    break
        else:
            cls.list_dup_obj.append(cls.create_dup_obj(new_list))

    @classmethod
    def create_dup_obj(cls, new_list):
        """Tworzy obiekt duplikatu"""
        dup = Duplicat(new_list[0], new_list[1])
        dup.add(new_list[2], new_list[3], new_list[4])
        return dup

    @staticmethod
    def create_filetxt(path, path_img, batch_name, number):
        """Tworzy plik tekstowy z informacjami o duplikatach.

        :param str path: Ścieżka do katalogu
        :param str path_img: ścieżka do pliku image
        :param str batch_name: Nazwa serii
        :param int number: Nimer obrazu w serii"""
        with open(os.path.join(path,"info.txt"), "w", encoding='utf-8') as f:
            f.write(f'{batch_name}:{str(number)}: {path_img}\n')

    @staticmethod
    def add_to_filetxt(path_cat, path_img, dup):
        """Dopisuje informacje o duplikatach do pliku tekstowego.

        :param str path_cat: Ścieżka do katalogu
        :param str path_img: Ścieżka do obrazu
        :param list[name, number, sim] dup: Informacje o podobnieństwie"""
        with open(os.path.join(path_cat,"info.txt"), "a", encoding='utf-8') as f:
                f.write("{}:{}: {} = {} \n".format(
                    dup[0], str(dup[1]), path_img, dup[2]))

    @staticmethod
    def create_catalog(file, index):
        """Tworzy katalog związany z danym obrazem, który posiada duplikaty

        :param int index: Index obrazu w serii.
        :param str file: Nazwa pliku serii, który zawiera sprawdzony obraz.
        :return path_dup: Ścieżka do katalogu"""
        path_dup = os.path.join(settings.PathFile.duplicates, f'{file}x{str(index)}')
        if os.path.exists(path_dup):
            shutil.rmtree(path_dup)
        os.mkdir(path_dup)
        return path_dup
    
    @staticmethod
    def copy_images(path_dir, path_img, name_batch, number):
        """Zapiuje obrazy do folderu
        
        :param str path_dir: Ścieżka do katalogu
        :param str path_img: Ścieżka do obrazu
        :param str name_batch: Nazwa serii.
        :param int number: Numer obrazu w serii.
        """
        _, type_f = os.path.splitext(path_img)
        shutil.copy(path_img, os.path.join(path_dir, name_batch+' '+str(number)+type_f))

    @classmethod
    def loop_all_dup(cls):
        """wykonyje dla wszystkich plików zapisanych w input_info"""
        
        for dup in cls.list_dup_obj:
            path_cat = Show.create_catalog(dup.batch_name, dup.number)
            path_img = Batch.return_path_img(dup.batch_name, dup.number)
            Show.create_filetxt(path_cat, path_img, dup.batch_name, dup.number)
            Show.copy_images(path_cat, path_img, dup.batch_name, dup.number)
            for dup_2 in dup.list_dup:
                path_img = Batch.return_path_img(dup_2[0], dup_2[1])
                cls.add_to_filetxt(path_cat, path_img, dup_2)
                Show.copy_images(path_cat, path_img, dup_2[0], dup_2[1])



