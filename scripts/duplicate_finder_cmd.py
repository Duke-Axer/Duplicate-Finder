import scripts.settings as s
from scripts import init, archive, similarity
from scripts.batch import Batch
from scripts.show import Show
import argparse
import numpy as np


def main():
    s.Config._read_settings()
    init
    arg= cmd()
    if arg.add_new:
        add_new()
    if arg.make_new_batchs:
        make_new_batchs()
    if arg.compare:
        compare()
    if arg.info:
        info()

def make_new_batchs():
    """Tworzy nowe serie z nowych ścieżek"""
    catalog = archive.Archive()
    while True:
        batch_img = catalog.make_new_batch()
        if batch_img.size == 0:
            break
        batch_features, images_info= similarity.Similarity.images_to_vectors(batch_img)
        manage_files = Batch(batch_features, images_info)
        manage_files.save_batch()
        catalog.save_list_files_to_npy_new(manage_files.batch_info)
    print('\r\033[33mZakończono tworzenie nowych serii\033[0m')


def __save_list_of_similary(show_obj: Show, list_of_similary: list):
    """Funkcja zajmuje się obsługą obiektu Show
    
    :param Show show_obj: Obiekt klasy Show.
    :param list list_of_similary: Lista w postaci: [['b_n1', int(num_1) 'b_n2', int(num_2), sim], ...]
    """
    if not list_of_similary:
        return
    print('\r\033[91mSeria zawiera obrazy do siebie podobne:\033[0m')
    for i in list_of_similary:
        print('\r\033[91m{}: {} {}: {} podobieństwo: {}\033[0m'.format(i[0],i[1],i[2],i[3],float(i[4])))
        show_obj.add_duplicates(i)

def compare():
    """Sprawdza, czy występują duplikaty. Aktualizuje informacje o serii"""
    show_obj = Show()
    print("\r\033[33m   Sprawdzanie plików N\033[0m")
    for file in Batch.list_batch[0]:
        batch_1 = Batch(name=s.FileName.batch_new+file)
        print(f"\r\033[33mSprawdzanie pliku {batch_1.name} N\033[0m")
        sim = similarity.Similarity(batch_1)
        list_of_similary= sim.create_matrix()
        __save_list_of_similary(show_obj, list_of_similary)
        batch_1.update_check_num(Batch.convert_list_of_similary(list_of_similary), np.uint8(2))
        
    print("\r\033[33m   Sprawdzanie plików ST\033[0m")
    Batch.list_batch_set(2)
    for file in Batch.list_batch[1]:
        batch_1 = Batch(name=s.FileName.batch_self_tested+file) #tworzenie obiektu
        print(f"\r\033[33mSprawdzanie pliku {batch_1.name} ST\033[0m")
        all_list_of_similary= []

        Batch.list_batch_set(3)
        for file_a in Batch.list_batch[2]:
            batch_2 = Batch(name=s.FileName.batch_archive+file_a)
            sim = similarity.Similarity(batch_1)
            list_of_similary= sim.create_matrix(batch_2)
            __save_list_of_similary(show_obj, list_of_similary)
            all_list_of_similary.extend(list_of_similary)
        batch_1.update_check_num(Batch.convert_list_of_similary(all_list_of_similary), np.uint8(3))
    show_obj.loop_all_dup()

def add_new():
    """Wyszukuje i dodaje nowe ścieżki do listy ścieżek"""
    catalog = archive.Archive()
    catalog.search_new_file()
    print('\r\033[33mZakończono dodawanie ścieżek\033[0m')

def info():
    """Informacje o programie"""
    print('Nazwa Programu: Duplicate Finder\nAutor: Brajan Gąbka\nE-mail: b.gabka.nkn@gmail.com\nWersja: 1.0')

def cmd():
    parser = argparse.ArgumentParser(description="Przykład użycia argparse")
    parser.add_argument("-an", "--add_new", action='store_true', help="dodaje do listy znalezione nowe obrazy")
    parser.add_argument("-mnb" ,"--make_new_batchs", action='store_true', help="Tworzy nowe serie z nowych ścieżek")
    parser.add_argument("-c" ,"--compare", action='store_true', help="Sprawdza, czy występują duplikaty. Aktualizuje informacje o serii")
    parser.add_argument("-i" ,"--info", action='store_true', help="Wyświetla informacje o programie")
    return parser.parse_args()

main()