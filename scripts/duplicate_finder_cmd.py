import settings
import init
import archive
import similarity
import batch
import show
import os
import argparse

import numpy as np


def main():
    settings.Config._read_settings()
    init
    arg= cmd()
    if arg.add_new:
        add_new()
    if arg.make_new_batchs:
        make_new_batchs()
    if arg.compare:
        compare()
    #add_new()
    #make_new_batchs()
    #test()
    #compare()
    #test()

def make_new_batchs():
    """Tworzy nowe serie z nowych ścieżek"""
    catalog = archive.Archive()
    catalog.search_new_file()
    while True:
        batch_img = catalog.make_new_batch()
        if batch_img.size == 0:
            return
        batch_features, images_info= similarity.Similarity.images_to_vectors(batch_img)
        manage_files = batch.Batch(batch_features, images_info)
        manage_files.save_batch(images_info)
        catalog.save_list_files_to_npy(manage_files.batch_info)

def test():
    seria = np.load("Data\\batch\\b_n1p.npy")
    print(seria)

def compare():
    """Sprawdza, czy występują duplikaty. Aktualizuje informacje o serii"""
    catalog = archive.Archive()
    show_obj = show.Show()
    batch.Batch.create_list_batch()
    for file in batch.Batch.list_batch[0]:
        batch_1 = batch.Batch(name=file) #tworzenie obiektu
        sim = similarity.Similarity(batch_features= batch_1.batch_features)
        sim.create_matrix()
        list_of_similary= sim.compare()
        print(f"{file}: {list_of_similary}")
        for i in list_of_similary:
            print([os.path.basename(file), os.path.basename(file)] + i)
            show_obj.add_duplicates([file, file] + i)
        print(batch.Batch.convert_list_of_similary(list_of_similary))
        batch_1.update_check_num(batch.Batch.convert_list_of_similary(list_of_similary), np.uint8(2))
        batch_1.save_batch(batch_info=batch_1.batch_info)
    print('wykonywanie testu a')
    for file in batch.Batch.list_batch[1]:
        
        batch_1 = batch.Batch(name=file) #tworzenie obiektu
        all_list_of_similary= []
        for file_a in batch.Batch.list_batch[2]:
            batch_2 = batch.Batch(name=file_a)
            sim = similarity.Similarity(batch_features= batch_1.batch_features, )
            sim.create_matrix(batch_2.batch_features)
            list_of_similary= sim.compare()
            for i in list_of_similary:
                
                print([os.path.basename(file), os.path.basename(file_a)] + i)
                show_obj.add_duplicates([file, file] + i)
            for i in list_of_similary:
                all_list_of_similary.append(i)
        print(f"{file}: {all_list_of_similary}")
        print(batch.Batch.convert_list_of_similary(all_list_of_similary))
        print(batch_1.batch_info)
        batch_1.update_check_num(batch.Batch.convert_list_of_similary(all_list_of_similary), np.uint8(3))
        print(batch_1.batch_info)
        batch_1.save_batch(batch_info=batch_1.batch_info)
    print("wynik")
    print(show_obj.input_info)
    show_obj.loop__all_dup()

def add_new():
    """Wyszukuje i dodaje nowe ścieżki do listy ścieżek"""
    catalog = archive.Archive()
    catalog.search_new_file()

def cmd():
    parser = argparse.ArgumentParser(description="Przykład użycia argparse")
    parser.add_argument("-an", "--add_new", action='store_true', help="dodaje do listy znalezione nowe obrazy")
    parser.add_argument("-mnb" ,"--make_new_batchs", action='store_true', help="Tworzy nowe serie z nowych ścieżek")
    parser.add_argument("-c" ,"--compare", action='store_true', help="Sprawdza, czy występują duplikaty. Aktualizuje informacje o serii")
    return parser.parse_args()

main()