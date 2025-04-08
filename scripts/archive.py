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
            self.reset()
        else:
            print("Konstruktor nie jest wywoływany ponownie!")
    
    def reset(self):
        """Resetuje informacje z klasy"""
        settings.Config._read_settings()
        Archive.catalog_path = settings.Config.path
        self.list_files_good = np.array([], dtype=settings.dtype_good)
        """Lista plików, które są brane pod uwagę. To są pliki graficzne"""
        self.list_files_bad = np.array([], dtype=np.dtype([('path', 'U256')]))
        """Lista plików, które są pomijane. To nie są pliki graficzne"""
        self.list_new_files_good: list[tuple[str, int, int, int]] = []
        """Lista nowych plików, które zosały znalezione w katalogu"""
        self.list_new_files_bad: list[str] = []
        """Lista nowych plików, które zosały znalezione w katalogu"""
        self.patch_good_npy = np.array([], dtype=settings.dtype_good)
        """Lista plików, które są brane pod uwagę. To są pliki graficzne"""
        self.patch_bad_npy = np.array([], dtype=settings.dtype_bad)
        """Lista plików, które są pomijane. To nie są pliki graficzne"""
        self.__open_list_files_to_npy()

    def __create_list_of_all_files(self):
        """Przeszukuje katalog i dodaje scieżkę nowego pliku do listy plików"""
        len_files = sum(len(files) for _, _, files in os.walk(self.catalog_path))
        var = 0
        for root, dirs, files in os.walk(self.catalog_path):
            for file in files:
                file = os.path.join(root, file)
                if file not in self.patch_good_npy['path']:
                    if self.__test_file(file):
                        
                        self.list_new_files_good.append((file, 0, 0, 0))
                    elif file not in self.patch_bad_npy['path']:
                        self.list_new_files_bad.append(file)
                var +=1
                if var // 100:
                    print(f"\r\\{var}/{len_files}", end="")
        print()
        
    
    def __test_file(self, file: str)->bool:
        """Sprawdza, czy plik nie jest uszkodzony"""
        try:
            with Image.open(file) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def save_list_files_to_npy(self, path_good:list[tuple[str, int, int, int]], path_bad:list[str] = []):
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
                new_row = np.array([row], dtype=settings.dtype_good)
                self.patch_good_npy = np.append(self.patch_good_npy, new_row)
            

        print()
        var_2 =0
        for row in path_bad:
            
            var_2 += 1
            print(f"\r\\{var_2}/ {len(path_bad)}", end="")
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

        np.save(settings.PathFile.p_bad+".npy", self.patch_bad_npy)
        np.save(settings.PathFile.p_good+".npy", self.patch_good_npy)
        return var
    
    def __open_list_files_to_npy(self):
        """Ładuje pliki ze ścieżkami do list"""
        self.patch_good_npy = np.load(settings.PathFile.p_good+".npy", allow_pickle=True)
        self.patch_bad_npy = np.load(settings.PathFile.p_bad+".npy", allow_pickle=True)
    
    def search_new_file(self):
        """Wyszukuje nowe pliki i zapisuje ścieżki do plików ścieżek npy"""
        self.__create_list_of_all_files()
        return self.save_list_files_to_npy(self.list_new_files_good, self.list_new_files_bad)
    
    def make_new_batch(self):
        """Zwraca 100 ścieżek do plików niesprawdzonych pod względem podobieństwa"""
        batch = np.array([], dtype=settings.dtype_good)
        var = 0
        for row in self.patch_good_npy:
            if row['check'] == 0 and var <100:
                
                batch = np.append(batch, row)
                var +=1
        if len(batch) < 100:
            print("jest mniej niż 100 plików")
        return batch
    
    
    def print_paths(self):
        print(self.patch_good_npy)
