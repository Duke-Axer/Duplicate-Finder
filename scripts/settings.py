from enum import Enum
import os

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
    paths_good = 'P_G.npy'
    paths_new = 'P_n'
    paths_bad = 'P_B.npy'


class PathFile():
    """Zawiera ścieżki do plików lub katalogu, w którym powinny się znajdować"""
    batches_new = os.path.join(FolderName.data, FolderName.batchs)
    batches_self_tested = os.path.join(FolderName.data, FolderName.batchs)
    batches_archive = os.path.join(FolderName.data, FolderName.archives_batch)
    p_good = os.path.join(FolderName.data, FolderName.paths, FileName.paths_good)
    p_bad = os.path.join(FolderName.data, FolderName.paths, FileName.paths_bad)
    batches_tmp = os.path.join(FolderName.data, FolderName.tmp)
    config_p = os.path.join(FolderName.data, FileName.config)

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


