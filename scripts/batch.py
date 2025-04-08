"""Plik odpowiedzialny za obsługę plików batch"""
import os
import archive
import settings
import numpy as np
import re

class Batch():
    list_batch: list[list] = [[], [], []]
    """Lista ścieżek do plików serii (0 - nowe, 1- st, 2- a)"""

    def __init__(self, batch_features: np.ndarray= np.array([]), batch_info: np.ndarray = np.array([]), name: str = ""):
        self.name = name
        """Nazwa serii w katalogu, jeśli jest pusta to znaczy, że nie istnieje (bez rozszerzenia)"""
        if self.name!= "":
            self.batch_num= ""
            for char in self.name:
                if char.isdigit():  # Sprawdzamy, czy znak jest cyfrą
                    self.batch_num += char
            self.open_batch()
            self.__what_batch()
        else:  
            self.batch_features = batch_features
            """Tablica zawierająca wektory cech plików z serii"""
            
            self.batch_info = batch_info
            """Zbiór informacji o pojedyńczych plikach"""
            self.type_batch = 1
            """Określi pod jakim typem powinna być zapisana seria"""
        
    def reset(self):
        self.__dict__.clear()


    def save_batch(self, batch_info):
        """Tworzy lub nadpisuje plik"""
        self.batch_info = batch_info
        if self.name == "":
            self.name, self.batch_num = self.__find_available_filename()
            print(f"Zapisano plik: {self.name}")
        self.update_batch_num()
        np.save(self.name+".npy", self.batch_features)
        np.save(self.name+"p.npy", self.batch_info)

    def update_batch_num(self):
        """Aktualizuje informacje o numerze pliku w serii"""
        for row in self.batch_info:
            row['batch'] = int(self.batch_num)
                    
    def update_check_num(self, list_sim, update= np.uint8(0)):
        """Aktualizuje informacje o teście"""
        if list_sim == []:
            self.batch_info['check'] =np.uint8(update)
        for row in self.batch_info:
            if int(row['check']) in list_sim:
                row['check'] =np.uint8(update)
        self.__what_batch()

                    

    
    def __find_available_filename(self, type_batch= -1, end_base_name='.npy'):
        """Funkcja do znajdowania dostępnej nazwy pliku"""
        if type_batch == -1:
            type_batch = self.type_batch
        start_base_name = ""
        match type_batch:
            case 1:
                start_base_name = settings.PathFile.batches_new
            case 2:
                start_base_name = settings.PathFile.batches_self_tested
            case 3:
                start_base_name = settings.PathFile.batches_archive

        i = 1
        while True:
            # Generowanie nazwy pliku
            file_path = f"{start_base_name}{i}"  # np. //batch_0001.npy, //batch_0002.npy, ...
            # Jeśli plik nie istnieje, zwróć nazwę
            if not os.path.exists(file_path+end_base_name):
                return file_path, i
            i += 1

    def __what_batch(self):
        """Zwraca informację o tym pod jakim typem serii powinny być zapisane pliki"""
        for row in self.batch_info:
            self.type_batch=3
            # według serii
            if self.type_batch > row['check']:
                self.type_batch = row['check']

        # według nazwy pliku
        type_name = re.match(r'^[a-zA-Z_]+', os.path.basename(self.name))
        type_name = type_name.group()
        match type_name:
            case -1:
                type_name = 1
            case settings.FileName.batch_new:
                type_name = 1
            case settings.FileName.batch_self_tested:
                type_name = 2
            case settings.FileName.batch_archive:
                type_name = 3
        if self.type_batch != type_name:
            print("self.type_batch", self.type_batch)
            print("type_name",type_name)
            # nalezy zmeinić nazwę pliku, (usunąć stary i ścieżki)
            print("Zmiana/utworzenie nowego pliku")
            self.rename_file(self.type_batch)
            self.update_global_path_file()

    def rename_file(self, type_name):
        """Zmienia śzieżkę i nazwę pliku"""
        new_path, no = self.__find_available_filename(type_batch=type_name)
        self.batch_info['batch'] = np.uint8(no)
        os.rename(self.name+".npy", new_path+".npy")
        np.save(new_path+"p.npy", self.batch_info)

        os.remove(self.name+"p.npy")
        self.name = new_path
    
    def update_global_path_file(self):
        """Aktualizuje informacje o serii w pliku zawierającym wszystkie ścieżki"""
        patch_good_npy = np.load(settings.PathFile.p_bad+".npy")
        var = 0
        for row in self.batch_info:
            var += 1
            print(f"\r\\{var}/ {len(self.batch_info)}", end="")
            existing_index = np.nonzero(patch_good_npy['path'] == row[0])[0]
            if len(existing_index) > 0:
                # Jeśli wiersz istnieje, sprawdzamy, czy dane są takie same
                if not np.array_equal(patch_good_npy[existing_index], row):
                    # Jeśli dane się różnią, aktualizujemy wiersz
                    patch_good_npy[existing_index] = row

        np.save(settings.PathFile.p_bad+".npy", patch_good_npy)
        

    @staticmethod
    def create_list_batch():
        """Tworzy listę zawierającą wszystkie pliki serii (bez rozszerzenia)"""
        Batch.list_batch = [[], [], []]
        for type in (settings.PathFile.batches_new, settings.PathFile.batches_self_tested, settings.PathFile.batches_archive):
            
            for f in os.listdir(os.path.dirname(type)):
                if f.startswith(os.path.basename(type)) and f.endswith(".npy") and f[-5].isdigit():
                    digits = ""
                    for char in f:
                        if char.isdigit():  # Sprawdzamy, czy znak jest cyfrą
                            digits += char
                    match type:
                        case settings.PathFile.batches_new:
                            digits = settings.PathFile.batches_new+digits
                            Batch.list_batch[0].append((digits))
                        case settings.PathFile.batches_self_tested:
                            digits = settings.PathFile.batches_self_tested+digits
                            Batch.list_batch[1].append((digits))
                        case settings.PathFile.batches_archive:
                            digits = settings.PathFile.batches_archive+digits
                            Batch.list_batch[2].append((digits))
    

    def open_batch(self):
        """Metoda pozwalająca na odczytanie serii i informacji o serii z plików batch"""
        self.batch_features = np.load(self.name+".npy")
        self.batch_info = np.load(self.name+"p.npy")

    @staticmethod
    def convert_list_of_similary(list_of_similary):
        list_s = []
        if list_of_similary == []:
            return []
        for i in list_of_similary:
            list_s.append(i[0])
            for t in i[1:]:
                list_s.append(t[0])
        return list_s
