"""Plik odpowiedzialny za obsługę plików batch"""
import os
from scripts import settings as s
import numpy as np

class classproperty:
    def __init__(self, method):
        self.method = method
    
    def __get__(self, obj, owner):
        return self.method(owner)

class Batch():
    """Reprezentuje plik serii
    
    :param list[list] list_batch: Lista id wszystkich plików zawierających serię [[lista n], [lista st], [lista a]]
    :param np.array([]) batch_features: Seria zawierająca cechy obrazów
    :param [('path', 'U512'), ('check', np.uint8), ('batch', np.uint16), ('no', np.uint8)] batch_info: Seria zawierająca informacje o obrazach
    :param str name: Scieżka do serii, uwzględniajac tylko p: <[p].npy>. np: Data\\batch\\[b_n1].
    :param str batch_num: Numer serii, nie zawiera informoacji o typie serii.
    :param int type_batch: Informacja o typie serii.\n
        1 - wykonana predykcja cech\n
        2 - plik nie zawiera obrazów podobnych do siebie w swojej serii\n
        3 - plik nie zawiera obrazów podobnych w swojej serii i w archiwum
    """
    _list_batch: list[list] | None = None
    """Lista id wszystkich plików zawierających serię [[lista n], [lista st], [lista a]]"""

    def __init__(self, batch_features: np.ndarray= np.array([]), batch_info: np.ndarray = np.array([]), name: str | None = None):
        """Inicjalizacja obiektu serii
        
        :param np.array([]) batch_features: Seria zawierająca cechy obrazów
        :param np.array([]) batch_info: Seria zawierająca informacje o obrazach
        :param str name: Scieżka do serii, nie uwzględniajac <[p].npy>. np: Data\\batch\\b_n1.
        """
        self.name = name
        """Scieżka do serii, nie uwzględniajac <[p].npy>. np: Data\\batch\\b_n1."""
        self._type_batch: int | None = None
        """
        Informacja o typie serii.
            1 - wykonana predykcja cech\n
            2 - plik nie zawiera obrazów podobnych do siebie w swojej serii
            3 - plik nie zawiera obrazów podobnych w swojej serii i w archiwum"""
        if self.name is not None:
            self.batch_num= ""
            """Numer serii, nie zawiera informacji o typie serii."""
            for char in self.name:
                if char.isdigit():
                    self.batch_num += char
            self.open_batch()
            self.__what_batch()
        else:  
            self.batch_features = batch_features
            """Seria zawierająca cechy obrazów"""
            
            self.batch_info = batch_info
            """Seria zawierająca informacje o obrazach"""
            
        
    def reset(self):
        self.__dict__.clear()
    


    @property
    def type_batch(self) -> int:
        """
        Typ serii:
            0 - nowy plik
            1 - wykonana predykcja cech
            2 - plik nie zawiera obrazów podobnych do siebie w swojej serii
            3 - plik nie zawiera obrazów podobnych w swojej serii i w archiwum
        """
        if self._type_batch == None:
            if self.name == None:
                self._type_batch = 1
                return self._type_batch
            else:
                self._type_batch = Batch.type_batch_to_int_from_str(self.name)
        return self._type_batch
    
    @staticmethod
    def type_batch_to_int_from_str(name: str):
        """Zwraca typ serii w postaci int
        
        :param str name: Typ serii
        :return type_str: typ w postaci str"""
        type_batch = ''
        for char in name:
            if char.isdigit():
                break
            type_batch += char
        match type_batch:
            case s.FileName.batch_new:
                return 1
            case s.FileName.batch_self_tested:
                return 2
            case s.FileName.batch_archive:
                return 3
        return 0
    
    @staticmethod
    def type_batch_to_str(type: int):
        """Zwraca typ serii w postaci str
        
        :param int type: Typ serii
        :return type_str: typ w postaci str"""
        match type:
            case -1:
                type_str = 1
            case 1:
                type_str = s.FileName.batch_new
            case 2:
                type_str = s.FileName.batch_self_tested
            case 3:
                type_str = s.FileName.batch_archive
        return type_str
    
    @staticmethod
    def type_batch_to_path(type):
        """Zwraca typ serii w postaci ścieżki

        :param int type: Typ serii
        :return type_str: typ w postaci ścieżki"""
        match type:
            case -1:
                path_f = 1
            case 1:
                path_f = s.PathFile.batches_new
            case 2:
                path_f = s.PathFile.batches_self_tested
            case 3:
                path_f = s.PathFile.batches_archive
        return path_f
            

    def save_batch(self):
        """Tworzy nowe pliki serii i informacji o serii.
        Jeśli obiekt nie ma nazwy to, tworzy nowe pliki wyszukujac dostępną nazwę.
        """
        if self.name is None:
            self.name, self.batch_num = self.__find_available_filename()
            print(f"\r\033[32mZapisano plik: {self.name}\033[0m")
        
        self.update_batch_num()
        path_f = Batch.type_batch_to_path(self.type_batch)

        np.save(path_f+str(self.batch_num)+s.np_type, self.batch_features)
        np.save(path_f+str(self.batch_num)+s.path_id+s.np_type, self.batch_info)

    def update_batch_num(self):
        """Aktualizuje numer serii we wszystkich wierszach serii w obiekcie"""
        self.batch_info['batch'] = int(self.batch_num)
                    
    def update_check_num(self, list_sim, update= np.uint8(0)):
        """Aktualizuje typ serii we wszystkich wierszach serii w obiekcie.
        Jeśli numer obrazu nie znajduje się w liście, to jest ustawiany typ <update>.

        :param List[int] list_sim: Numery wszystkich duplikatów
        :param np.uint8() update: Numer typu serii, który będzie ustawiany"""

        if list_sim == []:
            self.batch_info['check'] =np.uint8(update)
        for row in self.batch_info:
            if int(row['no']) in list_sim:
                row['check'] =np.uint8(update)
        self.__what_batch()

                    

    
    def __find_available_filename(self, type_batch= -1, end_base_name=s.np_type):
        """Funkcja do znajdowania dostępnej nazwy pliku o określonym typie serii.
        
        :param int type_batch: Typ serii, domyślnie -1
        :param str end_base_name: Sufiks nazwy, domyślnie s.np_type
        :return file_path: Pełna ścieżka do pliku zawiera katalogi, nazwę wraz z numerem, nie zawiera rozszerzenia.
        :return batch_num: Numer serii
        """
        if type_batch == -1:
            type_batch = self.type_batch
        path_f = Batch.type_batch_to_path(type_batch)

        batch_num = 1
        while True:
            file_path = f"{path_f}{batch_num}"  # np. FOLDER//batch_1.npy, FOLDER//batch_2.npy, ...
            if not os.path.exists(file_path+end_base_name):
                return file_path, batch_num
            batch_num += 1

    def __what_batch(self):
        """Zwraca informację o tym pod jakim typem serii powinny być zapisane pliki"""
        row_type = 3
        for row in self.batch_info:
            # Ustawiany jest typ serii na najniższy występujący w wierszach
            if row_type > row['check']:
                row_type = row['check']


        if row_type != self.type_batch:
            # Należy zmienić nazwę pliku, ponieważ zawiera serię zakwalifikowaną do innego typu
            print(f'\033[32m Seria {self.name} została zakwalifikowana do: {row_type}\033[0m')
            self.__rename_file(row_type)
            self.update_global_path_file()

    def __rename_file(self, type_batch):
        """Zmienia ścieżkę i nazwę pliku obiektu.
        
        :param int type_batch: Typ serii nowego pliku
        """
        new_path, batch_num = self.__find_available_filename(type_batch=type_batch)
        self.batch_info['batch'] = np.uint8(batch_num)
        path_old = Batch.return_path_from_type(self.type_batch)

        os.rename(path_old+self.batch_num+s.np_type, new_path+s.np_type)
        np.save(new_path+s.path_id+s.np_type, self.batch_info)
        os.remove(path_old+self.batch_num+s.path_id+s.np_type)
        self.name = os.path.basename(new_path)
    
    @staticmethod
    def return_path_from_type(type_b: int):
        """Zwraca informacje o ścieżce do pliku na podstawie typu
        
        :param int type_b: Typ serii
        :return: Ścieżka do pliku, z nazwą zawierającą typ (str)
        """
        match type_b:
            case 1:
                return s.PathFile.batches_new
            case 2:
                return s.PathFile.batches_self_tested
            case 3:
                return s.PathFile.batches_archive
        return 0

    def update_global_path_file(self):
        """Aktualizuje informacje o serii w pliku zawierającym wszystkie ścieżki"""
        patch_good_npy = np.load(s.PathFile.p_good+s.np_type)
        for row in self.batch_info:
            existing_index = np.nonzero(patch_good_npy['path'] == row[0])[0]
            if len(existing_index) > 0:
                if not np.array_equal(patch_good_npy[existing_index], row):
                    patch_good_npy[existing_index] = row
        np.save(s.PathFile.p_good+s.np_type, patch_good_npy)
        print('\033[35mWykonano aktualizacje pliku ze ścieżkami\033[0m')

    @staticmethod
    def return_batch_number(name: str):
        """Zwraca numer serii z przesłanej nazwy
        
        :param str name: Ścieżka do pliku lub nazwa pliku
        :return batch_num: Numer serii, nie zawiera informacji o typie serii."""
        batch_num = ""
        for char in os.path.basename(name):
            if char.isdigit():
                batch_num += char
        return batch_num

    def _return_batch_number(self):
        """Zwraca numer serii z przesłanej nazwy
        
        :param str name: Ścieżka do pliku lub nazwa pliku"""
        batch_num = ""
        name: str = os.path.basename(self.name)
        for char in name:
            if char.isdigit():
                batch_num += char
        self.batch_num= batch_num

    @staticmethod
    def _return_list_id_batchs(listdir: list[str], name_batch):
        """Tworzy listę zawierającą wszystkie id serii danej serii
        
        :param list[str] listdir: Lista wszystkich plików
        :param str name_batch: Prefix nazwy pliku
        :return list_f: Lista wszystkich numerów serii danego typu"""
        list_f = []
        for f in listdir:
            if f.startswith(name_batch) and f.endswith(s.path_id+s.np_type):
                list_f.append(Batch.return_batch_number(os.path.basename(f)))
        return list_f

    @classproperty
    def list_batch(cls):
        """Lista id wszystkich plików zawierających serię [[lista n], [lista st], [lista a]]"""
        if cls._list_batch == None:
            cls._list_batch = [[], [], []]
            cls.list_batch_set(1)
            cls.list_batch_set(2)
            cls.list_batch_set(3)
        return  Batch._list_batch
    
    @classmethod
    def list_batch_set(cls, type_b= 0):
        """Aktualizuje listę wszystkich plików zawierających serię o typie argumentu.
        
        :param int type_b: Typ serii."""
        match type_b:
            case 3:
                cls._list_batch[2] = Batch._return_list_id_batchs(
                    os.listdir(os.path.dirname(s.PathFile.batches_archive)), s.FileName.batch_archive)
            case 2:
                cls._list_batch[1] = Batch._return_list_id_batchs(
                    os.listdir(os.path.dirname(s.PathFile.batches_self_tested)), s.FileName.batch_self_tested)
            case 1:
                cls._list_batch[0] = Batch._return_list_id_batchs(
                    os.listdir(os.path.dirname(s.PathFile.batches_new)), s.FileName.batch_new)

    def open_batch(self):
        """Metoda pozwalająca na odczytanie serii i informacji o serii z plików batch"""
        path_f = Batch.type_batch_to_path(self.type_batch)

        self.batch_features = np.load(path_f+self.batch_num+s.np_type)
        self.batch_info = np.load(path_f+self.batch_num+s.path_id+s.np_type)

    @staticmethod
    def convert_list_of_similary(list_of_similary):
        """Konwereruje informację o podobieństwach na postać listy numerów obrazów, które zawierają duplikaty
        
        :param [['b_st70', int(num) 'b_a94', int(num), sim], ...] list_of_similary: Zawiera listy, które mają numer obrazu
        i numery innych obrazów i ich podobieństwo do pierwszego
        :return list_s: Lista wszystkich obrazów, które zawierają duplikaty
        """
        list_s = []
        if list_of_similary == []:
            return []
        for i in list_of_similary:
            list_s.append(i[1])
        return list_s 
    
    @staticmethod
    def return_path_img(name_batch, number_img):
        """Zwraca pełną ściezkę do danego obrazu"""
        path = Batch.type_batch_to_path(Batch.type_batch_to_int_from_str(name_batch))
        batch_number = Batch.return_batch_number(name_batch)
        for row in np.load(path+batch_number+"p.npy"):
            if row['no'] == np.uint8(number_img):
                return row['path']