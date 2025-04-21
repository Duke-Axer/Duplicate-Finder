"""Plik związany z obsługą katalogu głównego"""
import os
import scripts.settings as s
from PIL import Image
import numpy as np 

Image.MAX_IMAGE_PIXELS = 1000000000 # Zwięszenie limitu rozmiaru obrazu

class Archive():
    """Klasa odpowiedzialna za przeszukiwanie graficznej bazy danych oraz utworzenie listy ścieżek do analizowanych obrazów
    
    :param str catalog_path: Ścieżka do katalogu z obrazami
    """
    _instance = None
    catalog_path: str= ""
    """Ścieżka do katalogu z obrazami"""
    
    def __new__(cls, *args, **kwargs):
        # Jeśli instancja już istnieje, zwróć ją
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, catalog_path: str = catalog_path, value=None):
        """Tworzenie obiektu klasy
        
        :param str catalog_path: Ścieżka do katalogu z obrazami
        """
        if not hasattr(self, '_initialized'):  # Zapobiega ponownemu wywołaniu
            self.value = value
            self._initialized = True
            self.reset()
    
    def reset(self):
        """Resetuje informacje z klasy"""
        s.Config._read_settings()
        Archive.catalog_path = s.Config.path
        self.list_files_good = np.array([], dtype=s.dtype_good)
        """Lista plików, które są brane pod uwagę. To są pliki graficzne"""
        self.list_files_bad = np.array([], dtype=np.dtype([('path', 'U256')]))
        """Lista plików, które są pomijane. To nie są pliki graficzne"""
        self.list_new_files_good: list[tuple[str, int, int, int]] = []
        """Lista nowych plików, które zosały znalezione w katalogu"""
        self.list_new_files_bad: list[str] = []
        """Lista nowych plików, które zosały znalezione w katalogu"""
        self.patch_good_npy = np.array([], dtype=s.dtype_good)
        """Lista plików, które są brane pod uwagę. To są pliki graficzne"""
        self.patch_bad_npy = np.array([], dtype=s.dtype_bad)
        """Lista plików, które są pomijane. To nie są pliki graficzne"""
        self.__open_list_files_to_npy()

    def __create_list_of_all_files(self):
        """Przeszukuje katalog i dodaje scieżkę nowego pliku do listy plików"""
        print('Trwa przeszukiwanie katalogu w celu znalezienia nowych obrazów')
        len_files = sum(len(files) for _, _, files in os.walk(Archive.catalog_path))
        set_list_path_g = set(self.patch_good_npy['path'])
        set_list_path_b = set(self.patch_bad_npy['path'])
        var = 1
        for root, dirs, files in os.walk(Archive.catalog_path):
            for file in files:
                file = os.path.join(root, file)
                if file not in set_list_path_g:
                    if self.__test_file(file):
                        self.list_new_files_good.append((file, 0, 0, 0))
                    elif file not in set_list_path_b:
                        self.list_new_files_bad.append(file)
                if not var % 100:
                    print(f"\r{var}/{len_files}", end="")
                var+=1
        print(f"\r\033[32mZnaleziono {var-1} plików\033[0m")
    
    def __test_file(self, file: str)->bool:
        """Sprawdza, czy plik jest sprawny.
        
        :param str file: ścieżka do pliku.
        :return bool: Prawda - Plik jest sprawny. Fałsz - Plik jest uszkodzony.
        """
        try:
            with Image.open(file) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def save_list_files_to_npy(self, path_good:list[tuple[str, int, int, int]], path_bad:list[str] = []):
        """Zapisuje wszystkie ścieżki i informację o nich do pliku npy"""
        print('Trwa zapisywanie/atualizacja danych w głównym pliku ze ścieżkami\n')
        for var, row in enumerate(path_good, 1):
            print(f"\r\\{var}/ {len(path_good)}", end="")
            existing_index = np.nonzero(self.patch_good_npy['path'] == row[0])[0]
            if len(existing_index) > 0:
                # Jeśli wiersz istnieje, sprawdzamy, czy dane są takie same
                if not np.array_equal(self.patch_good_npy[existing_index], row):
                    # Jeśli dane się różnią, aktualizujemy wiersz
                    self.patch_good_npy[existing_index] = row
            else:
                # Jeśli wiersz z 'path' nie istnieje, dodajemy nowy
                new_row = np.array([row], dtype=s.dtype_good)
                self.patch_good_npy = np.append(self.patch_good_npy, new_row)
            
        for var_2, row in enumerate(path_bad, 1):
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

        np.save(s.PathFile.p_bad+".npy", self.patch_bad_npy)
        np.save(s.PathFile.p_good+".npy", self.patch_good_npy)
        return var
    
    @staticmethod
    def save_numpy(path: str, content):
        """Zapisuje plik numpy
        
        :param str path: Pełna ścieżka do miejsca gdzie ma się plik zapisać.
        :param np.array() content: Zawartość do zapisania.
        """
        save_succes = False
        while not save_succes:
            try:
                np.save(path, content)
                save_succes = True
            except KeyboardInterrupt:
                print('\033[33mPróba przerwania - ponawiam zapis...033[0m')

    
    def save_list_files_to_npy_new(self, path_good:np.array, path_bad:np.array = np.array([], dtype=s.dtype_bad)):
        """ Zapisuje i aktualizuje wszystkie ścieżki i informację o nich do plików npy.
        Aktualne wartości pobiera z argumentów.
        
        :param np.array([], dtype=s.dtype_good) path_good: Lista plików, poprawnych
        :param np.array([], dtype=s.dtype_bad) path_bad: Lista plików uszkodzonych
        """
        print('Trwa zapisywanie/aktualizacja danych w głównym pliku ze ścieżkami')
        full_var = len(path_good)
        all_path = {}
        for row in self.patch_good_npy:
            all_path[row[0]] = row
        for var, row in enumerate(path_good, 1):
            path = row[0]
            if path in all_path:
                updated_row = (path, row[1], row[2], row[3])
                all_path[path] = updated_row
            else:
                all_path[path] = row
            if not var%100:
                print(f"\r{var}/ {full_var}", end="")
        try:
            print(f"\r\033[32mPliki analizowane: {var}\033[0m")
        except UnboundLocalError:
            print('Brak nowych plików')
            return
        print(f"\r\033[32mPliki analizowane: {var}\033[0m")
        self.patch_good_npy = np.array(list(all_path.values()), dtype=s.dtype_good)
        Archive.save_numpy(s.PathFile.p_good+s.np_type, self.patch_good_npy)
        
        full_var = len(path_bad)
        if full_var == 0:
            return
        all_path = {}
        for row in self.patch_bad_npy:
            all_path[row[0]] = row
        for var, row in enumerate(path_bad, 1):
            path = row[0]
            if path not in all_path:
                all_path[path] = row
            if not var%100:
                print(f"\r{var}/ {full_var}", end="")
        print(f"\r\033[32mPliki niepoprawne: {var}\033[0m")
        self.patch_bad_npy = np.array(list(all_path.values()), dtype=s.dtype_bad)
        Archive.save_numpy(s.PathFile.p_bad+s.np_type, self.patch_bad_npy)


    def __open_list_files_to_npy(self):
        """Ładuje pliki ze ścieżkami do list"""
        self.patch_good_npy = np.load(s.PathFile.p_good+s.np_type, allow_pickle=True)
        self.patch_bad_npy = np.load(s.PathFile.p_bad+s.np_type, allow_pickle=True)
    
    def search_new_file(self):
        """Wyszukuje nowe pliki i zapisuje ścieżki do plików ścieżek npy"""
        self.__create_list_of_all_files()
        return self.save_list_files_to_npy_new(self.list_new_files_good, self.list_new_files_bad)
    
    def make_new_batch(self):
        """Zwraca 255 ścieżek do plików niesprawdzonych pod względem podobieństwa"""
        batch = np.array([], dtype=s.dtype_good)
        num = 0
        for row in self.patch_good_npy:
            if row['check'] == 0 and num <255:
                batch = np.append(batch, row)
                num+=1
                if num == 255:
                    break
        if len(batch) < 255:
            print(f"jest mniej niż 255 plików: {len(batch)}")
        return batch
