from enum import Enum
import os
import numpy as np

dtype_good=np.dtype([('path', 'U256'), ('check', np.uint8), ('batch', np.uint8), ('no', np.uint8)])
"""Typ danych przechwywanych w tablicy poprawnych ścieżek
check: 
    0 - nowy plik 
    1 - wykonana predykcja cech
    2 - plik nie zawiera obrazów podobnych do siebie w swojej serii
    3 - plik nie zawiera obrazów podobnych w swojej serii i w archiwum
batch - nazwa pliku serii (numer)
no    - numer w pliku serii
"""
dtype_bad=np.dtype([('path', 'U256')])
"""Typ danych przechwywanych w tablicy pomijanych ścieżek"""

class FolderName():
    """Zawiera wszystkie katalogi, które są wykorzystywane w programie"""
    data = "Data" # Wszystkie dane znajdują się w tym pliku
    paths = 'paths'
    batchs = 'batch'
    tmp = 'tmp'
    archives_batch = 'batch_archives'
    duplicates = 'Duplicates'

class FileName():
    """Zawiera wszystkie nazwy plików, które są wykorzystywane w programie"""
    config = 'settings.txt' # Plik z ustawieniami użytkownika
    batch_tmp = 'b_t'
    batch_new = 'b_n' # Nowe batch pliki, nie są sprawdzone, czy w nich są duplikaty
    batch_self_tested = 'b_st' # Zostały sprawdzone i nie mają w sobie duplikatów względem siebie
    batch_archive = 'b_a' # Pliki batch, które nie mają duplikatów względewm archiwum i siebie
    paths_good = 'P_G'
    paths_new = 'P_n'
    paths_bad = 'P_B'


class PathFile():
    """Zawiera ścieżki do plików lub katalogu, w którym powinny się znajdować"""
    batches_new = os.path.join(FolderName.data, FolderName.batchs, FileName.batch_new)
    batches_self_tested = os.path.join(FolderName.data, FolderName.batchs, FileName.batch_self_tested)
    batches_archive = os.path.join(FolderName.data, FolderName.archives_batch, FileName.batch_archive)
    p_good = os.path.join(FolderName.data, FolderName.paths, FileName.paths_good)
    p_bad = os.path.join(FolderName.data, FolderName.paths, FileName.paths_bad)
    batches_tmp = os.path.join(FolderName.data, FolderName.tmp)
    config_p = os.path.join(FolderName.data, FileName.config)
    duplicates = os.path.join(FolderName.data, FolderName.duplicates)

class Config():
    """Odczytuje i zawiera ustawienia użytkownika"""
    path: str
    """Ścieżka do katalogu z grafiką"""
    similarity: float
    """Wartość podobieństwa, przy której grafiki są uznawana za identyczne. przyjmuje przedział <0,1>"""

    @staticmethod
    def _read_settings():
        """Odczytuje ustawienia programu"""
        with open(PathFile.config_p, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith("path"):
                    _tmp = line.split(":", 1)
                    Config.path = str(_tmp[1].strip())
                elif line.startswith("similarity"):
                    _tmp = line.split(":", 1)
                    Config.similarity = float(_tmp[1].strip())


