"""Plik związany z obsługą katalogu głównego"""
import os
import settings
from PIL import Image
import numpy as np 

Image.MAX_IMAGE_PIXELS = 1000000000

class Archive():
    _instance = None  # Jedna instancja klasy
    catalog_path: str= ""
    
    def __new__(cls, *args, **kwargs):
        # Jeśli instancja już istnieje, zwróć ją
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, catalog_path: str = catalog_path, value=None):
        if not hasattr(self, '_initialized'):  # Zapobiega ponownemu wywołaniu
            self.value = value  # Ustawiamy wartość tylko raz
            self._initialized = True  # Ustawiamy flagę, że konstruktor już był wywołany
            print(f"ilość plików: {sum(len(files) for _, _, files in os.walk(catalog_path))}", end="")
            self.reset()
        else:
            print("Konstruktor nie jest wywoływany ponownie!")
    
    def reset(self):
        """Resetuje informacje z klasy"""
        settings.Config._read_settings()
        Archive.catalog_path = settings.Config.path
        self.list_files_good = np.array([], dtype=np.dtype([('path', 'U256'), ('check', np.uint8), 
                                                            ('batch', np.uint8), ('no', np.uint8)]))
        """Lista plików, które są brane pod uwagę. To są pliki graficzne"""
        self.list_files_bad = np.array([], dtype=np.dtype([('path', 'U256')]))
        """Lista plików, które są pomijane. To nie są pliki graficzne"""
        self.list_new_files_good: list[str, int, int] = []
        """Lista nowych plików, które zosały znalezione w katalogu"""
        self.list_new_files_bad: list[str] = []
        """Lista nowych plików, które zosały znalezione w katalogu"""
        self.patch_good_npy = []
        self.patch_bad_npy = []
        self.__open_list_files_to_npy()

    def __create_list_of_all_files(self):
        """Dodaje scieżkę nowego pliku do listy plików"""
        len_files = sum(len(files) for _, _, files in os.walk(self.catalog_path))
        var = 0
        for root, dirs, files in os.walk(self.catalog_path):
            for file in files:
                file = os.path.join(root, file)
                if file not in self.list_files_good['path']:
                    if self.__test_file(file):
                        
                        self.list_new_files_good.append((file, 0, 0, 0))
                    elif file not in self.list_files_bad['path']:
                        self.list_new_files_bad.append(file)
                var +=1
                if var // 100:
                    print(f"\r\\{var}/{len_files}", end="")
        print()
        self.__save_list_files_to_npy(self.list_new_files_good, self.list_new_files_bad)
    
    def __test_file(self, file: str)->bool:
        """Sprawdza, czy plik nie jest uszkodzony"""
        try:
            with Image.open(file) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def __save_list_files_to_npy(self, path_good:list[tuple[str, int, int, int]], path_bad:list[str] = []):
        """Zapisuje wszystkie ścieżki i informację o nich do pliku npy"""
        var = 0
        
        for row in path_good:
            var += 1
            print(f"\r\\{var}/ {len(path_good)}", end="")
            existing_index = np.nonzero(self.patch_good_npy['path'] == row[0])[0]
            if len(existing_index) > 0:
                # Jeśli wiersz istnieje, sprawdzamy, czy dane są takie same
                if not np.array_equal(self.patch_good_npy[existing_index], row):
                    # Jeśli dane się różnią, aktualizujemy wiersz
                    self.patch_good_npy[existing_index] = row
            else:
                # Jeśli wiersz z 'path' nie istnieje, dodajemy nowy
                new_row = np.array([row], dtype=np.dtype([('path', 'U256'), 
                                        ('check', np.uint8), ('batch', np.uint8), ('no', np.uint8)]))
                self.patch_good_npy = np.append(self.patch_good_npy, new_row)
            

        print()
        var =0
        for row in path_bad:
            
            var += 1
            print(f"\r\\{var}/ {len(path_bad)}", end="")
            existing_index = np.nonzero(self.patch_bad_npy['path'] == row)[0]
            if len(existing_index) > 0:
                # Jeśli wiersz istnieje, sprawdzamy, czy dane są takie same
                if not np.array_equal(self.patch_bad_npy[existing_index], row):
                    # Jeśli dane się różnią, aktualizujemy wiersz
                    self.patch_bad_npy[existing_index] = row
            else:
                # Jeśli wiersz z 'path' nie istnieje, dodajemy nowy
                new_row = np.array([row], dtype=np.dtype([('path', 'U256')]))
                self.patch_bad_npy = np.append(self.patch_bad_npy, new_row)

        # Zapisz zmodyfikowaną tablicę z powrotem do pliku
        np.save(settings.PathFile.p_bad, self.patch_bad_npy)
        # Zapisz zmodyfikowaną tablicę z powrotem do pliku
        np.save(settings.PathFile.p_good, self.patch_good_npy)
        print("\n", self.patch_bad_npy)

        print("poprawne: \n", self.patch_good_npy)
    
    def __open_list_files_to_npy(self):
        """Ładuje pliki ze ścieżkami do list"""
        self.patch_good_npy = np.load(settings.PathFile.p_good, allow_pickle=True)
        self.patch_bad_npy = np.load(settings.PathFile.p_bad, allow_pickle=True)
    
    def search_new_file(self):
        self.__create_list_of_all_files()
        self.__save_list_files_to_npy(self.list_files_good, self.list_files_good)
        print(self.list_files_good)
        print(self.list_files_good)
    
    
    
    
